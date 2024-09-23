import logging
from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import *
from spellchecker import SpellChecker

# Configurar o logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializar PySpellChecker para português
spell = SpellChecker(language='pt')

# Carregar o modelo BERT e o tokenizer
tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
model = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased')

UPLOAD_FOLDER = 'uploads/'

# Configurar o diretório de uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def obter_sinonimos(tabela, coluna):
    """Obtém as descrições de uma tabela específica para normalização."""
    sinonimos = {}
    registros = db.session.query(tabela).all()
    logging.info(f"Obtendo sinonimos para {tabela.__name__} na coluna {coluna}")
    for registro in registros:
        descricao = getattr(registro, coluna, None)
        if descricao:
            sinonimos[descricao] = [descricao]  # Cada descrição é inicialmente mapeada para si mesma
    logging.debug(f"Sinonimos obtidos: {sinonimos}")
    return sinonimos

def obter_primeiro_registro(tabela, coluna):
    """Retorna a primeira descrição da tabela para uso como padrão."""
    primeiro_registro = db.session.query(tabela).first()
    if primeiro_registro:
        descricao = getattr(primeiro_registro, coluna, None)
        logging.debug(f"Primeiro registro de {tabela.__name__} na coluna {coluna}: {descricao}")
        return descricao
    else:
        logging.warning(f"Não há registros na tabela {tabela.__name__}.")
    return None

def obter_ou_criar_registro(tabela, descricao, coluna):
    """Obtém um registro existente ou cria um novo com a descrição fornecida."""
    logging.info(f"Procurando por registro na tabela {tabela.__name__} com {coluna}='{descricao}'")
    registro = db.session.query(tabela).filter_by(**{coluna: descricao}).first()
    if registro:
        logging.info(f"Registro encontrado: {registro}")
        return registro
    else:
        # Criar novo registro com a descrição fornecida
        logging.info(f"Registro não encontrado, criando novo registro em {tabela.__name__} com {coluna}='{descricao}'")
        novo_registro = tabela(**{coluna: descricao})
        db.session.add(novo_registro)
        db.session.commit()
        logging.info(f"Novo registro criado: {novo_registro}")
        return novo_registro

def corrigir_ortografia_pyspellchecker(descricao):
    """Corrige erros ortográficos utilizando PySpellChecker."""
    logging.debug(f"Corrigindo ortografia para: {descricao}")
    palavras = descricao.split()
    palavras_corrigidas = [spell.correction(palavra) for palavra in palavras]
    descricao_corrigida = ' '.join(palavras_corrigidas)
    logging.debug(f"Ortografia corrigida: {descricao_corrigida}")
    return descricao_corrigida

def calcular_similaridade(descricao, candidatos):
    """Calcula a similaridade semântica entre a descrição e uma lista de candidatos."""
    descricao_corrigida = corrigir_ortografia_pyspellchecker(descricao)  # Corrigir ortografia com PySpellChecker
    descricao_tokens = tokenizer(descricao_corrigida, return_tensors='pt')
    descricao_embedding = model(**descricao_tokens).last_hidden_state.mean(dim=1)

    candidatos_embeddings = []
    for candidato in candidatos:
        candidato_tokens = tokenizer(candidato, return_tensors='pt')
        candidato_embedding = model(**candidato_tokens).last_hidden_state.mean(dim=1)
        candidatos_embeddings.append(candidato_embedding)
    
    candidatos_embeddings = torch.stack(candidatos_embeddings).squeeze()
    
    similaridades = torch.nn.functional.cosine_similarity(descricao_embedding, candidatos_embeddings)
    maior_similaridade, indice = similaridades.max(dim=0)
    
    # Debug: imprimir similaridades e o valor escolhido
    logging.debug(f"Descrição Original: {descricao}, Descrição Corrigida: {descricao_corrigida}, Similaridade: {maior_similaridade.item()}, Escolha: {candidatos[indice]}")
    
    return candidatos[indice] if maior_similaridade.item() > 0.80 else None

def normalizar_descricao_ou_criar(descricao, tabela, coluna, sinonimos, descricao_padrao):
    """Normaliza a descrição utilizando similaridade semântica ou cria um novo registro."""
    if not descricao:
        # Caso venha vazio, retorna o padrão
        logging.debug(f"Descrição vazia para {tabela.__name__}. Usando valor padrão: {descricao_padrao}")
        return descricao_padrao
    
    candidatos = list(sinonimos.keys())
    descricao_normalizada = calcular_similaridade(descricao, candidatos)
    
    if descricao_normalizada:
        return descricao_normalizada
    else:
        # Se não encontrar similaridade, cria um novo registro
        logging.info(f"Sem similaridade encontrada. Criando novo registro para {descricao} na tabela {tabela.__name__}")
        novo_registro = obter_ou_criar_registro(tabela, descricao, coluna)
        
        # Corrigir aqui para retornar o valor do atributo correto
        return getattr(novo_registro, coluna)

