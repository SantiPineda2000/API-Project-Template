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
        detail="Terminated user"
        )

def Email_Not_Registered():
    return HTTPException(
        status_code=404,
        detail="User does not have an email, please contact your system administrator"
    )

def Invalid_Token():
    return HTTPException(
        status_code=400,
        detail="Invalid token"
    )