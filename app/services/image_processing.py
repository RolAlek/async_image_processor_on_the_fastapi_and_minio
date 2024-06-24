from PIL import Image


def resize_image(image: Image, max_width: int, max_height: int):
    original_width, original_height = image.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_size = (int(original_width * ratio), int(original_height * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)