def processar_csv(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    logging.info(f"Arquivo {filename} salvo com sucesso em {filepath}")

    try:
        # Obter sinônimos das tabelas do banco de dados
        sinonimos_genero = obter_sinonimos(Genero, 'descricao')
        sinonimos_estado_civil = obter_sinonimos(EstadoCivil, 'descricao')
        sinonimos_nivel_escolaridade = obter_sinonimos(NivelEscolaridade, 'descricao')
        sinonimos_departamento = obter_sinonimos(Departamento, 'nome')
        sinonimos_formacao = obter_sinonimos(Formacao, 'descricao')
        sinonimos_faculdade = obter_sinonimos(Faculdade, 'nome')
        sinonimos_cargo = obter_sinonimos(Cargo, 'nome')
        sinonimos_viagem_trabalho = obter_sinonimos(ViagemTrabalho, 'descricao')
        sinonimos_setor = obter_sinonimos(Setor, 'nome')

        # Obter a primeira opção de cada tabela para ser usada como valor padrão
        padrao_genero = obter_primeiro_registro(Genero, 'descricao')
        padrao_estado_civil = obter_primeiro_registro(EstadoCivil, 'descricao')
        padrao_nivel_escolaridade = obter_primeiro_registro(NivelEscolaridade, 'descricao')
        padrao_departamento = obter_primeiro_registro(Departamento, 'nome')
        padrao_formacao = obter_primeiro_registro(Formacao, 'descricao')
        padrao_faculdade = obter_primeiro_registro(Faculdade, 'nome')
        padrao_cargo = obter_primeiro_registro(Cargo, 'nome')
        padrao_viagem_trabalho = obter_primeiro_registro(ViagemTrabalho, 'descricao')
        padrao_setor = obter_primeiro_registro(Setor, 'nome')

        df = pd.read_csv(filepath)
        df.fillna('', inplace=True)
        logging.info(f"Arquivo CSV lido com sucesso. Iniciando processamento de {len(df)} registros.")

        for index, row in df.iterrows():
            logging.debug(f"Processando linha {index}: {row.to_dict()}")
            # Normalizar descrições ou criar novos registros se necessário
            row['genero'] = normalizar_descricao_ou_criar(row['genero'], Genero, 'descricao', sinonimos_genero, padrao_genero)
            row['estadoCivil'] = normalizar_descricao_ou_criar(row['estadoCivil'], EstadoCivil, 'descricao', sinonimos_estado_civil, padrao_estado_civil)
            row['nivelEscolaridade'] = normalizar_descricao_ou_criar(row['nivelEscolaridade'], NivelEscolaridade, 'descricao', sinonimos_nivel_escolaridade, padrao_nivel_escolaridade)
            row['departamento'] = normalizar_descricao_ou_criar(row['departamento'], Departamento, 'nome', sinonimos_departamento, padrao_departamento)
            row['formacao'] = normalizar_descricao_ou_criar(row['formacao'], Formacao, 'descricao', sinonimos_formacao, padrao_formacao)
            row['faculdade'] = normalizar_descricao_ou_criar(row['faculdade'], Faculdade, 'nome', sinonimos_faculdade, padrao_faculdade)
            row['cargo'] = normalizar_descricao_ou_criar(row['cargo'], Cargo, 'nome', sinonimos_cargo, padrao_cargo)
            row['viagemTrabalho'] = normalizar_descricao_ou_criar(row['viagemTrabalho'], ViagemTrabalho, 'descricao', sinonimos_viagem_trabalho, padrao_viagem_trabalho)
            row['setor'] = normalizar_descricao_ou_criar(row['setor'], Setor, 'nome', sinonimos_setor, padrao_setor)

            # Verificar e aplicar as normalizações antes das consultas
            logging.debug(f"Verificando registros no banco de dados para a linha {index}")
            genero = Genero.query.filter_by(descricao=row['genero']).first()
            estado_civil = EstadoCivil.query.filter_by(descricao=row['estadoCivil']).first()
            formacao = Formacao.query.filter_by(descricao=row['formacao']).first()
            faculdade = Faculdade.query.filter_by(nome=row['faculdade']).first()
            departamento = Departamento.query.filter_by(nome=row['departamento']).first()
            setor = Setor.query.filter_by(nome=row['setor']).first()
            cargo = Cargo.query.filter_by(nome=row['cargo']).first()
            nivel_escolaridade = NivelEscolaridade.query.filter_by(descricao=row['nivelEscolaridade']).first()
            viagem_trabalho = ViagemTrabalho.query.filter_by(descricao=row['viagemTrabalho']).first()

            colaborador = Colaborador(
                nome=row['nome'],
                cpf=row['cpf'],
                idade=row['idade'],
                genero=genero,
                estado_civil=estado_civil,
                telefone=row['telefone'],
                email=row['email'],
                formacao=formacao,
                faculdade=faculdade,
                endereco=row['endereco'],
                numero=row['numero'],
                complemento=row['complemento'] if row['complemento'] != '' else None,
                bairro=row['bairro'],
                cidade=row['cidade'],
                estado=row['estado'],
                cep=row['cep'],
                departamento=departamento,
                setor=setor,
                salario=row['salario'],
                cargo=cargo,
                gerente=row['gerente'],
                tempo_trabalho=int(row['tempoTrabalho'].split()[0]) if row['tempoTrabalho'] else 0,
                quantidade_empresas_trabalhou=row['quantidadeEmpresasTrabalhou'],
                quantidade_anos_trabalhados_anteriormente=row['quantidadeAnosTrabalhadosAnteriormente'],
                nivel_escolaridade=nivel_escolaridade,
                viagem_trabalho=viagem_trabalho,
                ex_funcionario=row.get('exFuncionario', False),
                senha_hash=123,  # Atualize esse campo conforme necessário
                porcentagem_ultimo_aumento=row.get('porcentagemUltimoAumento', 0),
                distancia_casa=row.get('distanciaCasa', 0),
                quantidade_anos_atual_gestor=row.get('quantidadeAnosAtualGestor', 0),
                quantidade_anos_na_empresa=row.get('quantidadeAnosNaEmpresa', 0),
                quantidade_horas_treinamento_ano=row.get('quantidadeHorasTreinamentoAno', 0)
            )

            db.session.add(colaborador)
        db.session.commit()

        logging.info("Arquivo processado e dados inseridos com sucesso.")
        return 'Arquivo enviado e processado com sucesso'
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo: {str(e)}", exc_info=True)
        raise Exception(f'Erro ao processar o arquivo: {str(e)}')
