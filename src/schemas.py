from sqlmodel import SQLModel

##=============================================================================================
## GLOBAL SCHEMAS
##=============================================================================================

# Image configuration constraints
class ImageCons(SQLModel):
    ALLOWED_CONTENT_TYPES: list[str]
    MAX_IMAGE_SIZE: int
    UPLOAD_SUB_DIR: str