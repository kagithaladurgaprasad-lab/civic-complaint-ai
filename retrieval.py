from complaint_embeddings import create_text_embedding
from search_complaints import search_complaints


def retrieve_similar_complaints(
    title,
    description,
    category=None,
    top_k=5
):

    text = f"{title}. {description}"

    results = search_complaints(

        query=text,

        category=category,

        top_k=top_k
    )

    return results
from vector_db import (
    client,
    TEXT_COLLECTION
)

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)


def retrieve_similar_complaints(

    title,

    description,

    category=None,

    top_k=5
):

    # -----------------------------
    # Create query text
    # -----------------------------

    text = f"{title}. {description}"


    # -----------------------------
    # Create embedding
    # -----------------------------

    query_embedding = create_text_embedding(
        text
    )


    # -----------------------------
    # Create category filter
    # -----------------------------

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


    # -----------------------------
    # Search Qdrant
    # -----------------------------

    results = client.query_points(

        collection_name=TEXT_COLLECTION,

        query=query_embedding,

        query_filter=complaint_filter,

        limit=top_k,

        with_payload=True
    ).points


    return results