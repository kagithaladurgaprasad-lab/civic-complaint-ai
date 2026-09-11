import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


# --------------------------------
# Load CLIP model
# --------------------------------

model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)


# --------------------------------
# Create image embedding
# --------------------------------

def create_image_embedding(image_path):

    # Open image
    image = Image.open(image_path).convert("RGB")

    # Prepare image
    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    # Generate image features
    with torch.no_grad():

        vision_outputs = model.vision_model(
            pixel_values=inputs["pixel_values"]
        )

        pooled_output = vision_outputs.pooler_output

        image_features = model.visual_projection(
            pooled_output
        )

    # Normalize embedding
    image_features = image_features / image_features.norm(
        dim=-1,
        keepdim=True
    )

    return image_features[0].cpu().tolist()