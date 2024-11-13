from dataclasses import dataclass
from sqlmodel import SQLModel

##=============================================================================================
## GLOBAL SCHEMAS
##=============================================================================================

# Image configuration constraints
@dataclass
class ImageCons():
    ALLOWED_CONTENT_TYPES: list[str]
    MAX_IMAGE_SIZE: int
    UPLOAD_SUB_DIR: str

# Generic message schema
class Message(SQLModel):
    message: str