from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)


# -----------------------------
# Qdrant local database
# -----------------------------

client = QdrantClient(
    path="qdrant_data"
)


# -----------------------------
# Collection names
# -----------------------------

TEXT_COLLECTION = "historical_complaints"

IMAGE_COLLECTION = "image_complaints"

DOCUMENT_COLLECTION = "municipal_documents"

# -----------------------------
# Create text collection
# -----------------------------

def create_text_collection():

    collections = client.get_collections().collections

    existing_names = [
        collection.name
        for collection in collections
    ]

    if TEXT_COLLECTION not in existing_names:

        client.create_collection(

            collection_name=TEXT_COLLECTION,

            vectors_config=VectorParams(

                size=384,

                distance=Distance.COSINE
            )
        )


# -----------------------------
# Create image collection
# -----------------------------

def create_image_collection():

    collections = client.get_collections().collections

    existing_names = [
        collection.name
        for collection in collections
    ]

    if IMAGE_COLLECTION not in existing_names:

        client.create_collection(

            collection_name=IMAGE_COLLECTION,

            vectors_config=VectorParams(

                size=512,

                distance=Distance.COSINE
            )
        )
def create_document_collection():

    collections = client.get_collections().collections

    existing_names = [
        collection.name
        for collection in collections
    ]

    if DOCUMENT_COLLECTION not in existing_names:

        client.create_collection(

            collection_name=DOCUMENT_COLLECTION,

            vectors_config=VectorParams(

                size=384,

                distance=Distance.COSINE
            )
        )
create_text_collection()

create_image_collection()

create_document_collection()