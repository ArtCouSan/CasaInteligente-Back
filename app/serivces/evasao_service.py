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

def gerar_explicacao_leiga(contribuicao_df, probabilidade, predicao):
    """
    Gera uma explicação textual amigável com base nas contribuições das features para a predição.

    Parâmetros:
    contribuicao_df (DataFrame): DataFrame com as contribuições das features.
    probabilidade (float): Probabilidade de evasão.
    predicao (int): Predição final (0 ou 1).

    Retorna:
    explicacao (str): Texto explicativo amigável.
    """
    contribuicao_df = contribuicao_df.sort_values(by='Contribuicao', key=abs, ascending=False)

    if predicao == 1:
        explicacao = f"Este colaborador tem uma alta probabilidade de deixar a empresa ({probabilidade:.2%}). "
    else:
        explicacao = f"Este colaborador tem uma baixa probabilidade de deixar a empresa ({probabilidade:.2%}). "
    
    explicacao += "Os cinco principais fatores que influenciam esta previsão são: "

    # Selecionar as cinco principais contribuições
    top_five_contribuicoes = contribuicao_df.head(5)

    # Construir a explicação em texto corrido
    fatores = []
    for index, row in top_five_contribuicoes.iterrows():
        feature = row['Feature']
        value = row['Value']
        contribuicao = row['Contribuicao']
        
        # Nome amigável da feature
        nome_amigavel = coluna_para_nome_amigavel.get(feature, feature)
        
        # Substituir valores codificados por descrições
        if isinstance(value, (int, float)):
            valor_descricao = f"{value:.2f}"
        else:
            valor_descricao = valores_codificados_para_nome.get(feature, {}).get(value, value)
        
        if contribuicao > 0:
            fator_texto = f"a variável '{nome_amigavel}' com valor '{valor_descricao}', que está contribuindo para aumentar a chance de saída"
        else:
            fator_texto = f"a variável '{nome_amigavel}' com valor '{valor_descricao}', que está contribuindo para diminuir a chance de saída"
        
        fatores.append(fator_texto)
    
    # Juntar todos os fatores em uma frase corrida
    explicacao += "; ".join(fatores) + "."

    return explicacao

def verificar_evasao_colaborador(colaborador):
    data = colaborador  # Colaborador já está sendo passado como dicionário

    # Pré-processamento e previsão
    features = gerar_dados_colaborador(data)
    probabilidade = modelo_carregado.predict_proba(features)[0, 1]  # Probabilidade de evasão
    predicao = modelo_carregado.predict(features)[0]  # Previsão de evasão (0 ou 1)

    # Verificando se o modelo dentro do pipeline possui coef_
    try:
        importancias = modelo_carregado.named_steps['classifier'].coef_[0]
    except AttributeError:
        raise AttributeError("Erro ao acessar os coeficientes do modelo. Certifique-se de que o modelo é uma regressão logística.")

    # Calcular as contribuições das features
    contribuicao_df = calcular_contribuicao(features, importancias)

    # Gerar explicação textual amigável
    explicacao = gerar_explicacao_leiga(contribuicao_df, probabilidade, predicao)

    analise_existente = AnaliseColaborador.query.filter_by(colaborador_id=colaborador.get('id')).first()

    if analise_existente:
        # Atualizar a análise existente
        analise_existente.evasao = "Sim" if int(predicao) == 1 else "Não"
        analise_existente.motivo = ""  # Pode adicionar a lógica para determinar o motivo
        analise_existente.sugestao = ""  # Pode adicionar a lógica para determinar a sugestão
        analise_existente.observacao = explicacao
        analise_existente.porcentagem_evasao = float(probabilidade)*100
        return analise_existente
    else:
        # Criar uma nova análise
        nova_analise = AnaliseColaborador(
            colaborador_id=colaborador.get('id'),
            evasao="Sim" if int(predicao) == 1 else "Não",
            motivo="",
            sugestao="",
            observacao=explicacao,
            porcentagem_evasao=float(probabilidade)*100
        )
        return nova_analise

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

    print(respostas_dict)
    
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

