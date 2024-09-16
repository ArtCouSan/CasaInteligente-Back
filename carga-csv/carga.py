import pandas as pd
import mysql.connector
from mysql.connector import Error

# Carregar o CSV
file_path = './base_traduzida.csv'
colaboradores_df = pd.read_csv(file_path, sep=';')

# Conectar ao MySQL
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='colaborador_db',
        user='sdc',  # Substitua pelo seu usuário
        password='sdc'  # Substitua pela sua senha
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Inserir os colaboradores
        for _, row in colaboradores_df.iterrows():
            inserir_colaborador_query = """
            INSERT INTO colaborador (
                cpf, idade, genero_id, estado_civil_id, formacao_id, 
                departamento_id, faixa_salarial_id, cargo_id, 
                tempo_trabalho, quantidade_empresas_trabalhou, 
                quantidade_anos_trabalhados_anteriormente, faculdade_id, 
                aumento_percentual_do_salario, distancia_de_casa, 
                anos_com_o_atual_gestor, anos_na_empresa
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Inserir o colaborador
            cursor.execute(inserir_colaborador_query, (
                row['cpf'],
                row['idade'],
                row['genero_id'],
                row['estado_civil_id'],
                row['formacao_id'],
                row['departamento_id'],
                row['faixa_salarial_id'],
                row['cargo_id'],
                row['tempo_trabalho'],
                row['quantidade_empresas_trabalhou'],
                row['quantidade_anos_trabalhados_anteriormente'],
                row['faculdade_id'],
                row['aumento_percentual_do_salario'],
                row['distancia_de_casa'],
                row['anos_com_o_atual_gestor'],
                row['anos_na_empresa']
            ))

            # Obter o ID do colaborador recém-inserido
            colaborador_id = cursor.lastrowid

            # Inserir as predições associadas a esse colaborador
            inserir_predicao_query = """
            INSERT INTO colaborador_predicao (colaborador_id, evasao, motivo, sugestao, observacao)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(inserir_predicao_query, (
                colaborador_id,
                row['evasao'],
                row.get('motivo', ''),
                row.get('sugestao', ''),
                row.get('observacao', '')
            ))

        # Confirmar as alterações
        connection.commit()
        print("Colaboradores e predições inseridos com sucesso!")

except Error as e:
    print(f"Erro ao conectar ao MySQL: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexão ao MySQL foi encerrada.")