import os
from typing import List, Sequence, Tuple, Optional

import numpy as np
import psycopg2
from psycopg2.extensions import connection as PGConnection


def get_db_connection() -> PGConnection:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    dbname = os.getenv("POSTGRES_DB", "vectordb")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    return conn


def _get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    from openai import OpenAI

    return OpenAI(api_key=api_key)


EMBEDDING_DIM = 1536


def get_embedding_for_text(text: str) -> List[float]:
    """
    Retourne un embedding pour un texte.

    - Si OPENAI_API_KEY est défini, utilise l'API OpenAI (text-embedding-3-small).
    - Sinon, génère un embedding pseudo-aléatoire déterministe basé sur le texte.
    """
    client = _get_openai_client()
    if client is not None:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    # Fallback : embedding déterministe basé sur le hash du texte
    seed = abs(hash(text)) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.random(EMBEDDING_DIM, dtype=np.float32)
    return vec.tolist()


def to_pgvector(values: Sequence[float]) -> str:
    """
    Convertit une séquence de floats en littéral texte pour le type vector de pgvector.
    Exemple : [0.1, 0.2] -> "[0.1,0.2]".
    """
    return "[" + ",".join(f"{float(v):.6f}" for v in values) + "]"


def insert_document(conn: PGConnection, content: str, embedding: Sequence[float]) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (content, embedding)
            VALUES (%s, %s::vector)
            RETURNING id
            """,
            (content, to_pgvector(embedding)),
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    return new_id


def search_most_similar(
    conn: PGConnection, embedding: Sequence[float]
) -> Optional[Tuple[int, str, float]]:
    """
    Retourne (id, content, distance) du document le plus proche selon la distance euclidienne (<->).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, content, embedding <-> %s::vector AS distance
            FROM documents
            ORDER BY embedding <-> %s::vector
            LIMIT 1
            """,
            (to_pgvector(embedding), to_pgvector(embedding)),
        )
        row = cur.fetchone()
        if not row:
            return None
        return int(row[0]), str(row[1]), float(row[2])

