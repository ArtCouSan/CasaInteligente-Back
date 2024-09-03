from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Cargo, Colaborador, Departamento, EstadoCivil, Faculdade, FaixaSalarial, Formacao, Genero, NivelEscolaridade, Setor

# Carregar o modelo BERT e o tokenizer
tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
model = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased')

UPLOAD_FOLDER = 'uploads/'

# Configurar o diretório de uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dicionários de sinônimos para padronização
sinonimos_genero = {
    'Masculino': ['M', 'Masculino'],
    'Feminino': ['F', 'Feminino']
}

sinonimos_estado_civil = {
    'Solteiro': ['Solteiro(a)', 'Solteiro'],
    'Casado': ['Casado(a)', 'Casado']
}

sinonimos_nivel_escolaridade = {
    'Ensino Superior - Completo': ['Ensino Superior', 'Graduação', 'Superior Completo'],
    'Ensino Superior - Incompleto': ['Ensino Superior Incompleto']
}

sinonimos_departamento = {
    'Tecnologia da Informação': ['TI', 'Informática']
}

sinonimos_formacao = {
    'Engenharia de Software': ['Engenharia de Software', 'Engenharia de SW'],
    'Ciências da Computação': ['Ciências da Computação', 'Computação']
}

sinonimos_faculdade = {
    'Universidade XYZ': ['Universidade XYZ', 'Uni XYZ']
}

sinonimos_cargo = {
    'Desenvolvedor Sênior': ['Desenvolvedor Sênior', 'Dev Sênior'],
    'Analista de Dados': ['Analista de Dados', 'Data Analyst']
}

def calcular_similaridade(descricao, candidatos):
    """Calcula a similaridade semântica entre a descrição e uma lista de candidatos."""
    descricao_tokens = tokenizer(descricao, return_tensors='pt')
    descricao_embedding = model(**descricao_tokens).last_hidden_state.mean(dim=1)

    candidatos_embeddings = []
    for candidato in candidatos:
        candidato_tokens = tokenizer(candidato, return_tensors='pt')
        candidato_embedding = model(**candidato_tokens).last_hidden_state.mean(dim=1)
        candidatos_embeddings.append(candidato_embedding)
    
    candidatos_embeddings = torch.stack(candidatos_embeddings).squeeze()
    
    similaridades = torch.nn.functional.cosine_similarity(descricao_embedding, candidatos_embeddings)
    maior_similaridade, indice = similaridades.max(dim=0)
    
    return candidatos[indice] if maior_similaridade.item() > 0.8 else descricao

def normalizar_descricao(descricao, sinonimos):
    """Normaliza a descrição baseada nos sinônimos fornecidos utilizando similaridade semântica."""
    for chave, sinonimos_lista in sinonimos.items():
        if descricao in sinonimos_lista:
            return chave
    
    candidatos = list(sinonimos.keys())
    descricao_normalizada = calcular_similaridade(descricao, candidatos)
    return descricao_normalizada

def parse_faixa_salarial(descricao):
    """Extrai o valor mínimo e máximo de uma faixa salarial a partir da descrição."""
    try:
        faixa = descricao.replace('R$', '').replace(',', '').replace('.', '').split('-')
        min_value = int(faixa[0].strip())
        max_value = int(faixa[1].strip())
        return min_value, max_value
    except Exception as e:
        raise ValueError(f"Erro ao parsear a faixa salarial: {descricao}. Detalhes: {e}")

def encaixar_faixa_salarial(salario):
    """Encontra a faixa salarial correspondente a um salário."""
    faixas = FaixaSalarial.query.all()
    
    for faixa in faixas:
        min_value, max_value = parse_faixa_salarial(faixa.descricao)
        if min_value <= salario <= max_value:
            return faixa
    return None

def processar_csv(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        df = pd.read_csv(filepath)
        df.fillna('', inplace=True)

        for index, row in df.iterrows():
            # Normalizar descrições usando os embeddings
            row['genero'] = normalizar_descricao(row['genero'], sinonimos_genero)
            row['estadoCivil'] = normalizar_descricao(row['estadoCivil'], sinonimos_estado_civil)
            row['nivelEscolaridade'] = normalizar_descricao(row['nivelEscolaridade'], sinonimos_nivel_escolaridade)
            row['departamento'] = normalizar_descricao(row['departamento'], sinonimos_departamento)
            row['formacao'] = normalizar_descricao(row['formacao'], sinonimos_formacao)
            row['faculdade'] = normalizar_descricao(row['faculdade'], sinonimos_faculdade)
            row['cargo'] = normalizar_descricao(row['cargo'], sinonimos_cargo)

            # Verificar e aplicar as normalizações antes das consultas
            genero = Genero.query.filter_by(descricao=row['genero']).first() or Genero(descricao=row['genero'])
            estado_civil = EstadoCivil.query.filter_by(descricao=row['estadoCivil']).first() or EstadoCivil(descricao=row['estadoCivil'])
            formacao = Formacao.query.filter_by(descricao=row['formacao']).first() or Formacao(descricao=row['formacao'])
            faculdade = Faculdade.query.filter_by(nome=row['faculdade']).first() or Faculdade(nome=row['faculdade'])
            departamento = Departamento.query.filter_by(nome=row['departamento']).first() or Departamento(nome=row['departamento'])
            setor = Setor.query.filter_by(nome=row['setor']).first() or Setor(nome=row['setor'])
            faixa_salarial = encaixar_faixa_salarial(row['salario'])
            cargo = Cargo.query.filter_by(nome=row['cargo']).first() or Cargo(nome=row['cargo'])
            nivel_escolaridade = NivelEscolaridade.query.filter_by(descricao=row['nivelEscolaridade']).first() or NivelEscolaridade(descricao=row['nivelEscolaridade'])

            if faixa_salarial is None:
                raise Exception(f"Faixa salarial não encontrada para o salário: {row['salario']}")

            # Adicionar os novos objetos ao banco de dados se não existirem
            if genero.id is None:
                db.session.add(genero)
            if estado_civil.id is None:
                db.session.add(estado_civil)
            if formacao.id is None:
                db.session.add(formacao)
            if faculdade.id is None:
                db.session.add(faculdade)
            if departamento.id is None:
                db.session.add(departamento)
            if setor.id is None:
                db.session.add(setor)
            if faixa_salarial.id is None:
                db.session.add(faixa_salarial)
            if cargo.id is None:
                db.session.add(cargo)
            if nivel_escolaridade.id is None:
                db.session.add(nivel_escolaridade)

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
                faixa_salarial=faixa_salarial,
                cargo=cargo,
                gerente=row['gerente'],
                tempo_trabalho=row['tempoTrabalho'],
                quantidade_empresas_trabalhou=row['quantidadeEmpresasTrabalhou'],
                quantidade_anos_trabalhados_anteriormente=row['quantidadeAnosTrabalhadosAnteriormente'],
                nivel_escolaridade=nivel_escolaridade,
                ex_funcionario=row['exFuncionario']
            )

            db.session.add(colaborador)
        db.session.commit()

        return 'Arquivo enviado e processado com sucesso'
    except Exception as e:
        raise Exception(f'Erro ao processar o arquivo: {str(e)}')
