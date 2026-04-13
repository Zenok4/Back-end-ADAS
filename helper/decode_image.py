import base64


def decode_image(image_base64: str):
    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]

    return base64.b64decode(image_base64)