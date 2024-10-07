import pandas as pd
import mysql.connector
from mysql.connector import Error
import random
from faker import Faker
import psutil
import time
import threading
import matplotlib.pyplot as plt

fake = Faker('pt_BR')

# Variável para controle do monitoramento
monitorando = False
metricas_monitoramento = []

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

# Função para limpar a base de dados
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

# Função para medir o uso de recursos do sistema
def medir_recursos():
    cpu_percent = psutil.cpu_percent(interval=1)
    memoria = psutil.virtual_memory()
    uso_memoria = memoria.percent
    memoria_usada = memoria.used / (1024 ** 3)  # Convertendo para GB
    memoria_disponivel = memoria.available / (1024 ** 3)  # Convertendo para GB
    return cpu_percent, uso_memoria, memoria_usada, memoria_disponivel

# Função para monitorar recursos do sistema em paralelo
def monitorar_recursos():
    global metricas_monitoramento
    metricas_monitoramento = []
    while monitorando:
        cpu_percent, uso_memoria, memoria_usada, memoria_disponivel = medir_recursos()
        metricas_monitoramento.append({
            'tempo': time.time(),
            'cpu_percent': cpu_percent,
            'uso_memoria': uso_memoria,
            'memoria_usada': memoria_usada,
            'memoria_disponivel': memoria_disponivel
        })
        time.sleep(0.1)  # Coletar a cada 0.1 segundos

