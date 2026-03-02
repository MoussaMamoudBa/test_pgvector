import os

from app.vector_utils import (
    get_db_connection,
    get_embedding_for_text,
    insert_document,
    search_most_similar,
)


def main() -> None:
    print("Connexion à PostgreSQL...")
    conn = get_db_connection()

    docs = [
        "FastAPI est un framework web moderne pour Python.",
        "PostgreSQL est une base de données relationnelle puissante.",
        "pgvector permet de stocker et rechercher des embeddings.",
        "Les embeddings de texte servent pour la similarité sémantique.",
        "Docker Compose permet d'orchestrer plusieurs services.",
    ]

    print("Insertion de documents avec embeddings...")
    for content in docs:
        emb = get_embedding_for_text(content)
        doc_id = insert_document(conn, content, emb)
        print(f"- inséré id={doc_id} : {content!r}")

    example_query = os.getenv(
        "DEMO_QUERY", "Quelle technologie pour faire de la recherche vectorielle ?"
    )
    print(f"\nRecherche du document le plus proche pour : {example_query!r}")
    query_emb = get_embedding_for_text(example_query)

    result = search_most_similar(conn, query_emb)
    conn.close()

    if result is None:
        print("Aucun document trouvé (table vide ?).")
        return

    doc_id, content, distance = result
    print("\n=== Résultat ===")
    print(f"id       : {doc_id}")
    print(f"content  : {content}")
    print(f"distance : {distance}")


if __name__ == "__main__":
    main()

