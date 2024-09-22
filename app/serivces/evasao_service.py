import pickle
import numpy as np
import os
import pandas as pd
pd.set_option('display.max_columns', None)  # Mostra todas as colunas
pd.set_option('display.width', 1000)  # Ajusta a largura do console
from sklearn.preprocessing import StandardScaler
from app.models import AnaliseColaborador, RespostaFechada
from ..models import *

# Obter o caminho absoluto do diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho completo para o modelo, scaler e colunas
model_path = os.path.join(current_dir, '../ml/logistic_model.pkl')
scaler_path = os.path.join(current_dir, '../ml/scaler.pkl')
columns_path = os.path.join(current_dir, '../ml/columns.pkl')

# Carregar o modelo, scaler e colunas
with open(model_path, 'rb') as model_file:
    modelo_carregado = pickle.load(model_file)

with open(scaler_path, 'rb') as scaler_file:
    scaler_carregado = pickle.load(scaler_file)

with open(columns_path, 'rb') as columns_file:
    colunas = pickle.load(columns_file)

    # Dicionário de mapeamento para colunas mais amigáveis
coluna_para_nome_amigavel = {
    'idade': 'Idade',
    'salario': 'Salário',
    'tempo_trabalho': 'Tempo de trabalho',
    'quantidade_empresas_trabalhou': 'Quantidade de empresas onde trabalhou',
    'quantidade_anos_trabalhados_anteriormente': 'Anos trabalhados anteriormente',
    'nivel_escolaridade_id': 'Nível de escolaridade',
    'porcentagem_ultimo_aumento': 'Último aumento salarial (%)',
    'distancia_casa': 'Distância até o trabalho (km)',
    'quantidade_anos_atual_gestor': 'Anos com o atual gestor',
    'quantidade_anos_na_empresa': 'Anos na empresa',
    'satisfacao_trabalho': 'Satisfação com o trabalho',
    'satisfacao_com_o_ambiente': 'Satisfação com o ambiente',
    'envolvimento_no_trabalho': 'Envolvimento no trabalho',
    'nivel_do_trabalho': 'Nível do trabalho',
    'satisfacao_com_relacionamento': 'Satisfação com os relacionamentos',
    'quantidade_horas_treinamento_ano': 'Horas de treinamento por ano',
    'equilibrio_trabalho_vida': 'Equilíbrio entre trabalho e vida pessoal',
    'departamento_id': 'Departamento',
    'formacao_id': 'Formação',
    'genero_id': 'Gênero',
    'cargo_id': 'Cargo',
    'estado_civil_id': 'Estado civil',
    'viagem_trabalho_id': 'Viagem a trabalho'
}

# Dicionário de mapeamento para valores codificados
valores_codificados_para_nome = {
    'departamento_id_5': 'Departamento de TI',
    'departamento_id_6': 'Departamento Financeiro',
    'formacao_id_6': 'Formação em Engenharia',
    'formacao_id_7': 'Formação em Administração',
    'genero_id': {1: 'Feminino', 2: 'Masculino'},
    'estado_civil_id': {1: 'Solteiro', 2: 'Casado', 3: 'Divorciado'},
    'cargo_id_5': 'Analista',
    'cargo_id_6': 'Gerente',
    'viagem_trabalho_id_3': 'Viagem Frequente',
    'viagem_trabalho_id_4': 'Viagem Ocasional'
}

def calcular_contribuicao(features, coeficientes):
    """
    Calcula a contribuição de cada feature para a predição final.
    """
    contribuicoes = features * coeficientes
    contribuicao_df = pd.DataFrame({
        'Feature': colunas,
        'Value': features[0],
        'Coeficiente': coeficientes,
        'Contribuicao': contribuicoes[0]
    }).sort_values(by='Contribuicao', key=abs, ascending=False)
    return contribuicao_df

