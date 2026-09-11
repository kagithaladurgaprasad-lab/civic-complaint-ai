
from qdrant_client.models import PointStruct

from image_embeddings import create_image_embedding

from vector_db import (
    client,
    TEXT_COLLECTION,
    IMAGE_COLLECTION
)


text_model = None


def get_text_model():

    global text_model

    if text_model is None:

        # Import only when the model is actually needed.
        # This prevents sentence-transformers from consuming
        # large amounts of RAM during application startup.
        from sentence_transformers import SentenceTransformer

        text_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return text_model


def create_text_embedding(text):

    model = get_text_model()

    embedding = model.encode(text)

    return embedding.tolist()


def create_image_embedding_from_file(image_path):

    return create_image_embedding(image_path)


def store_text_complaint(
    complaint_id,
    title,
    description,
    category,
    department,
    urgency,
    latitude,
    longitude
):

    text = f"{title}. {description}"

    embedding = create_text_embedding(text)

    point = PointStruct(
        id=complaint_id,
        vector=embedding,
        payload={
            "complaint_id": complaint_id,
            "title": title,
            "description": description,
            "category": category,
            "department": department,
            "urgency": urgency,
            "latitude": latitude,
            "longitude": longitude
        }
    )

    client.upsert(
        collection_name=TEXT_COLLECTION,
        points=[point]
    )


def store_image_complaint(
    complaint_id,
    image_path,
    title,
    description,
    category,
    department,
    urgency,
    latitude,
    longitude
):

    embedding = create_image_embedding_from_file(
        image_path
    )

    point = PointStruct(
        id=complaint_id,
        vector=embedding,
        payload={
            "complaint_id": complaint_id,
            "title": title,
            "description": description,
            "category": category,
            "department": department,
            "urgency": urgency,
            "latitude": latitude,
            "longitude": longitude,
            "image_path": image_path
        }
    )

    client.upsert(
        collection_name=IMAGE_COLLECTION,
        points=[point]
    )

