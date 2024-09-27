from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import mysql.connector
from mysql.connector import Error
import random
from faker import Faker
import time
import psutil  # Importa o psutil para monitoramento do sistema

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

# Função para inserir colaborador e seus dados relacionados
def inserir_colaborador(row):
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
            cursor.execute("SELECT id FROM pesquisa WHERE titulo = 'Pulso 1'")
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
                quantidade_horas_treinamento_ano, nivel_trabalho
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores_colaborador = (
                gerar_nome(),  # Gera um nome aleatório
                gerar_cpf(),   # Gera um CPF aleatório
                row.get('idade'),
                row.get('genero_id'),
                row.get('estado_civil_id'),
                row.get('telefone', ''),
                'rm97804arthur@gmail.com',
                '123',  # senha_hash fixo
                row.get('formacao_id'),
                row.get('faculdade_id', 1),
                row.get('endereco', ''),
                row.get('numero', ''),
                row.get('complemento', ''),
                row.get('bairro', ''),
                row.get('cidade', ''),
                row.get('estado', ''),
                row.get('cep', ''),
                row.get('departamento_id'),
                row.get('setor_id', 1),
                row.get('viagem_trabalho_id'),
                row.get('salario'),
                row.get('cargo_id'),
                row.get('gerente', ''),
                row.get('tempo_trabalho'),
                row.get('quantidade_empresas_trabalhou'),
                row.get('quantidade_anos_trabalhados_anteriormente'),
                row.get('nivel_escolaridade_id'),
                row.get('ex_funcionario', 0),
                row.get('porcentagem_ultimo_aumento'),
                row.get('distancia_casa'),
                row.get('quantidade_anos_atual_gestor'),
                row.get('quantidade_anos_na_empresa'),
                row.get('quantidade_horas_treinamento_ano'),
                row.get('nivel_do_trabalho')
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

            # Inserir as respostas associadas a esse colaborador
            for coluna, pergunta_id in pergunta_ids.items():
                if pergunta_id and not pd.isna(row[coluna]):
                    resposta_nota = row[coluna]
                    inserir_resposta_query = """
                    INSERT INTO resposta_anonima (colaborador_id, pesquisa_id, pergunta_id, nota)
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
            print(f"Colaborador {colaborador_id} e respostas inseridos com sucesso!")

    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Função para medir o uso de recursos do sistema
def medir_recursos():
    cpu_percent = psutil.cpu_percent(interval=1)
    memoria = psutil.virtual_memory()
    uso_memoria = memoria.percent
    memoria_usada = memoria.used / (1024 ** 3)  # Convertendo para GB
    memoria_disponivel = memoria.available / (1024 ** 3)  # Convertendo para GB
    return cpu_percent, uso_memoria, memoria_usada, memoria_disponivel

# Coletar informações antes do processamento
cpu_inicial, uso_mem_inicial, mem_usada_inicial, mem_disp_inicial = medir_recursos()

# Tempo inicial
tempo_inicial = time.time()

# Usar ThreadPoolExecutor para paralelizar a inserção dos colaboradores
with ThreadPoolExecutor(max_workers=4) as executor:  # Ajuste max_workers conforme o número de núcleos disponíveis
    executor.map(inserir_colaborador, [row for _, row in colaboradores_df.iterrows()])

# Tempo final
tempo_final = time.time()

# Coletar informações após o processamento
cpu_final, uso_mem_final, mem_usada_final, mem_disp_final = medir_recursos()

# Cálculo do tempo de execução
tempo_execucao = tempo_final - tempo_inicial

# Impressão dos resultados
print(f"Tempo de execução: {tempo_execucao:.2f} segundos")

print("Uso de CPU antes do processamento: {:.2f}%".format(cpu_inicial))
print("Uso de CPU após o processamento: {:.2f}%".format(cpu_final))

print("Uso de memória antes do processamento: {:.2f}%".format(uso_mem_inicial))
print("Uso de memória após o processamento: {:.2f}%".format(uso_mem_final))

print("Memória usada antes do processamento: {:.2f} GB".format(mem_usada_inicial))
print("Memória usada após o processamento: {:.2f} GB".format(mem_usada_final))

print("Memória disponível antes do processamento: {:.2f} GB".format(mem_disp_inicial))
print("Memória disponível após o processamento: {:.2f} GB".format(mem_disp_final))
