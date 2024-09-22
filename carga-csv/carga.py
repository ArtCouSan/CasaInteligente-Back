import pandas as pd
import mysql.connector
from mysql.connector import Error
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

    # Gerar os primeiros 9 dígitos do CPF
    cpf = [random.randint(0, 9) for _ in range(9)]
    # Calcular o primeiro dígito verificador
    cpf.append(calcula_digito(cpf))
    # Calcular o segundo dígito verificador
    cpf.append(calcula_digito(cpf))
    # Formatar o CPF no padrão XXX.XXX.XXX-XX
    return "{}{}{}.{}{}{}.{}{}{}-{}{}".format(*cpf)

# Função para gerar um nome aleatório
def gerar_nome():
    return fake.name()

# Caminho do arquivo CSV
file_path = './base_traduzida_5.csv'

# Carregar o CSV em um DataFrame
colaboradores_df = pd.read_csv(file_path, sep=';')

# Dicionário para mapear as respostas do CSV para as opções de resposta do banco
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

# Conectar ao MySQL
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='colaborador_db',
        user='sdc',  # Substitua pelo seu usuário
        password='sdc'  # Substitua pela sua senha
    )

    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)

        # Obter o ID da pesquisa e das perguntas
        cursor.execute("SELECT id FROM pesquisa WHERE titulo = 'Pesquisa de Satisfação no Trabalho'")
        pesquisa = cursor.fetchone()
        pesquisa_id = pesquisa['id']

        # Obter os IDs das perguntas
        cursor.execute("SELECT id, texto FROM pergunta WHERE id IN (SELECT pergunta_id FROM pesquisa_pergunta WHERE pesquisa_id = %s)", (pesquisa_id,))
        perguntas = cursor.fetchall()

        pergunta_ids = {
            'satisfacao_trabalho': None,
            'satisfacao_com_o_ambiente': None,
            'envolvimento_no_trabalho': None,
            'satisfacao_com_relacionamento': None,
            'equilibrio_trabalho_vida': None
        }

        # Mapeando perguntas para variáveis
        for pergunta in perguntas:
            if 'satisfação no trabalho' in pergunta['texto'].lower():
                pergunta_ids['satisfacao_trabalho'] = pergunta['id']
            elif 'satisfação com o ambiente' in pergunta['texto'].lower():
                pergunta_ids['satisfacao_com_o_ambiente'] = pergunta['id']
            elif 'envolvimento com o trabalho' in pergunta['texto'].lower():
                pergunta_ids['envolvimento_no_trabalho'] = pergunta['id']
            elif 'satisfação com o relacionamento' in pergunta['texto'].lower():
                pergunta_ids['satisfacao_com_relacionamento'] = pergunta['id']
            elif 'equilíbrio entre trabalho e vida' in pergunta['texto'].lower():
                pergunta_ids['equilibrio_trabalho_vida'] = pergunta['id']

        # Iterar sobre o DataFrame e inserir os dados
        for _, row in colaboradores_df.iterrows():

            # Inserir o colaborador na tabela colaborador
            inserir_colaborador_query = """
            INSERT INTO colaborador (
                nome, cpf, idade, genero_id, estado_civil_id, telefone, email, 
                senha_hash, formacao_id, faculdade_id, endereco, numero, complemento, 
                bairro, cidade, estado, cep, departamento_id, setor_id, 
                viagem_trabalho_id, salario, cargo_id, gerente, tempo_trabalho, 
                quantidade_empresas_trabalhou, quantidade_anos_trabalhados_anteriormente, 
                nivel_escolaridade_id, ex_funcionario, porcentagem_ultimo_aumento, 
                distancia_casa, quantidade_anos_atual_gestor, quantidade_anos_na_empresa, 
                quantidade_horas_treinamento_ano
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Gerando valores e passando ao cursor diretamente, sem verificação
            valores_colaborador = (
                gerar_nome(),  # Gera um nome aleatório
                gerar_cpf(),   # Gera um CPF aleatório
                row.get('idade'),  # Pega a idade diretamente do DataFrame
                row.get('genero_id'),  # Pega o genero_id diretamente do DataFrame
                row.get('estado_civil_id'),  # Pega o estado_civil_id diretamente do DataFrame
                row.get('telefone', ''),  # Pega o telefone, com valor padrão como string vazia se não existir
                row.get('email', ''),  # Pega o email, com valor padrão como string vazia se não existir
                '123',  # senha_hash fixo
                row.get('formacao_id'),  # Pega o formacao_id diretamente do DataFrame
                row.get('faculdade_id', 1),  # Pega o faculdade_id, com valor padrão 1 se não existir
                row.get('endereco', ''),  # Pega o endereco, com valor padrão como string vazia se não existir
                row.get('numero', ''),  # Pega o numero, com valor padrão como string vazia se não existir
                row.get('complemento', ''),  # Pega o complemento, com valor padrão como string vazia se não existir
                row.get('bairro', ''),  # Pega o bairro, com valor padrão como string vazia se não existir
                row.get('cidade', ''),  # Pega a cidade, com valor padrão como string vazia se não existir
                row.get('estado', ''),  # Pega o estado, com valor padrão como string vazia se não existir
                row.get('cep', ''),  # Pega o cep, com valor padrão como string vazia se não existir
                row.get('departamento_id'),  # Pega o departamento_id diretamente do DataFrame
                row.get('setor_id', 1),  # Pega o setor_id, com valor padrão 1 se não existir
                row.get('viagem_trabalho_id'),  # Pega o viagem_trabalho_id, com valor padrão 0 se não existir
                row.get('salario'),  # Pega o salario diretamente do DataFrame
                row.get('cargo_id'),  # Pega o cargo_id diretamente do DataFrame
                row.get('gerente', ''),  # Pega o gerente, com valor padrão como string vazia se não existir
                row.get('tempo_trabalho'),  # Pega o tempo_trabalho diretamente do DataFrame
                row.get('quantidade_empresas_trabalhou'),  # Pega o quantidade_empresas_trabalhou diretamente do DataFrame
                row.get('quantidade_anos_trabalhados_anteriormente'),  # Pega o quantidade_anos_trabalhados_anteriormente diretamente do DataFrame
                row.get('nivel_escolaridade_id'),  # Pega o nivel_escolaridade_id diretamente do DataFrame
                row.get('ex_funcionario', 0),  # Pega o ex_funcionario, com valor padrão 0 se não existir
                row.get('porcentagem_ultimo_aumento'),  # Pega o porcentagem_ultimo_aumento diretamente do DataFrame
                row.get('distancia_casa'),  # Pega o distancia_casa diretamente do DataFrame
                row.get('quantidade_anos_atual_gestor'),  # Pega o quantidade_anos_atual_gestor diretamente do DataFrame
                row.get('quantidade_anos_na_empresa'),  # Pega o quantidade_anos_na_empresa diretamente do DataFrame
                row.get('quantidade_horas_treinamento_ano')  # Pega o quantidade_horas_treinamento_ano diretamente do DataFrame
            )

            cursor.execute(inserir_colaborador_query, valores_colaborador)

            # Obter o ID do colaborador recém-inserido
            colaborador_id = cursor.lastrowid

            # Inserir as predições associadas a esse colaborador (supondo que você tenha essas informações no CSV)
            inserir_predicao_query = """
            INSERT INTO colaborador_predicao (
                colaborador_id, evasao, motivo, sugestao, observacao, porcentagem_evasao
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(inserir_predicao_query, (
                colaborador_id,
                row['evasao'],
                row.get('motivo', ''),
                row.get('sugestao', ''),
                row.get('observacao', ''),
                row.get('porcentagem_evasao', 0)
            ))

            # Inserir o colaborador na tabela de perfil como colaborador
            inserir_colaborador_perfil_query = """
            INSERT INTO colaborador_perfil (colaborador_id, perfil_id)
            VALUES (%s, %s)
            """
            cursor.execute(inserir_colaborador_perfil_query, (colaborador_id, 1))  # perfil_id = 1 para "colaborador"

            # Inserir as respostas associadas a esse colaborador
            for coluna, pergunta_id in pergunta_ids.items():
                if pergunta_id and not pd.isna(row[coluna]):
                    resposta_nota = row[coluna]
                    inserir_resposta_query = """
                    INSERT INTO resposta_fechada (colaborador_id, pesquisa_id, pergunta_id, nota)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(inserir_resposta_query, (
                        colaborador_id,
                        pesquisa_id,
                        pergunta_id,
                        resposta_nota
                    ))

        # Confirmar as alterações
        connection.commit()
        print("Colaboradores e respostas inseridos com sucesso!")

except Error as e:
    print(f"Erro ao conectar ao MySQL: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexão ao MySQL foi encerrada.")
