from image_embeddings import create_image_embedding

from vector_db import (
    client,
    IMAGE_COLLECTION
)


def search_similar_images(
    image_path,
    top_k=5
):

    query_embedding = create_image_embedding(
        image_path
    )


    results = client.query_points(

        collection_name=IMAGE_COLLECTION,

        query=query_embedding,

        limit=top_k,

        with_payload=True
    ).points


    return results