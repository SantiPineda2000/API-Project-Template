from fastapi import HTTPException

# GLOBAL EXCEPTIONS
# ---------------------------------------------------------------------------------------------

def Upload_Failed(*, e:str = None):
    return HTTPException(
        status_code=500,
        detail=f"The file could not be uploaded, {e}." if e else "The file could not be uploaded."
    )

def Invalid_Configuration():
    return HTTPException(
        status_code=400, 
        detail="Invalid environment configuration"
        )