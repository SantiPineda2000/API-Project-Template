from fastapi import HTTPException

# AUTH2 EXCEPTIONS
# ---------------------------------------------------------------------------------------------

def Invalid_Credentials():
    return HTTPException(
        status_code=401,
        detail="Incorrect username or password"
    )

def Terminated_User():
    return HTTPException(
        status_code=401, 
        detail="Terminated User"
        )