
import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)


def trimite_email(destinatar: str, subiect: str, mesaj: str):
    server = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT", "465"))
    utilizator = os.getenv("SMTP_USER")
    parola = os.getenv("SMTP_PASSWORD")

    if not all([server, utilizator, parola]):
        raise ValueError("Configurarea emailului este incompleta.")

    email = EmailMessage()
    email["From"] = utilizator
    email["To"] = destinatar
    email["Subject"] = subiect
    email.set_content(mesaj)

    with smtplib.SMTP_SSL(server, port, timeout=20) as smtp:
        smtp.login(utilizator, parola)
        smtp.send_message(email)

    return True

if __name__ == "__main__":
    destinatar = input("Adresa de email destinatar: ").strip()

    try:
        trimite_email(
            destinatar,
            "Test Flux de aprovizionare",
            "Felicitari! Aplicatia poate trimite notificari prin email."
        )
        print("Email trimis cu succes!")
    except Exception as eroare:
        print(f"Eroare la trimiterea emailului: {eroare}")
