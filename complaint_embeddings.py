
import os

# ============================================================
# RENDER CPU / MEMORY SETTINGS
# ============================================================

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import gc

import torch

torch.set_num_threads(1)
torch.set_num_interop_threads(1)

from qdrant_client.models import PointStruct

from image_embeddings import create_image_embedding

from vector_db import (
    client,
    TEXT_COLLECTION,
    IMAGE_COLLECTION,
)


# ============================================================
# SHARED TEXT EMBEDDING MODEL
# ============================================================

text_embedding_model = None


class MiniLMTextModel:

    def __init__(self):

        from sentence_transformers import SentenceTransformer

        model_name = "sentence-transformers/all-MiniLM-L6-v2"

        self.model = SentenceTransformer(
            model_name,
            device="cpu",
        )

        self.model.eval()


    def encode(
        self,
        text,
        normalize_embeddings=True,
    ):

        embedding = self.model.encode(
            text,
            normalize_embeddings=normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embedding


# ============================================================
# GET SHARED TEXT MODEL
# ============================================================

def get_text_model():

    global text_embedding_model

    if text_embedding_model is None:

        text_embedding_model = MiniLMTextModel()

    return text_embedding_model


# ============================================================
# CREATE TEXT EMBEDDING
# ============================================================

def create_text_embedding(text):

    model = get_text_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


# ============================================================
# CREATE IMAGE EMBEDDING
# ============================================================

def create_image_embedding_from_file(
    image_path,
):

    return create_image_embedding(
        image_path,
    )


# ============================================================
# STORE TEXT COMPLAINT IN QDRANT
# ============================================================

def store_text_complaint(
    complaint_id,
    title,
    description,
    category,
    department,
    urgency,
    latitude,
    longitude,
):

    text = f"{title}. {description}"

    embedding = create_text_embedding(
        text,
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
        },
    )

    client.upsert(
        collection_name=TEXT_COLLECTION,
        points=[
            point,
        ],
    )

    # Release temporary objects
    gc.collect()


# ============================================================
# STORE IMAGE COMPLAINT IN QDRANT
# ============================================================

def store_image_complaint(
    complaint_id,
    image_path,
    title,
    description,
    category,
    department,
    urgency,
    latitude,
    longitude,
):

    embedding = create_image_embedding_from_file(
        image_path,
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
            "image_path": image_path,
        },
    )

    client.upsert(
        collection_name=IMAGE_COLLECTION,
        points=[
            point,
        ],
    )

    gc.collect()

