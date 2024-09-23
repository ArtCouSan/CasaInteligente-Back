from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import *
from transformers import AutoTokenizer, AutoModel, pipeline
from symspellpy import SymSpell, Verbosity
import pkg_resources

# Carregar o modelo BERT e o tokenizer
tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
model = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased')

# Configurar SymSpell para correção ortográfica
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_pt.txt")
bigram_path = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_pt.txt")

# Carregar dicionário de correção ortográfica
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

UPLOAD_FOLDER = 'uploads/'

# Configurar o diretório de uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def obter_sinonimos(tabela, coluna):
    """Obtém as descrições de uma tabela específica para normalização."""
    sinonimos = {}
    registros = db.session.query(tabela).all()
    for registro in registros:
        descricao = getattr(registro, coluna)
        sinonimos[descricao] = [descricao]  # Cada descrição é inicialmente mapeada para si mesma
    return sinonimos

def obter_primeiro_registro(tabela, coluna):
    """Retorna a primeira descrição da tabela para uso como padrão."""
    primeiro_registro = db.session.query(tabela).first()
    return getattr(primeiro_registro, coluna) if primeiro_registro else None

def obter_ou_criar_registro(tabela, descricao, coluna):
    """Obtém um registro existente ou cria um novo com a descrição fornecida."""
    registro = db.session.query(tabela).filter_by(**{coluna: descricao}).first()
    if registro:
        return registro
    else:
        # Criar novo registro com a descrição fornecida
        novo_registro = tabela(**{coluna: descricao})
        db.session.add(novo_registro)
        db.session.commit()
        return novo_registro

def corrigir_ortografia(descricao):
    """Corrige erros ortográficos utilizando SymSpell."""
    suggestions = sym_spell.lookup_compound(descricao, max_edit_distance=2)
    if suggestions:
        return suggestions[0].term
    return descricao

def calcular_similaridade(descricao, candidatos):
    """Calcula a similaridade semântica entre a descrição e uma lista de candidatos."""
    descricao_corrigida = corrigir_ortografia(descricao)  # Corrigir ortografia antes de calcular a similaridade
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
    print(f"Descrição Original: {descricao}, Descrição Corrigida: {descricao_corrigida}, Similaridade: {maior_similaridade.item()}, Escolha: {candidatos[indice]}")
    
    return candidatos[indice] if maior_similaridade.item() > 0.80 else None

def normalizar_descricao_ou_criar(descricao, tabela, coluna, sinonimos, descricao_padrao):
    """Normaliza a descrição utilizando similaridade semântica ou cria um novo registro."""
    if not descricao:
        # Caso venha vazio, retorna o padrão
        return descricao_padrao
    
    candidatos = list(sinonimos.keys())
    descricao_normalizada = calcular_similaridade(descricao, candidatos)
    
    if descricao_normalizada:
        return descricao_normalizada
    else:
        # Se não encontrar similaridade, cria um novo registro
        novo_registro = obter_ou_criar_registro(tabela, descricao, coluna)
        return novo_registro.descricao

def processar_csv(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

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

        for index, row in df.iterrows():
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

        return 'Arquivo enviado e processado com sucesso'
    except Exception as e:
        print(e)
        raise Exception(f'Erro ao processar o arquivo: {str(e)}')
