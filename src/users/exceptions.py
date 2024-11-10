from fastapi import HTTPException

# USER EXCEPTIONS
# ---------------------------------------------------------------------------------------------

def User_Not_Found():
    return HTTPException(
        status_code=404, 
        detail="The user with this id does not exist in the system"
        )

def User_Already_Exists():
    return HTTPException(
        status_code=400, 
        detail="A user with this username already exists in the system."
        )

def Insufficient_Privileges():
    return HTTPException(
        status_code=403, 
        detail="The user doesn't have enough privileges"
        )

def Username_Conflict():
    return HTTPException(
        status_code=409, 
        detail="User with this username already exists"
        )

def Self_Delete():
    return HTTPException(
        status_code=403, 
        detail="Owners are not allowed to delete themselves"
        )

def Incorrect_Password():
    return HTTPException(
        status_code=400, 
        detail="Incorrect password"
        )

def Same_Password():
    return HTTPException(
        status_code=400, 
        detail="New password cannot be the same as the current one"
        )


# ROLE EXCEPTIONS
# ---------------------------------------------------------------------------------------------

def Role_Not_Found():
    return HTTPException(
        status_code=404, 
        detail="The role provided does not exist in the system."
        )

def Role_Already_Exists():
    return HTTPException(
        status_code=400, 
        detail="This role already exists in the system."
        )

def Role_In_Use():
    return HTTPException(
        status_code=400, 
        detail="Role cannot be deleted because it is linked to user(s)."
        )

def Role_Name_Conflict():
    return HTTPException(
        status_code=409, 
        detail="Role with this name already exists"
        )

# IMAGE EXCEPTIONS
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