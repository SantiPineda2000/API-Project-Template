from dataclasses import dataclass

##=============================================================================================
## EMAIL SCHEMAS
##=============================================================================================

@dataclass
class EmailData:
    html_content: str
    subject: str