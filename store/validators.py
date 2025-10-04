from django.core.exceptions import ValidationError


MAX_PRODUCT_IMAGE_SIZE_KB = 1024  # 1 MB


def validate_product_image_size(image):
    if image.size > MAX_PRODUCT_IMAGE_SIZE_KB * 1024:
        raise ValidationError(
            f"ERROR: Image too big, max allowed: {MAX_PRODUCT_IMAGE_SIZE_KB} KB"
        )
