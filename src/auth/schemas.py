from sqlmodel import SQLModel, Field

##=============================================================================================
## SCHEMAS RETURNED BY THE API
##=============================================================================================


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

##=============================================================================================
## SCHEMAS RETURNED BY THE API
##=============================================================================================

# JSON payload containing access token
class Token(SQLModel): 
    access_token: str
    token_type: str = "bearer"

# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
