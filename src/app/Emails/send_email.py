import smtplib
import ssl
from email.message import EmailMessage
from app.core.configs import settings


def send_email_verification_code(receiver_email: str, code: int, username: str) -> None:

    msg = EmailMessage()
    msg['Subject'] = "Verificação de Email - Multimeios"
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = receiver_email
    msg.set_content(f"Ola {username.capitalize()}!\nObrigado por se cadastrar em nossa plataforma.\n\nSeu código de verificação é: {code}\nirá expirar em 5 minutos!\n\nAtenciosamente,\nEquipe Multimeios!")

    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SENDER_EMAIL, settings.APP_PASSWORD)
            server.send_message(msg)
            
        print("E-mail enviado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")
        
if __name__ == "__main__":
    send_email_verification_code("blackoutzff9@gmail.com", "123456")
        
    

