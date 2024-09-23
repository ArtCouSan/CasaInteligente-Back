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
        Olá { colaborador.nome }

        Estamos comprometidos em criar um ambiente de trabalho cada vez melhor para todos, e a sua opinião é fundamental para alcançarmos esse objetivo. Por isso, convidamos você a participar da nossa {pesquisa.titulo}.

        A pesquisa leva apenas 10 minutos para ser respondida. Suas respostas nos ajudarão a entender melhor o que está funcionando bem e onde podemos melhorar, garantindo que sua voz seja ouvida e que possamos juntos construir um ambiente mais saudável e colaborativo.

        Clique no link abaixo para iniciar a pesquisa:

        [Link para a pesquisa]

        Contamos com a sua participação para fazermos do nosso ambiente de trabalho um lugar ainda melhor.

        Se você tiver alguma dúvida ou dificuldade para acessar a pesquisa, entre em contato com o nosso time de RH pelo e-mail ou telefone.

        Muito obrigado por sua colaboração!

        Atenciosamente,

        CiX
    """

    mensagem = MIMEMultipart()
    mensagem['From'] = email_de
    mensagem['To'] = email_para
    mensagem['Subject'] = assunto
    mensagem.attach(MIMEText(corpo, 'plain'))

    try:
        servidor_smtp = smtplib.SMTP(smtp_host, smtp_port)
        servidor_smtp.starttls()
        servidor_smtp.login(smtp_user, smtp_password)
        servidor_smtp.sendmail(email_de, email_para, mensagem.as_string())
        print("E-mail enviado com sucesso!")

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

    finally:
        servidor_smtp.quit()
