
from sentence_transformers import SentenceTransformer

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

from vector_db import client, TEXT_COLLECTION


# ============================================================
# LAZY-LOADED TEXT EMBEDDING MODEL
# ============================================================

model = None


def get_model():

    global model

    if model is None:

        model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return model


# ============================================================
# SEARCH HISTORICAL COMPLAINTS
# ============================================================

def search_complaints(
    query,
    category=None,
    top_k=5
):

    # Load model only when search is actually required
    embedding_model = get_model()

    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()


    complaint_filter = None


    if category:

        complaint_filter = Filter(

            must=[

                FieldCondition(

                    key="category",

                    match=MatchValue(
                        value=category
                    )
                )
            ]
        )


    results = client.query_points(

        collection_name=TEXT_COLLECTION,

        query=query_embedding,

        query_filter=complaint_filter,

        limit=top_k,

        with_payload=True

    ).points


    return results
