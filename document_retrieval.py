
from complaint_embeddings import get_text_model

from vector_db import (
    client,
    DOCUMENT_COLLECTION
)


def retrieve_documents(
    query,
    top_k=5
):

    # Use the shared SentenceTransformer model
    embedding_model = get_text_model()

    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = client.query_points(
        collection_name=DOCUMENT_COLLECTION,
        query=query_embedding,
        limit=top_k,
        with_payload=True
    ).points

    documents = []

    for index, result in enumerate(
        results,
        start=1
    ):

        payload = result.payload or {}

        document = {

            "source_id": payload.get(
                "document_id",
                payload.get(
                    "source_id",
                    f"DOC-{index}"
                )
            ),

            "title": payload.get(
                "title",
                payload.get(
                    "document_title",
                    "Unknown Document"
                )
            ),

            "source": payload.get(
                "source",
                "Unknown Source"
            ),

            "text": payload.get(
                "text",
                payload.get(
                    "content",
                    ""
                )
            ),

            "document_type": payload.get(
                "document_type"
            ),

            "department": payload.get(
                "department"
            ),

            "category": payload.get(
                "category"
            ),

            "sub_category": payload.get(
                "sub_category"
            ),

            "sla_days": payload.get(
                "sla_days"
            ),

            "effective_date": payload.get(
                "effective_date"
            ),

            "updated_at": payload.get(
                "updated_at"
            ),

            "similarity_score": result.score
        }

        documents.append(
            document
        )

    return documents

