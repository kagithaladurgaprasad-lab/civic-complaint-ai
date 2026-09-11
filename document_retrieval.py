from sentence_transformers import SentenceTransformer

from vector_db import (
    client,
    DOCUMENT_COLLECTION
)


# ============================================================
# TEXT EMBEDDING MODEL
# ============================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# RETRIEVE MUNICIPAL DOCUMENTS
# ============================================================

def retrieve_documents(
    query,
    top_k=5
):

    # --------------------------------------------------------
    # Create query embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        query
    ).tolist()


    # --------------------------------------------------------
    # Search Qdrant
    # --------------------------------------------------------

    results = client.query_points(

        collection_name=DOCUMENT_COLLECTION,

        query=query_embedding,

        limit=top_k,

        with_payload=True
    ).points


    # --------------------------------------------------------
    # Normalize document metadata
    # --------------------------------------------------------

    documents = []

    for index, result in enumerate(results, start=1):

        payload = result.payload or {}

        document = {

            # Stable source ID
            "source_id": payload.get(
                "document_id",
                payload.get(
                    "source_id",
                    f"DOC-{index}"
                )
            ),

            # Document title
            "title": payload.get(
                "title",
                payload.get(
                    "document_title",
                    "Unknown Document"
                )
            ),

            # Source organization / URL / file
            "source": payload.get(
                "source",
                "Unknown Source"
            ),

            # Actual document content
            "text": payload.get(
                "text",
                payload.get(
                    "content",
                    ""
                )
            ),

            # ------------------------------------------------
            # SLA METADATA
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Optional date information
            # ------------------------------------------------

            "effective_date": payload.get(
                "effective_date"
            ),

            "updated_at": payload.get(
                "updated_at"
            ),

            # ------------------------------------------------
            # Qdrant similarity score
            # ------------------------------------------------

            "similarity_score": result.score
        }

        documents.append(document)


    return documents