def salvar_feature_importances(contribuicao_df, colaborador_predicao_id):

    EvasaoFeatureImportance.query.filter_by(colaborador_predicao_id=colaborador_predicao_id).delete()
    db.session.commit()

    contribuicao_df = contribuicao_df.sort_values(by='Contribuicao', key=abs, ascending=False)
    top_five_contribuicoes = contribuicao_df.head(5)

    for _, row in top_five_contribuicoes.iterrows():
        feature = row['Feature']
        value = row['Value']
        contribuicao = row['Contribuicao']
        
        nome_amigavel = coluna_para_nome_amigavel.get(feature, feature)
        
        if isinstance(value, (int, float)):
            valor_descricao = f"{value:.2f}"
        else:
            valor_descricao = value
        
        if contribuicao > 0:
            fator_texto = f"A variável '{nome_amigavel}' com valor '{valor_descricao}', que está contribuindo para aumentar a chance de saída"
        else:
            fator_texto = f"A variável '{nome_amigavel}' com valor '{valor_descricao}', que está contribuindo para diminuir a chance de saída"

        # Salvar cada linha de importância como uma nova instância de EvasaoFeatureImportance
        nova_importancia = EvasaoFeatureImportance(
            colaborador_predicao_id=colaborador_predicao_id,
            motivo=fator_texto,
            acuracia=abs(contribuicao)  # Aqui, 'acuracia' representa a magnitude da contribuição
        )
        
        db.session.add(nova_importancia)
        db.session.commit()

def verificar_evasao_colaborador(colaborador):
    data = colaborador  # Dicionário do colaborador

    # Pré-processamento e previsão
    features = gerar_dados_colaborador(data)
    probabilidade = modelo_carregado.predict_proba(features)[0, 1]
    predicao = modelo_carregado.predict(features)[0]

    try:
        importancias = modelo_carregado.named_steps['classifier'].coef_[0]
    except AttributeError:
        raise AttributeError("Erro ao acessar os coeficientes do modelo. Certifique-se de que o modelo é uma regressão logística.")

    contribuicao_df = calcular_contribuicao(features, importancias)

    # Verificar se a análise já existe
    analise_existente = AnaliseColaborador.query.filter_by(colaborador_id=colaborador.get('id')).first()

    explicacao = ""
    if predicao == 1:
        explicacao = f"Este colaborador tem uma alta probabilidade de deixar a empresa ({probabilidade:.2%}). "
    else:
        explicacao = f"Este colaborador tem uma baixa probabilidade de deixar a empresa ({probabilidade:.2%}). "
    

    if analise_existente:
        analise_existente.evasao = "Sim" if int(predicao) == 1 else "Não"
        analise_existente.motivo = ""  
        analise_existente.sugestao = ""  
        analise_existente.observacao = explicacao
        analise_existente.porcentagem_evasao = float(probabilidade) * 100

        db.session.add(analise_existente)
        salvar_feature_importances(contribuicao_df, analise_existente.id)
    else:
        nova_analise = AnaliseColaborador(
            colaborador_id=colaborador.get('id'),
            evasao="Sim" if int(predicao) == 1 else "Não",
            motivo="",
            sugestao="",
            observacao=explicacao,
            porcentagem_evasao=float(probabilidade) * 100
        )
        
        db.session.add(nova_analise)
        db.session.commit()  
        salvar_feature_importances(contribuicao_df, nova_analise.id)
    
    db.session.commit()
    return analise_existente or nova_analise

