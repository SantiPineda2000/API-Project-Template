# pip install google-cloud-storage # To use the uploading service
# from google.cloud import storage
from pathlib import Path
import os
from fastapi import UploadFile

from src.exceptions import File_Too_Large, Unsupported_File, Upload_Failed, Invalid_Configuration
from src.config import settings
from src.schemas import ImageCons

# SINGLE IMAGE UPLOAD
# ---------------------------------------------------------------------------------------------

async def upload_image(*, image_const: ImageCons, image: UploadFile, image_name:str) -> str:
    '''
    Handle image uploads to the path specified in the settings image.
    
    Returns
    ---
    A string containing the image path or URL, in case the upload failed raises an exception. 
    '''
    # Checking the constraints passed
    if image.content_type not in image_const.ALLOWED_CONTENT_TYPES:
        raise Unsupported_File(supported=image_const.ALLOWED_CONTENT_TYPES)
        
    elif image.size > image_const.MAX_IMAGE_SIZE:
        raise File_Too_Large(max_bytes=image_const.MAX_IMAGE_SIZE)
        
    # Change the image name but keep the extension
    file_ext = image.filename.split('.')[-1]
    image.filename = image_name + f'.{file_ext}'
    
    if settings.ENVIRONMENT == "local": # Save file locally for local development
        local_path = os.path.join('.', "development_files", image_const.UPLOAD_SUB_DIR, image.filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            with open(local_path, "wb") as local_file:
                content = await image.read()
                local_file.write(content)
        except Exception as e:
            raise Upload_Failed(e=e)

        return local_path
    
    elif settings.ENVIRONMENT in ["production", "staging"]: # Save file to Google Cloud Storage for production or staging

        # client = image.Client()
        # bucket = client.bucket(settings.GCS_BUCKET_NAME)  # Bucket name should be set in your settings
        # blob = bucket.blob(image.filename)
        
        # try:
        #     blob.upload_from_string(await image.read(), content_type=image.content_type)
        # except Exception as e:
        #     raise exceptions.Upload_Failed(e=e)
        
        # return blob.public_url
        pass

    raise Invalid_Configuration()