
import os
import re
import hashlib
import requests

from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from vector_db import (
    client,
    DOCUMENT_COLLECTION
)


# ============================================================
# CONFIGURATION
# ============================================================

DOCUMENT_FOLDER = "official_documents"

URLS = [
    {
        "url": "https://cdma.ap.gov.in/services/grievances/",
        "document_id": "CDMA-GRIEVANCES",
        "title": "CDMA Grievance Redressal",
    },
    {
        "url": "https://cdma.ap.gov.in/resources/grievance-sla/",
        "document_id": "CDMA-GRIEVANCE-SLA",
        "title": "CDMA Grievance Service Level Agreements",
    },
    {
        "url": "https://cdma.ap.gov.in/resources/citizen-charter/",
        "document_id": "CDMA-CITIZEN-CHARTER",
        "title": "CDMA Citizen Charter",
    }
]


# ============================================================
# CREATE FOLDER
# ============================================================

os.makedirs(
    DOCUMENT_FOLDER,
    exist_ok=True
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# DOWNLOAD WEBPAGE
# ============================================================

def download_page(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# EXTRACT MAIN TEXT
# ============================================================

def extract_text(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Remove unnecessary webpage elements
    for element in soup([
        "script",
        "style",
        "noscript",
        "header",
        "footer",
        "nav"
    ]):
        element.decompose()

    text = soup.get_text(
        separator="\n"
    )

    # Clean excessive whitespace
    lines = []

    for line in text.splitlines():

        line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


# ============================================================
# CHUNK TEXT
# ============================================================

def create_chunks(
    text,
    chunk_size=1000,
    overlap=150
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


# ============================================================
# CREATE STABLE POINT ID
# ============================================================

def create_point_id(
    document_id,
    chunk_index
):

    value = (
        f"{document_id}-"
        f"{chunk_index}"
    )

    hash_value = hashlib.md5(
        value.encode()
    ).hexdigest()

    # Qdrant integer point ID
    return int(
        hash_value[:15],
        16
    )


# ============================================================
# PROCESS DOCUMENT
# ============================================================

def process_document(
    document
):

    print("\n" + "=" * 70)

    print(
        f"Downloading: {document['title']}"
    )

    print(
        f"URL: {document['url']}"
    )

    html = download_page(
        document["url"]
    )

    text = extract_text(
        html
    )

    print(
        f"Extracted characters: {len(text)}"
    )

    if len(text) < 100:

        print(
            "WARNING: Very little text extracted."
        )

        return []


    # --------------------------------------------------------
    # Save raw extracted text
    # --------------------------------------------------------

    safe_name = (
        document["document_id"]
        .lower()
        .replace(
            "-",
            "_"
        )
    )

    text_file = os.path.join(
        DOCUMENT_FOLDER,
        f"{safe_name}.txt"
    )

    with open(
        text_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(text)


    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    chunks = create_chunks(
        text
    )

    print(
        f"Created chunks: {len(chunks)}"
    )


    # --------------------------------------------------------
    # Create embeddings
    # --------------------------------------------------------

    embeddings = model.encode(
        chunks,
        show_progress_bar=True
    )


    # --------------------------------------------------------
    # Create Qdrant points
    # --------------------------------------------------------

    points = []

    for index, (
        chunk,
        embedding
    ) in enumerate(
        zip(
            chunks,
            embeddings
        )
    ):

        point_id = create_point_id(
            document["document_id"],
            index
        )

        point = PointStruct(

            id=point_id,

            vector=embedding.tolist(),

            payload={

                "document_id":
                    document["document_id"],

                "title":
                    document["title"],

                "source":
                    document["url"],

                "text":
                    chunk,

                "chunk_index":
                    index,

                "total_chunks":
                    len(chunks),

                "source_type":
                    "official_cdma_webpage"
            }
        )

        points.append(
            point
        )


    return points


# ============================================================
# MAIN
# ============================================================

def main():

    all_points = []

    for document in URLS:

        try:

            points = process_document(
                document
            )

            all_points.extend(
                points
            )

        except Exception as e:

            print(
                f"\nERROR processing "
                f"{document['title']}:"
            )

            print(e)


    # --------------------------------------------------------
    # Store in Qdrant
    # --------------------------------------------------------

    if all_points:

        print(
            "\nUploading documents to Qdrant..."
        )

        client.upsert(

            collection_name=
                DOCUMENT_COLLECTION,

            points=all_points
        )

        print(
            f"Successfully stored "
            f"{len(all_points)} chunks."
        )

    else:

        print(
            "\nNo document chunks were created."
        )


    # --------------------------------------------------------
    # Verify collection
    # --------------------------------------------------------

    collection_info = client.get_collection(
        DOCUMENT_COLLECTION
    )

    print("\n" + "=" * 70)

    print(
        "Municipal document collection:"
    )

    print(
        collection_info
    )


if __name__ == "__main__":

    main()

