
from PIL import Image


model = None
processor = None


def get_clip_model():

    global model
    global processor

    if model is None or processor is None:

        # Import heavy libraries only when an image
        # embedding is actually required.
        from transformers import (
            CLIPProcessor,
            CLIPModel
        )

        model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32"
        )

        processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )

    return model, processor


def create_image_embedding(image_path):

    # Import torch only when image processing is needed.
    import torch

    clip_model, clip_processor = get_clip_model()

    image = Image.open(
        image_path
    ).convert("RGB")

    inputs = clip_processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        vision_outputs = clip_model.vision_model(
            pixel_values=inputs["pixel_values"]
        )

        pooled_output = (
            vision_outputs.pooler_output
        )

        image_features = (
            clip_model.visual_projection(
                pooled_output
            )
        )

    image_features = (
        image_features
        /
        image_features.norm(
            dim=-1,
            keepdim=True
        )
    )

    return image_features[0].cpu().tolist()

