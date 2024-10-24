import pandas as pd
import random
from faker import Faker

fake = Faker('pt_BR')

# Função para gerar um CPF válido
def gerar_cpf():
    def calcula_digito(digs):
        s = 0
        peso = len(digs) + 1
        for dig in digs:
            s += int(dig) * peso
            peso -= 1
        resto = 11 - s % 11
        return resto if resto < 10 else 0

    cpf = [random.randint(0, 9) for _ in range(9)]
    cpf.append(calcula_digito(cpf))
    cpf.append(calcula_digito(cpf))
    return "{}{}{}.{}{}{}.{}{}{}-{}{}".format(*cpf)

# Função para gerar um nome aleatório
def gerar_nome():
    return fake.name()

# Caminho do arquivo CSV
file_path = './base_traduzida_5.csv'

# Carregar o CSV em um DataFrame
colaboradores_df = pd.read_csv(file_path, sep=';')

# Estruturas de dados para simular o banco de dados
colaboradores = []
predicoes = []
respostas = []
respostas_anonimas = []

# Dicionário para mapear as respostas do CSV para as opções de resposta
respostas_map = {
    'satisfacao_trabalho': {
        1: 'Baixa',
        2: 'Média',
        3: 'Alta',
        4: 'Muito Alta'
    },
    'satisfacao_com_o_ambiente': {
        1: 'Baixa',
        2: 'Média',
        3: 'Alta',
        4: 'Muito Alta'
    },
    'envolvimento_no_trabalho': {
        1: 'Baixo',
        2: 'Médio',
        3: 'Alto',
        4: 'Muito Alto'
    },
    'satisfacao_com_relacionamento': {
        1: 'Baixa',
        2: 'Média',
        3: 'Alta',
        4: 'Muito Alta'
    },
    'equilibrio_trabalho_vida': {
        1: 'Ruim',
        2: 'Bom',
        3: 'Melhor',
        4: 'Ótimo'
    }
}

# IDs fictícios para perguntas (simulando IDs de banco de dados)
pergunta_ids = {
    'satisfacao_trabalho': 1,
    'satisfacao_com_o_ambiente': 2,
    'envolvimento_no_trabalho': 3,
    'satisfacao_com_relacionamento': 4,
    'equilibrio_trabalho_vida': 5
}

# Iterar sobre o DataFrame e simular a inserção dos dados
for _, row in colaboradores_df.iterrows():
    # Inserir colaborador
    colaborador = {
        'nome': gerar_nome(),
        'cpf': gerar_cpf(),
        'idade': row.get('idade'),
        'genero_id': row.get('genero_id'),
        'estado_civil_id': row.get('estado_civil_id'),
        'telefone': row.get('telefone', ''),
        'email': 'rm97804arthur@gmail.com',
        'senha_hash': '123',
        'formacao_id': row.get('formacao_id'),
        'faculdade_id': row.get('faculdade_id', 1),
        'endereco': row.get('endereco', ''),
        'numero': row.get('numero', ''),
        'complemento': row.get('complemento', ''),
        'bairro': row.get('bairro', ''),
        'cidade': row.get('cidade', ''),
        'estado': row.get('estado', ''),
        'cep': row.get('cep', ''),
        'departamento_id': row.get('departamento_id'),
        'setor_id': row.get('setor_id', 1),
        'viagem_trabalho_id': row.get('viagem_trabalho_id'),
        'salario': row.get('salario'),
        'cargo_id': row.get('cargo_id'),
        'gerente': row.get('gerente', ''),
        'tempo_trabalho': row.get('tempo_trabalho'),
        'quantidade_empresas_trabalhou': row.get('quantidade_empresas_trabalhou'),
        'quantidade_anos_trabalhados_anteriormente': row.get('quantidade_anos_trabalhados_anteriormente'),
        'nivel_escolaridade_id': row.get('nivel_escolaridade_id'),
        'ex_funcionario': row.get('ex_funcionario', 0),
        'porcentagem_ultimo_aumento': row.get('porcentagem_ultimo_aumento'),
        'distancia_casa': row.get('distancia_casa'),
        'quantidade_anos_atual_gestor': row.get('quantidade_anos_atual_gestor'),
        'quantidade_anos_na_empresa': row.get('quantidade_anos_na_empresa'),
        'quantidade_horas_treinamento_ano': row.get('quantidade_horas_treinamento_ano'),
        'nivel_do_trabalho': row.get('nivel_do_trabalho')
    }
    colaboradores.append(colaborador)
    colaborador_id = len(colaboradores)  # Simulando o ID do colaborador

    # Inserir predicao
    predicao = {
        'colaborador_id': colaborador_id,
        'evasao': row['evasao'],
        'motivo': row.get('motivo', ''),
        'sugestao': row.get('sugestao', ''),
        'observacao': row.get('observacao', ''),
        'porcentagem_evasao': row.get('porcentagem_evasao', 0)
    }
    predicoes.append(predicao)

    # Inserir respostas fechadas e anônimas
    for coluna, pergunta_id in pergunta_ids.items():
        if not pd.isna(row[coluna]):
            resposta_nota = row[coluna]
            resposta = {
                'colaborador_id': colaborador_id,
                'pesquisa_id': 1,  # ID fictício da pesquisa
                'pergunta_id': pergunta_id,
                'nota': resposta_nota
            }
            respostas.append(resposta)
            respostas_anonimas.append(resposta)

print("Dados simulados inseridos com sucesso!")
