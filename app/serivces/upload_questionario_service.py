import logging
import pandas as pd
from werkzeug.utils import secure_filename
from app import db
from app.models import Pesquisa, PesquisaPergunta, Pergunta
import os

# Configurar o logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = 'uploads/'

# Configurar o diretório de uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def processar_csv_pesquisa(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    logging.info(f"Arquivo {filename} salvo com sucesso em {filepath}")

    try:
        # Carregar o arquivo CSV
        df = pd.read_csv(filepath)
        df.fillna('', inplace=True)
        logging.info(f"Arquivo CSV lido com sucesso. Iniciando processamento de {len(df)} registros.")

        pesquisa_atual = None  # Variável para armazenar a pesquisa atual

        for index, row in df.iterrows():
            tipo_registro = row['tipo_registro'].strip().lower()
            logging.debug(f"Processando linha {index}: {row.to_dict()}")

            if tipo_registro == 'pesquisa':
                # Criar uma nova pesquisa
                pesquisa_atual = Pesquisa(
                    titulo=row['titulo_pesquisa'].strip(),
                    descricao=row['descricao_pesquisa'].strip(),
                    ano=row['ano']
                )
                db.session.add(pesquisa_atual)
                db.session.flush()  # Usar flush para obter o ID gerado antes de commit
                logging.info(f"Pesquisa criada com ID: {pesquisa_atual.id}")

            elif tipo_registro == 'associacao' and pesquisa_atual:
                # Associar uma pergunta existente à pesquisa atual
                id_pergunta = row['id_pergunta']
                pergunta = Pergunta.query.get(id_pergunta)
                if pergunta:
                    pesquisa_pergunta = PesquisaPergunta(
                        pesquisa_id=pesquisa_atual.id,
                        pergunta_id=pergunta.id
                    )
                    db.session.add(pesquisa_pergunta)
                    logging.info(f"Pergunta ID {pergunta.id} associada à pesquisa ID {pesquisa_atual.id}")
                else:
                    logging.warning(f"Pergunta com ID {id_pergunta} não encontrada. Ignorando associação.")

        # Salvar todas as alterações no banco de dados
        db.session.commit()
        logging.info("Arquivo processado e dados inseridos com sucesso.")
        return 'Arquivo enviado e processado com sucesso'
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo: {str(e)}", exc_info=True)
        db.session.rollback()  # Desfaz qualquer alteração em caso de erro
        raise Exception(f'Erro ao processar o arquivo: {str(e)}')

