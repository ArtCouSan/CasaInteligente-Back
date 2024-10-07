from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import mysql.connector
from mysql.connector import Error
import random
from faker import Faker
import time
import psutil
import os

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

# Função para inserir colaborador e seus dados relacionados
def inserir_colaborador(row):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='colaborador_db',
            user='sdc',
            password='sdc'
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT id FROM pesquisa WHERE titulo = 'Pulso 1'")
            pesquisa = cursor.fetchone()
            pesquisa_id = pesquisa['id']

            cursor.execute("SELECT id, texto FROM pergunta WHERE id IN (SELECT pergunta_id FROM pesquisa_pergunta WHERE pesquisa_id = %s)", (pesquisa_id,))
            perguntas = cursor.fetchall()

            pergunta_ids = {
                'satisfacao_trabalho': None,
                'satisfacao_com_o_ambiente': None,
                'envolvimento_no_trabalho': None,
                'satisfacao_com_relacionamento': None,
                'equilibrio_trabalho_vida': None
            }

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
                gerar_nome(),
                gerar_cpf(),
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

            colaborador_id = cursor.lastrowid

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

            inserir_colaborador_perfil_query = """
            INSERT INTO colaborador_perfil (colaborador_id, perfil_id)
            VALUES (%s, %s)
            """
            cursor.execute(inserir_colaborador_perfil_query, (colaborador_id, 1))  # perfil_id = 1 para "colaborador"

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

            connection.commit()
            print(f"Colaborador {colaborador_id} e respostas inseridos com sucesso!")

    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Função para medir o uso de recursos do processo atual
def medir_recursos_processo():
    process = psutil.Process(os.getpid())  # Obter o processo atual
    cpu_percent = process.cpu_percent(interval=None)  # Uso de CPU do processo em tempo real
    memoria_info = process.memory_info()  # Informações de memória do processo
    memoria_usada = memoria_info.rss / (1024 ** 3)  # Memória usada em GB
    memoria_vms = memoria_info.vms / (1024 ** 3)  # Memória virtual usada em GB
    return cpu_percent, memoria_usada, memoria_vms

# Função para medir o uso de CPU durante o processamento
def medir_cpu_durante_execucao(executor, colaboradores_df):
    cpu_usos = []
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_row = {executor.submit(inserir_colaborador, row): row for _, row in colaboradores_df.iterrows()}
        for future in future_to_row:
            cpu_usos.append(psutil.cpu_percent(interval=None))  # Medir CPU em tempo real
    end_time = time.time()
    return cpu_usos, end_time - start_time

# Função para limpar as tabelas antes de cada execução
def limpar_base():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='colaborador_db',
            user='sdc',
            password='sdc'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            # Excluir os registros das tabelas relacionadas
            cursor.execute("DELETE FROM resposta_anonima")
            cursor.execute("DELETE FROM resposta_fechada")
            cursor.execute("DELETE FROM colaborador_predicao")
            cursor.execute("DELETE FROM colaborador_perfil")
            cursor.execute("DELETE FROM colaborador")
            
            connection.commit()
            print("Base de dados limpa com sucesso!")

    except Error as e:
        print(f"Erro ao limpar a base de dados: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Função principal para repetir o processo 10 vezes e salvar as métricas
def executar_processos_repetidos(vezes=10):
    # Carregar o CSV em um DataFrame antes de iniciar as execuções
    file_path = './base_traduzida_5.csv'
    colaboradores_df = pd.read_csv(file_path, sep=';')

    # Lista para armazenar as métricas de cada execução
    metricas = []

    for i in range(vezes):
        print(f"\nExecutando iteração {i + 1} de {vezes}...")

        # Limpar a base de dados antes de cada execução
        limpar_base()

        # Coletar informações do processo antes do processamento
        cpu_inicial, mem_usada_inicial, mem_vms_inicial = medir_recursos_processo()

        # Medir CPU durante o processamento
        cpu_durante_execucao, tempo_execucao = medir_cpu_durante_execucao(ThreadPoolExecutor(max_workers=4), colaboradores_df)

        # Coletar informações do processo após o processamento
        cpu_final, mem_usada_final, mem_vms_final = medir_recursos_processo()

        # Armazenar métricas
        metricas.append({
            'iteracao': i + 1,
            'tempo_execucao': tempo_execucao,
            'cpu_inicial': cpu_inicial,
            'cpu_final': cpu_final,
            'mem_usada_inicial': mem_usada_inicial,
            'mem_usada_final': mem_usada_final,
            'mem_vms_inicial': mem_vms_inicial,
            'mem_vms_final': mem_vms_final,
            'cpu_medio_execucao': sum(cpu_durante_execucao) / len(cpu_durante_execucao) if cpu_durante_execucao else 0,
            'cpu_max_execucao': max(cpu_durante_execucao) if cpu_durante_execucao else 0
        })

        # Impressão dos resultados
        print(f"Tempo de execução: {tempo_execucao:.2f} segundos")
        print(f"Uso de CPU pelo processo antes do processamento: {cpu_inicial:.2f}%")
        print(f"Uso de CPU pelo processo após o processamento: {cpu_final:.2f}%")
        print(f"Uso médio de CPU durante o processamento: {metricas[-1]['cpu_medio_execucao']:.2f}%")
        print(f"Uso máximo de CPU durante o processamento: {metricas[-1]['cpu_max_execucao']:.2f}%")
        print(f"Memória física usada pelo processo antes do processamento: {mem_usada_inicial:.2f} GB")
        print(f"Memória física usada pelo processo após o processamento: {mem_usada_final:.2f} GB")
        print(f"Memória virtual usada pelo processo antes do processamento: {mem_vms_inicial:.2f} GB")
        print(f"Memória virtual usada pelo processo após o processamento: {mem_vms_final:.2f} GB")

    # Salvar métricas em um DataFrame
    df_metricas = pd.DataFrame(metricas)
    df_metricas.to_csv('metricas_processamento.csv', index=False)
    print("\nMétricas de todas as execuções foram salvas em 'metricas_processamento.csv'.")

    # Cálculo de métricas consolidadas
    metricas_consolidadas = df_metricas.describe()

    # Impressão das métricas consolidadas
    print("\nResumo Consolidado das Execuções:")
    print(metricas_consolidadas)

    # Análise e comentários sobre o desempenho
    print("\nAnálise Geral:")
    print(f"Tempo médio de execução: {metricas_consolidadas['tempo_execucao']['mean']:.2f} segundos")
    print(f"Uso médio de CPU antes do processamento: {metricas_consolidadas['cpu_inicial']['mean']:.2f}%")
    print(f"Uso médio de CPU após o processamento: {metricas_consolidadas['cpu_final']['mean']:.2f}%")
    print(f"Uso médio de CPU durante o processamento: {metricas_consolidadas['cpu_medio_execucao']['mean']:.2f}%")
    print(f"Uso máximo de CPU durante o processamento: {metricas_consolidadas['cpu_max_execucao']['max']:.2f}%")
    print(f"Memória física média usada antes do processamento: {metricas_consolidadas['mem_usada_inicial']['mean']:.2f} GB")
    print(f"Memória física média usada após o processamento: {metricas_consolidadas['mem_usada_final']['mean']:.2f} GB")
    print(f"Memória virtual média usada antes do processamento: {metricas_consolidadas['mem_vms_inicial']['mean']:.2f} GB")
    print(f"Memória virtual média usada após o processamento: {metricas_consolidadas['mem_vms_final']['mean']:.2f} GB")

# Executar o processo 10 vezes
executar_processos_repetidos(10)
