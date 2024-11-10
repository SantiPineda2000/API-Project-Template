from sqlmodel import SQLModel

##=============================================================================================
## SCHEMAS RETURNED BY THE API
##=============================================================================================

class Token(SQLModel): # JSON payload containing access token
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel): # Contents of JWT token
    sub: str | None = None