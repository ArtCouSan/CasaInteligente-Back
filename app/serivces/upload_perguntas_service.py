import logging
import pandas as pd
from werkzeug.utils import secure_filename
from app import db
import os
from app.models import Pergunta, RespostaOpcao

# Configurar o logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = 'uploads/'

# Configurar o diretório de uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def processar_csv_perguntas_respostas(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    logging.info(f"Arquivo {filename} salvo com sucesso em {filepath}")

    try:
        # Carregar o arquivo CSV
        df = pd.read_csv(filepath)
        df.fillna('', inplace=True)
        logging.info(f"Arquivo CSV lido com sucesso. Iniciando processamento de {len(df)} registros.")

        pergunta_atual = None  # Variável para armazenar a pergunta atual

        for index, row in df.iterrows():
            tipo_registro = row['tipo_registro'].strip().lower()
            logging.debug(f"Processando linha {index}: {row.to_dict()}")

            if tipo_registro == 'pergunta':
                # Criar uma nova pergunta
                pergunta_atual = Pergunta(texto=row['texto_pergunta'].strip())
                db.session.add(pergunta_atual)
                db.session.flush()  # Usar flush para obter o ID gerado antes de commit
                logging.info(f"Pergunta criada com ID: {pergunta_atual.id}")

            elif tipo_registro == 'resposta_opcao' and pergunta_atual:
                # Criar uma nova opção de resposta associada à última pergunta criada
                resposta_opcao = RespostaOpcao(
                    texto=row['texto_resposta'].strip(),
                    nota=row['nota_resposta'],
                    pergunta_id=pergunta_atual.id  # Associar à pergunta atual
                )
                db.session.add(resposta_opcao)
                logging.info(f"Resposta opcao criada para pergunta ID {pergunta_atual.id}")

        # Salvar todas as alterações no banco de dados
        db.session.commit()
        logging.info("Arquivo processado e dados inseridos com sucesso.")
        return 'Arquivo enviado e processado com sucesso'
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo: {str(e)}", exc_info=True)
        db.session.rollback()  # Desfaz qualquer alteração em caso de erro
        raise Exception(f'Erro ao processar o arquivo: {str(e)}')