# Função para executar o processo de inserção de dados e medir métricas
def executar_processamento():
    # Limpar a base de dados antes de cada execução
    limpar_base()

    # Carregar o CSV em um DataFrame
    file_path = './base_traduzida_5.csv'
    colaboradores_df = pd.read_csv(file_path, sep=';')

    # Coletar informações antes do processamento
    cpu_inicial, uso_mem_inicial, mem_usada_inicial, mem_disp_inicial = medir_recursos()

    # Tempo inicial
    tempo_inicial = time.time()

    # Iniciar o monitoramento paralelo
    global monitorando
    monitorando = True
    thread_monitoramento = threading.Thread(target=monitorar_recursos)
    thread_monitoramento.start()

    # Conectar ao MySQL e inserir os dados
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='colaborador_db',
            user='sdc',
            password='sdc'
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
                    gerar_nome(), gerar_cpf(), row.get('idade'), row.get('genero_id'), row.get('estado_civil_id'),
                    row.get('telefone', ''), 'rm97804arthur@gmail.com', '123', row.get('formacao_id'),
                    row.get('faculdade_id', 1), row.get('endereco', ''), row.get('numero', ''), row.get('complemento', ''),
                    row.get('bairro', ''), row.get('cidade', ''), row.get('estado', ''), row.get('cep', ''),
                    row.get('departamento_id'), row.get('setor_id', 1), row.get('viagem_trabalho_id'), row.get('salario'),
                    row.get('cargo_id'), row.get('gerente', ''), row.get('tempo_trabalho'),
                    row.get('quantidade_empresas_trabalhou'), row.get('quantidade_anos_trabalhados_anteriormente'),
                    row.get('nivel_escolaridade_id'), row.get('ex_funcionario', 0), row.get('porcentagem_ultimo_aumento'),
                    row.get('distancia_casa'), row.get('quantidade_anos_atual_gestor'), row.get('quantidade_anos_na_empresa'),
                    row.get('quantidade_horas_treinamento_ano'), row.get('nivel_do_trabalho')
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
                    colaborador_id, row['evasao'], row.get('motivo', ''), row.get('sugestao', ''),
                    row.get('observacao', ''), row.get('porcentagem_evasao', 0)
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
                        cursor.execute(inserir_resposta_query, (colaborador_id, pesquisa_id, pergunta_id, resposta_nota))

                for coluna, pergunta_id in pergunta_ids.items():
                    if pergunta_id and not pd.isna(row[coluna]):
                        resposta_nota = row[coluna]
                        inserir_resposta_query = """
                        INSERT INTO resposta_anonima (colaborador_id, pesquisa_id, pergunta_id, nota)
                        VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(inserir_resposta_query, (colaborador_id, pesquisa_id, pergunta_id, resposta_nota))

            connection.commit()
            print("Colaboradores e respostas inseridos com sucesso!")

    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexão ao MySQL foi encerrada.")

    # Finalizar o monitoramento
    monitorando = False
    thread_monitoramento.join()
    # Coletar as métricas de monitoramento ao final
    metricas_monitoramento_final = metricas_monitoramento.copy()

    # Tempo final
    tempo_final = time.time()

    # Coletar informações após o processamento
    cpu_final, uso_mem_final, mem_usada_final, mem_disp_final = medir_recursos()

    # Cálculo do tempo de execução
    tempo_execucao = tempo_final - tempo_inicial

    # Retornar as métricas
    return {
        'tempo_execucao': tempo_execucao,
        'cpu_inicial': cpu_inicial,
        'cpu_final': cpu_final,
        'uso_mem_inicial': uso_mem_inicial,
        'uso_mem_final': uso_mem_final,
        'mem_usada_inicial': mem_usada_inicial,
        'mem_usada_final': mem_usada_final,
        'mem_disp_inicial': mem_disp_inicial,
        'mem_disp_final': mem_disp_final,
        'monitoramento_recursos': metricas_monitoramento_final
    }

# Função para executar o processo 10 vezes e consolidar as métricas
def executar_processos_repetidos(vezes=10):
    metricas = []
    for i in range(vezes):
        print(f"\nExecutando iteração {i + 1} de {vezes}...")
        metricas.append(executar_processamento())

    # Salvar métricas em um DataFrame
    df_metricas = pd.DataFrame(metricas)
    df_metricas.to_csv('metricas_processamento_individual.csv', index=False)
    print("\nMétricas de todas as execuções foram salvas em 'metricas_processamento_individual.csv'.")

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
    print(f"Uso médio de memória antes do processamento: {metricas_consolidadas['uso_mem_inicial']['mean']:.2f}%")
    print(f"Uso médio de memória após o processamento: {metricas_consolidadas['uso_mem_final']['mean']:.2f}%")
    print(f"Memória física média usada antes do processamento: {metricas_consolidadas['mem_usada_inicial']['mean']:.2f} GB")
    print(f"Memória física média usada após o processamento: {metricas_consolidadas['mem_usada_final']['mean']:.2f} GB")
    print(f"Memória disponível média antes do processamento: {metricas_consolidadas['mem_disp_inicial']['mean']:.2f} GB")
    print(f"Memória disponível média após o processamento: {metricas_consolidadas['mem_disp_final']['mean']:.2f} GB")

    # Plotar gráficos de todas as execuções
    plotar_graficos_execucoes(metricas)

# Função para plotar gráficos de todas as execuções
def plotar_graficos_execucoes(metricas_processamento):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    for i, execucao in enumerate(metricas_processamento):
        df = pd.DataFrame(execucao['monitoramento_recursos'])
        if not df.empty:
            tempo_inicial = df['tempo'].min()
            df['tempo'] = df['tempo'] - tempo_inicial

            axes[0].plot(df['tempo'], df['cpu_percent'], label=f'Execução {i+1}')
            axes[1].plot(df['tempo'], df['uso_memoria'], label=f'Execução {i+1}')

    axes[0].set_title('Uso de CPU durante o Processamento (10 execuções)')
    axes[0].set_ylabel('CPU (%)')
    axes[0].legend(loc='upper right')

    axes[1].set_title('Uso de Memória durante o Processamento (10 execuções)')
    axes[1].set_ylabel('Memória (%)')
    axes[1].legend(loc='upper right')

    plt.xlabel('Tempo (s)')
    plt.tight_layout()
    plt.show()

# Executar o processo 10 vezes e salvar as métricas
executar_processos_repetidos(10)
