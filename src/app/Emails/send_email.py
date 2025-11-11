import smtplib
import ssl
from email.message import EmailMessage
from app.core.configs import settings
from app.models.loanRequest_model import LoanRequestModel, Status as RequestStatus, ReasonChoices


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
        
def send_email_for_new_request(receiver_email: str,
                               request_data: LoanRequestModel) -> bool:
    
    msg = EmailMessage()
    msg['Subject'] = "Nova Solicitação de Emprestimo - Multimeios"
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = receiver_email
    msg.set_content(f"Ola {request_data.user.first_name}!\n\nRecebemos sua solicitação para emprestimo do livro ({request_data.book.title})!\nfique atento ao status da sua solicitação!\n\nDados da solicitação:\nSolicitação N#{request_data.id}\nLivro: {request_data.book.title} - {request_data.book.author}\nStatus: {str(request_data.status.value).capitalize()}\n\nAtenciosamente,\nEquipe Multimeios!")
    
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SENDER_EMAIL, settings.APP_PASSWORD)
            server.send_message(msg)
            
        print("E-mail enviado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")
        return False
        
def send_status_update_email(receiver_email: str, 
                             request_data: LoanRequestModel, 
                             loan_id: int = None) -> None:   
    
    msg = EmailMessage()
    msg['Subject'] = "Status da Solicitação - Multimeios"
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = receiver_email
    
    if request_data.status == RequestStatus.approved:
        msg.set_content(f"Ola {request_data.user.first_name}!\n\nSua solicitação de N#{request_data.id} para o emprestimo do livro ({request_data.book.title}) foi aprovada!\n\nO codigo do seu emprestimo é: {loan_id} estamos aguardando a sua retirada!\n\nAtenciosamente,\nEquipe Multimeios!")
    
    if request_data.status == RequestStatus.denied:
        msg.set_content(f"Ola {request_data.user.first_name}!\n\nSua solicitação de N#{request_data.id} para o emprestimo do livro ({request_data.book.title}) foi negada!\n\nMotivo: {request_data.reason if request_data.reason != ReasonChoices.other else request_data.other_reason}\n\nAtenciosamente,\nEquipe Multimeios!")
        
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SENDER_EMAIL, settings.APP_PASSWORD)
            server.send_message(msg)
            
        print("E-mail enviado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")
        return False
        
if __name__ == "__main__":
    send_email_verification_code("blackoutzff9@gmail.com", "123456")  
    

