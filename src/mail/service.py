import logging
from typing import Any
from pathlib import Path

import emails
from jinja2 import Template

from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

##=============================================================================================
## MAIL FUNCTIONS
##=============================================================================================

def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(*, email_to: str, subject: str = "", html_content: str = "") -> None:
    assert settings.emails_enabled, "No provided configuration for email variables"
    # Building the message using emails
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host":settings.SMTP_HOST, "port":settings.SMTP_PORT}
    
    # Setting the email service options in the config file
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")

    