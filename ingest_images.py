import os

from qdrant_client.models import PointStruct

from vector_db import (
    client,
    create_image_collection,
    IMAGE_COLLECTION
)

from image_embeddings import create_image_embedding


# ============================================================
# IMAGE FOLDER
# ============================================================

IMAGE_FOLDER = r"C:\Users\admin\OneDrive\Attachments\civic_complaint_rag\Pothole_Image_Data"


# ============================================================
# CREATE IMAGE COLLECTION
# ============================================================

create_image_collection()


# ============================================================
# FIND IMAGE FILES
# ============================================================

image_files = [
    file
    for file in os.listdir(IMAGE_FOLDER)
    if file.lower().endswith(
        (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        )
    )
]


print(
    f"Found {len(image_files)} images."
)


# ============================================================
# CREATE EMBEDDINGS AND QDRANT POINTS
# ============================================================

points = []


for index, file in enumerate(
    image_files,
    start=1
):

    image_path = os.path.join(
        IMAGE_FOLDER,
        file
    )

    try:

        print(
            f"Processing {index}/{len(image_files)}: {file}"
        )


        # ----------------------------------------------------
        # Create CLIP embedding
        # ----------------------------------------------------

        embedding = create_image_embedding(
            image_path
        )


        # ----------------------------------------------------
        # Use filename as image ID
        # ----------------------------------------------------

        image_id = os.path.splitext(file)[0]


        # ----------------------------------------------------
        # Create Qdrant point
        # ----------------------------------------------------

        point = PointStruct(

            id=index,

            vector=embedding,

            payload={

                "image_id": image_id,

                "image_path": image_path,

                "category": "Pothole",

                "source": "Pothole Image Dataset"
            }
        )


        points.append(point)


    except Exception as e:

        print(
            f"ERROR processing {file}: {e}"
        )


# ============================================================
# STORE VECTORS IN QDRANT
# ============================================================

if points:

    client.upsert(

        collection_name=IMAGE_COLLECTION,

        points=points
    )


# ============================================================
# FINAL RESULT
# ============================================================

print(
    f"\nSuccessfully stored "
    f"{len(points)} images in Qdrant."
)