def gerar_dados_colaborador(colaborador):
    respostas = obter_respostas_mais_recentes(colaborador.get('id'))

    # Dados originais do colaborador
    dados_convertidos = {
        'idade': colaborador.get('idade', 0),
        'salario': float(colaborador.get('salario', 0)),
        'tempo_trabalho': colaborador.get('tempoTrabalho', 0),
        'quantidade_empresas_trabalhou': colaborador.get('quantidadeEmpresasTrabalhou', 0),
        'quantidade_anos_trabalhados_anteriormente': colaborador.get('quantidadeAnosTrabalhadosAnteriormente', 0),
        'nivel_escolaridade_id': colaborador['nivelEscolaridade']['id'],
        'porcentagem_ultimo_aumento': colaborador.get('porcentagemUltimoAumento', 0),
        'distancia_casa': colaborador.get('distanciaCasa', 0),
        'quantidade_anos_atual_gestor': colaborador.get('quantidadeAnosAtualGestor', 0),
        'quantidade_anos_na_empresa': colaborador.get('quantidadeAnosNaEmpresa', 0),
        'quantidade_horas_treinamento_ano': colaborador.get('quantidadeHorasTreinamentoAno', 0),
        'genero_id': colaborador['genero']['id'],
        'estado_civil_id': colaborador['estadoCivil']['id'],
        'departamento_id': colaborador['departamento']['id'],
        'formacao_id': colaborador['formacao']['id'],
        'cargo_id': colaborador['cargo']['id'],
        'nivel_do_trabalho': 2,
        'viagem_trabalho_id': colaborador['viagemTrabalho']['id'],
        'satisfacao_trabalho': respostas.get(1, 0),
        'satisfacao_com_o_ambiente': respostas.get(2, 0),
        'envolvimento_no_trabalho': respostas.get(3, 0),
        'satisfacao_com_relacionamento': respostas.get(4, 0),
        'equilibrio_trabalho_vida': respostas.get(5, 0)
    }

    df_colaborador = pd.DataFrame([dados_convertidos])
    df = pd.get_dummies(data=df_colaborador, columns=['departamento_id', 'formacao_id', 'genero_id', 'cargo_id', 'estado_civil_id', 'viagem_trabalho_id'], drop_first=False)

    # Adicione colunas ausentes com 0
    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = False

    # Organizar colunas de acordo com o esperado pelo modelo
    df = df[colunas]

    # Verifique valores ausentes e substitua-os por zero
    df.fillna(0, inplace=True)

    # Verifique e converta valores inválidos para numéricos
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Aplicar o scaler
    features_scaled = scaler_carregado.transform(df)

    return features_scaled

def obter_respostas_mais_recentes(colaborador_id):
    # IDs das perguntas desejadas
    perguntas_ids = [1, 2, 3, 4, 5]

    # Consulta para obter as respostas mais recentes para cada pergunta
    subquery = (
        db.session.query(
            RespostaFechada.pergunta_id,
            db.func.max(RespostaFechada.data_hora).label('data_hora')
        )
        .filter(RespostaFechada.colaborador_id == colaborador_id, RespostaFechada.pergunta_id.in_(perguntas_ids))
        .group_by(RespostaFechada.pergunta_id)
        .subquery()
    )

    respostas_recentes = (
        db.session.query(RespostaFechada)
        .join(subquery, (RespostaFechada.pergunta_id == subquery.c.pergunta_id) & (RespostaFechada.data_hora == subquery.c.data_hora))
        .filter(RespostaFechada.colaborador_id == colaborador_id)
        .filter(RespostaFechada.pergunta_id.in_(perguntas_ids))
        .order_by(RespostaFechada.pergunta_id)
        .all()
    )

    # Transformar as respostas em dicionário
    respostas_dict = {resposta.pergunta_id: resposta.nota for resposta in respostas_recentes}
    
    return respostas_dict

def obter_mapeamento_dinamico():
    mapeamento = {}

    tabelas_mapeamento = {
        'Genero': {'modelo': Genero, 'atributo': 'descricao'},
        'EstadoCivil': {'modelo': EstadoCivil, 'atributo': 'descricao'},
        'Formacao': {'modelo': Formacao, 'atributo': 'descricao'},
        'Departamento': {'modelo': Departamento, 'atributo': 'nome'},  # Ajustado para 'nome'
        'Cargo': {'modelo': Cargo, 'atributo': 'nome'},
        'ViagemTrabalho': {'modelo': ViagemTrabalho, 'atributo': 'descricao'},
        'NivelEscolaridade': {'modelo': NivelEscolaridade, 'atributo': 'descricao'}
    }

    for nome_tabela, info in tabelas_mapeamento.items():
        modelo = info['modelo']
        atributo = info['atributo']
        dados_tabela = db.session.query(modelo).all()
        mapeamento[nome_tabela] = {getattr(item, 'id'): getattr(item, atributo) for item in dados_tabela}

    return mapeamento

