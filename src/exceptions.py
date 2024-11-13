from fastapi import HTTPException

##=============================================================================================
# GLOBAL EXCEPTIONS
##=============================================================================================

# UPLOADS EXCEPTIONS
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

# FILE EXCEPTIONS
# ---------------------------------------------------------------------------------------------

def Unsupported_File(*, supported: list[str] | None = None):
    return HTTPException(
        status_code=415,
        detail=f"Unsupported file type, supported files are: {', '.join(supported)}." if supported else "Unsupported file type."
    )

def File_Too_Large(*, max_bytes: int | None = None):
    return HTTPException(
        status_code=413,
        detail=f"Contents of the file too large, the maximum size is {max_bytes*0.0000001} MB." if max_bytes else "Contents of the file too large."
    )

def File_Not_Found():
    return HTTPException(
        status_code=400,
        detail="File not found."
    )