import os
import json
import pickle
import openai
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app import mongo
from app.models import AnaliseColaborador, Colaborador

# Carrega a chave da API a partir do arquivo JSON
with open('config.json', 'r') as file:
    config = json.load(file)
    os.environ['OPENAI_API_KEY'] = config.get('OPENAI_API_KEY')

# Define o caminho relativo para a pasta 'splits' dentro do projeto
current_directory = os.getcwd()
splits_directory = os.path.join(current_directory, r"app\chat\splits")
splits_filepath = os.path.join(splits_directory, 'splits.pkl')
faiss_directory = os.path.join(current_directory, r"app\chat\faiss_index")

# Função para carregar os splits
def load_splits(filepath):
    with open(filepath, 'rb') as file:
        splits = pickle.load(file)
    return splits

# Carregar os splits usando o caminho relativo
splits = load_splits(splits_filepath)

# Definindo os embeddings antes de carregar o FAISS
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# Carregando o índice FAISS localmente
faiss_db = FAISS.load_local(faiss_directory, embeddings, allow_dangerous_deserialization=True)

# Criar o retriever a partir do faiss_db
retriever = faiss_db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

client = OpenAI()

def fazer_pergunta(query, colaborador_id, num_messages=5):
    # Recuperar as últimas mensagens do colaborador específico no MongoDB
    recent_messages = mongo.db.messages.find({'colaborador_id': colaborador_id}).sort('_id', -1).limit(num_messages)
    recent_messages_context = " ".join([msg['text'] for msg in recent_messages])

    # Recuperar as 5 combinações mais relevantes do FAISS
    relevant_docs = retriever.invoke(query)
    faiss_context = " ".join([doc.page_content for doc in relevant_docs])

    # Concatenar o contexto das mensagens recentes e dos documentos relevantes
    full_context = f"{recent_messages_context} {faiss_context}"
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente de perguntas e respostas. Seu objetivo é responder perguntas com a maior precisão possível com base nas instruções e no contexto fornecido. Responda sempre em português."},
            {"role": "user", "content": f"Contexto: {full_context} Pergunta: {query}"}
        ],
        max_tokens=150,
        temperature=0.5
    )

    return completion.choices[0].message.content


def gerar_contexto_colaborador(colaborador_id):
    # Recuperar o colaborador pelo ID
    colaborador = Colaborador.query.get(colaborador_id)
    if not colaborador:
        raise ValueError("Colaborador não encontrado")

    # Recuperar análises preditivas do colaborador
    analises = AnaliseColaborador.query.filter_by(colaborador_id=colaborador_id).all()

    # Criar o dicionário de contexto
    contexto = {
        'colaborador': colaborador.to_dict_somente_dados(),
        'analises': [analise.to_dict_predicao() for analise in analises],
        'respostas': [resposta.to_dict() for resposta in colaborador.respostas]
    }

    return contexto

def gerar_novo_motivo_ia(colaborador_id):
    contexto = gerar_contexto_colaborador(colaborador_id)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Com base nos dados de colaborador, porcentagem de chance de saida e pesquisa de clima, responda o motivo do colaborador estar saindo, sem a sugestao. Responda sempre em português."},
            {"role": "user", "content": f"Contexto: {contexto}"}
        ],
        max_tokens=150,
        temperature=0.5
    )

    return completion.choices[0].message.content

def gerar_nova_sugestao_ia(colaborador_id):
    contexto = gerar_contexto_colaborador(colaborador_id)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Com base nos dados de colaborador, porcentagem de chance de saida e pesquisa de clima, responda sugestoes para evitar do colaborador estar sair, sem o motivo. Responda sempre em português."},
            {"role": "user", "content": f"Contexto: {contexto}"}
        ],
        max_tokens=150,
        temperature=0.5
    )

    return completion.choices[0].message.content