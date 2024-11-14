from src.config import settings

from src.mail.service import send_email, render_email_template
from src.mail.schemas import EmailData

##=============================================================================================
## AUTH and USERS MAILS
##=============================================================================================


def generate_reset_password_email(email_to:str, token: str, username: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {username}"
    link = f"{settings.FRONTEND_HOST}/login/reset-password?token={token}"

    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name":settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link
        }
     )
    
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(email_to: str, username: str, password: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
        }
    )

    return EmailData(html_content=html_content, subject=subject)

