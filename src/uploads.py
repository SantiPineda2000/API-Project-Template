# pip install google-cloud-storage # To use the uploading service
# from google.cloud import storage

import os
from fastapi import UploadFile

from src import exceptions

# SINGLE IMAGE UPLOAD
# ---------------------------------------------------------------------------------------------

async def upload_image(*, sub_dir:str, image: UploadFile, environment: str) -> str:
    '''
    Handle image uploads to the path specified in the settings image.
    
    Returns
    ---
    A string containing the image path or URL, in case the upload failed raises an exception. 
    '''
    if environment == "local": # Save file locally for local development
        local_path = os.path.join("./development_files", sub_dir, image.filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            with open(local_path, "wb") as local_file:
                content = await image.read()
                local_file.write(content)
        except Exception as e:
            raise exceptions.Upload_Failed(e=e)

        return local_path
    
    elif environment in ["production", "staging"]: # Save file to Google Cloud Storage for production or staging

        # client = image.Client()
        # bucket = client.bucket(settings.GCS_BUCKET_NAME)  # Bucket name should be set in your settings
        # blob = bucket.blob(image.filename)
        
        # try:
        #     blob.upload_from_string(await image.read(), content_type=image.content_type)
        # except Exception as e:
        #     raise exceptions.Upload_Failed(e=e)
        
        # return blob.public_url
        pass

    raise exceptions.Invalid_Configuration()