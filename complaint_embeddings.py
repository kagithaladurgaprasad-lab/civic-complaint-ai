
import os
import gc

# Keep CPU usage low on Render
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from qdrant_client.models import PointStruct

from image_embeddings import create_image_embedding
from vector_db import client, TEXT_COLLECTION, IMAGE_COLLECTION


# ============================================================
# FAST EMBED TEXT MODEL
# ============================================================

text_embedding_model = None


class MiniLMTextModel:
    """
    Lightweight text embedding wrapper using FastEmbed.

    Model:
        sentence-transformers/all-MiniLM-L6-v2

    Output:
        384-dimensional normalized embedding
    """

    def __init__(self):
        from fastembed import TextEmbedding

        self.model = TextEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def encode(self, text, normalize_embeddings=True):
        embeddings = list(
            self.model.embed([text])
        )

        embedding = embeddings[0]

        return embedding


def get_text_model():
    """
    Load the text embedding model only when required.
    """

    global text_embedding_model

    if text_embedding_model is None:
        print("[TEXT EMBEDDING] Loading FastEmbed MiniLM model...")
        text_embedding_model = MiniLMTextModel()
        print("[TEXT EMBEDDING] FastEmbed model loaded.")

    return text_embedding_model


def create_text_embedding(text):
    """
    Create a 384-dimensional MiniLM embedding.
    """

    model = get_text_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


# ============================================================
# IMAGE EMBEDDING
# ============================================================

def create_image_embedding_from_file(image_path):
    return create_image_embedding(image_path)


# ============================================================
# STORE TEXT COMPLAINT
# ============================================================

def store_text_complaint(
    complaint_id,
    title,
    description,
    category,
    department,
    latitude,
    longitude
):
    """
    Create and store text embedding in Qdrant.
    """

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
            "latitude": latitude,
            "longitude": longitude
        }
    )

    client.upsert(
        collection_name=TEXT_COLLECTION,
        points=[point]
    )

    gc.collect()


# ============================================================
# STORE IMAGE COMPLAINT
# ============================================================

def store_image_complaint(
    complaint_id,
    image_path,
    category,
    department,
    latitude,
    longitude
):
    """
    Create and store image embedding in Qdrant.
    """

    embedding = create_image_embedding_from_file(image_path)

    point = PointStruct(
        id=complaint_id,
        vector=embedding,
        payload={
            "complaint_id": complaint_id,
            "image_id": complaint_id,
            "image_path": image_path,
            "category": category,
            "department": department,
            "latitude": latitude,
            "longitude": longitude
        }
    )

    client.upsert(
        collection_name=IMAGE_COLLECTION,
        points=[point]
    )

    gc.collect()

