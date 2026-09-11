import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


if not QDRANT_URL:
    raise ValueError(
        "QDRANT_URL is not set. "
        "Please add it to your .env file."
    )

if not QDRANT_API_KEY:
    raise ValueError(
        "QDRANT_API_KEY is not set. "
        "Please add it to your .env file."
    )


# ==========================================
# Qdrant Cloud
# ==========================================

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


# ==========================================
# Collection names
# ==========================================

TEXT_COLLECTION = "historical_complaints"

IMAGE_COLLECTION = "image_complaints"

DOCUMENT_COLLECTION = "municipal_documents"


# ==========================================
# Create text collection
# ==========================================

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


# ==========================================
# Create image collection
# ==========================================

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


# ==========================================
# Create document collection
# ==========================================

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


# ==========================================
# Create collections
# ==========================================

create_text_collection()

create_image_collection()

create_document_collection()