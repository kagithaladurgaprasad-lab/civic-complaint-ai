import os

# Reduce CPU thread memory usage on Render
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch

torch.set_num_threads(1)
torch.set_num_interop_threads(1)

from qdrant_client.models import PointStruct

from image_embeddings import create_image_embedding

from vector_db import (
    client,
    TEXT_COLLECTION,
    IMAGE_COLLECTION
)


# ---------------------------------------------------------
# Shared text embedding model
# ---------------------------------------------------------

text_embedding_model = None


class MiniLMTextModel:

    def __init__(self):

        from transformers import (
            AutoTokenizer,
            AutoModel
        )

        model_name = "sentence-transformers/all-MiniLM-L6-v2"

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        # Load transformer model
        self.model = AutoModel.from_pretrained(
            model_name
        )

        # Inference mode
        self.model.eval()

        # Disable gradients
        for parameter in self.model.parameters():
            parameter.requires_grad = False


    def encode(
        self,
        text,
        normalize_embeddings=True
    ):

        # Tokenize text
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True
        )

        # Inference only
        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        # Token embeddings
        token_embeddings = outputs.last_hidden_state

        # Attention mask
        attention_mask = inputs["attention_mask"]

        # Expand mask
        mask = (
            attention_mask
            .unsqueeze(-1)
            .expand(token_embeddings.size())
            .float()
        )

        # Mean pooling
        summed = torch.sum(
            token_embeddings * mask,
            dim=1
        )

        counts = torch.clamp(
            mask.sum(dim=1),
            min=1e-9
        )

        sentence_embedding = (
            summed / counts
        )

        # Normalize embedding
        if normalize_embeddings:

            sentence_embedding = (
                torch.nn.functional.normalize(
                    sentence_embedding,
                    p=2,
                    dim=1
                )
            )

        # Convert to Python list
        return sentence_embedding[0].cpu().numpy()


# ---------------------------------------------------------
# Get shared text model
# ---------------------------------------------------------

def get_text_model():

    global text_embedding_model

    if text_embedding_model is None:

        text_embedding_model = MiniLMTextModel()

    return text_embedding_model


# ---------------------------------------------------------
# Create text embedding
# ---------------------------------------------------------

def create_text_embedding(text):

    model = get_text_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


# ---------------------------------------------------------
# Create image embedding
# ---------------------------------------------------------

def create_image_embedding_from_file(
    image_path
):

    return create_image_embedding(
        image_path
    )


# ---------------------------------------------------------
# Store text complaint in Qdrant
# ---------------------------------------------------------

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

    # Combine title and description
    text = f"{title}. {description}"

    # Create 384-dimensional embedding
    embedding = create_text_embedding(
        text
    )

    # Create Qdrant point
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

    # Store in Qdrant
    client.upsert(

        collection_name=TEXT_COLLECTION,

        points=[
            point
        ]
    )


# ---------------------------------------------------------
# Store image complaint in Qdrant
# ---------------------------------------------------------

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

    # Create 512-dimensional CLIP embedding
    embedding = create_image_embedding_from_file(
        image_path
    )

    # Create Qdrant point
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

    # Store in Qdrant
    client.upsert(

        collection_name=IMAGE_COLLECTION,

        points=[
            point
        ]
    )