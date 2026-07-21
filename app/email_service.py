import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))

def send_routing_email(sender_email: str, target_department_email: str, original_message: str, category_explanation: str) -> bool:
    """Wysyła e-mail do wybranego działu z nagłówkiem Reply-To ustawionym na nadawcę."""
    try:
        msg = MIMEMultipart()
        msg['From'] = "AI Routing Agent <agent@example.com>"
        msg['To'] = target_department_email
        msg['Reply-To'] = sender_email
        msg['Subject'] = f"Przekierowane zgłoszenie od: {sender_email}"
        
        body = (
            f"Wiadomość została automatycznie sklasyfikowana i przekierowana do Twojego działu.\n\n"
            f"--- Informacje o zgłoszeniu ---\n"
            f"Nadawca: {sender_email}\n"
            f"Odbiorca (dział): {target_department_email}\n"
            f"Wyjaśnienie: {category_explanation}\n\n"
            f"--- Oryginalna treść wiadomości ---\n"
            f"{original_message}\n"
        )
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        logger.info(f"Wysyłanie e-maila do {target_department_email} przez {SMTP_HOST}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail("agent@example.com", [target_department_email], msg.as_string())
            
        logger.info("E-mail wysłany pomyślnie.")
        return True
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania e-maila: {e}")
        raise
