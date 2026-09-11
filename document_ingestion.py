import os

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from vector_db import client
from vector_db import (
    client,
    DOCUMENT_COLLECTION
)


# -----------------------------
# Configuration
# -----------------------------

DOCUMENT_DIR = "municipal_documents"

DOCUMENT_COLLECTION = "municipal_documents"

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# Read PDF
# -----------------------------

def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

    return text


# -----------------------------
# Create chunks
# -----------------------------

def create_chunks(
    text,
    chunk_size=500
):

    words = text.split()

    chunks = []

    for i in range(
        0,
        len(words),
        chunk_size
    ):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

    return chunks


# -----------------------------
# Store document
# -----------------------------

def ingest_document(file_path):

    text = read_pdf(file_path)

    chunks = create_chunks(text)

    points = []

    for index, chunk in enumerate(chunks):

        embedding = model.encode(
            chunk
        ).tolist()

        point = PointStruct(

            id=abs(
                hash(
                    f"{file_path}_{index}"
                )
            ),

            vector=embedding,

            payload={

                "source": os.path.basename(
                    file_path
                ),

                "chunk_id": index,

                "text": chunk
            }
        )

        points.append(point)


    client.upsert(

        collection_name=DOCUMENT_COLLECTION,

        points=points
    )


# -----------------------------
# Ingest all documents
# -----------------------------

def ingest_all_documents():

    for filename in os.listdir(
        DOCUMENT_DIR
    ):

        if filename.lower().endswith(
            ".pdf"
        ):

            file_path = os.path.join(
                DOCUMENT_DIR,
                filename
            )

            ingest_document(
                file_path
            )