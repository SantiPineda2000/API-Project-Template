from src.schemas import ImageCons

# CONSTANTS
# ---------------------------------------------------------------------------------------------

ALLOWED_CONTENT_TYPES = ["image/png", "image/jpg", "image/jpeg"]
MAX_IMAGE_SIZE = 2000000 # bytes
UPLOAD_SUB_DIR = "user_imgs"

image_const = ImageCons(
    ALLOWED_CONTENT_TYPES=ALLOWED_CONTENT_TYPES,
    MAX_IMAGE_SIZE=MAX_IMAGE_SIZE,
    UPLOAD_SUB_DIR=UPLOAD_SUB_DIR
)