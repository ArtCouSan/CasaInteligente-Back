import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.models import Colaborador, Pesquisa

# Configurações do Gmail
smtp_host = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'rm97804arthur@gmail.com'
smtp_password = 'cbaj qxow aiqd oujo'

def enviar_email(colaborador: Colaborador, pesquisa: Pesquisa):

    # Criação do e-mail
    email_de = smtp_user
    email_para = colaborador.email
    assunto = pesquisa.titulo
    corpo = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{pesquisa.titulo}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #F0F0F0; background-color: #023d31; padding: 20px;">
            <div style="width: 80%; max-width: 600px; margin: 0 auto; background-color: #333333; border: 1px solid #444444; border-radius: 8px; padding: 20px;">
                <p style="font-size: 20px; font-weight: bold; color: #F0F0F0;">Olá {colaborador.nome},</p>
                <div style="margin-top: 10px;">
                    <p>Estamos comprometidos em criar um ambiente de trabalho cada vez melhor para todos, e a sua opinião é fundamental para alcançarmos esse objetivo. Por isso, convidamos você a participar da nossa <strong>{pesquisa.titulo}</strong>.</p>
                    <p>A pesquisa leva apenas 10 minutos para ser respondida. Suas respostas nos ajudarão a entender melhor o que está funcionando bem e onde podemos melhorar, garantindo que sua voz seja ouvida e que possamos juntos construir um ambiente mais saudável e colaborativo.</p>
                    <p>Clique no link abaixo para iniciar a pesquisa:</p>
                    <a href="http://link-da-pesquisa.com" style="display: inline-block; padding: 10px 20px; margin-top: 20px; background-color: #f05724; color: white; text-decoration: none; border-radius: 5px;">Participar da Pesquisa</a>
                    <p style="margin-top: 20px;">Contamos com a sua participação para fazermos do nosso ambiente de trabalho um lugar ainda melhor.</p>
                    <p>Se você tiver alguma dúvida ou dificuldade para acessar a pesquisa, entre em contato com o nosso time de RH pelo e-mail ou telefone.</p>
                    <p>Muito obrigado por sua colaboração!</p>
                </div>
                <div style="margin-top: 20px; font-size: 12px; color: #B0BEC5;">
                    <p>Atenciosamente,<br> CiX</p>
                </div>
            </div>
        </body>
        </html>
    """

    mensagem = MIMEMultipart('alternative')
    mensagem['From'] = email_de
    mensagem['To'] = email_para
    mensagem['Subject'] = assunto
    parte_html = MIMEText(corpo, 'html')
    mensagem.attach(parte_html)

    try:
        servidor_smtp = smtplib.SMTP(smtp_host, smtp_port)
        servidor_smtp.starttls()
        servidor_smtp.login(smtp_user, smtp_password)
        servidor_smtp.sendmail(email_de, email_para, mensagem.as_string())

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

    finally:
        servidor_smtp.quit()
