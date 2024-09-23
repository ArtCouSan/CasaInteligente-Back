from openai import OpenAI
from flask import jsonify, request
from app.models import Contexto, PerguntaContexto, db
import json
import os

with open('config.json', 'r') as file:
    config = json.load(file)
    os.environ['OPENAI_API_KEY'] = config.get('OPENAI_API_KEY')

client = OpenAI()

def salvar_pergunta_contexto(pergunta):
    try:
        # Obtém todos os contextos disponíveis no banco de dados
        contextos = Contexto.query.all()
        
        # Cria uma lista de textos com a numeração e descrição de cada contexto
        contextos_texto = "\n".join([f"{idx+1}. {contexto.nome}: {contexto.descricao}" for idx, contexto in enumerate(contextos)])

        # Envia a pergunta e os contextos disponíveis para o modelo de IA
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente inteligente que ajuda a identificar o contexto mais apropriado para perguntas com base em uma lista de contextos fornecidos. Responda apenas com o número do contexto mais adequado, sem fornecer explicações ou descrições adicionais."
                },
                {
                    "role": "user",
                    "content": f"""Dada a pergunta abaixo, escolha o contexto mais apropriado entre os seguintes contextos:
                                Contextos:
                                {contextos_texto}
                                Pergunta: "{pergunta.texto}"
                                Responda apenas com o número do contexto, sem mais detalhes.
                                """
                }
            ],
            max_tokens=10,  # Mantendo o número de tokens baixo para evitar respostas longas
            temperature=0.0  # Definindo temperatura baixa para respostas mais determinísticas
        )

        # Extrai o número do contexto retornado pela IA
        resposta_modelo = completion.choices[0].message.content.strip()

        # Tentativa de extrair apenas o número do contexto
        numero_contexto = ''.join([char for char in resposta_modelo if char.isdigit()])

        # Verifica se o número do contexto é um valor válido
        if not numero_contexto:
            print(f"Erro: O modelo retornou um valor inválido: {resposta_modelo}")
            return

        numero_contexto = int(numero_contexto)

        # Verifica se o número do contexto está dentro do intervalo dos contextos disponíveis
        if numero_contexto < 1 or numero_contexto > len(contextos):
            print(f"Erro: Número de contexto fora do intervalo válido: {numero_contexto}")
            return

        # Mapeia o número para o id do contexto correspondente
        contexto_id = contextos[numero_contexto - 1].id

        # Cria a associação entre a pergunta e o contexto no banco de dados
        pergunta_contexto = PerguntaContexto(
            contexto_id=contexto_id,
            pergunta_id=pergunta.id
        )

        db.session.add(pergunta_contexto)
        db.session.commit()

    except Exception as e:
        print(f"Erro ao salvar pergunta_contexto: {str(e)}")


def categorizar_nota(media_nota, min_nota, max_nota):
    """
    Função para calcular a porcentagem de quão perto a média das notas está do valor máximo (bom).
    
    Retorna:
        - A porcentagem indicando a proximidade do bom.
        - A categoria baseada na proximidade (ruim, neutro, bom).
    """
    if media_nota is None or min_nota is None or max_nota is None:
        return 0, 'neutro'
    
    intervalo = max_nota - min_nota
    
    if intervalo == 0:  # Todos os valores são iguais
        return 0, 'neutro'
    
    # Calcular a porcentagem de proximidade do "bom"
    proximidade_bom = ((media_nota - min_nota) / intervalo) * 100

    # Categorizar a nota com base na proximidade
    if proximidade_bom <= 40:  # Primeiro terço
        categoria = 'ruim'
    elif proximidade_bom <= 50:  # Segundo terço
        categoria = 'neutro'
    else:  # Último terço
        categoria = 'bom'
    
    return proximidade_bom, categoria

def analisar(termometro, contexto, perguntas_respostas, min_nota, max_nota, media_nota):
    # Consolidar as perguntas para evitar repetição
    perguntas_consolidadas = consolidar_perguntas(perguntas_respostas)

    proximidade_bom, categoria = categorizar_nota(media_nota, min_nota, max_nota)
    
    # Criação do prompt para o modelo OpenAI
    prompt = f"""
    Análise do Contexto: {contexto.nome}
    Proximidade de Bom: {proximidade_bom}%
    Status Atual: {categoria}

    Perguntas e Respostas:
    {perguntas_consolidadas}

    Com base nas informações acima, explique o motivo para o status '{categoria}'.
    Além disso, forneça sugestões para melhorar este contexto e as percepções dos colaboradores.
    """
    
    print("Prompt Enviado ao Modelo OpenAI:\n", prompt)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de análise de contexto. Responda até no máximo 500 caracteres"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        # Extrair a resposta gerada pelo modelo
        analise = completion.choices[0].message.content.strip()
        return analise
    except Exception as e:
        print(f"Erro ao gerar análise com OpenAI: {str(e)}")
        return "Erro ao gerar análise."
    
def parse_string_to_list(input_string):
    # Divide a string em linhas e remove espaços extras
    linhas = input_string.strip().split('\n')
    perguntas_respostas = []

    for linha in linhas:
        # Divide a linha em 'Pergunta' e 'Nota'
        partes = linha.split(', Nota: ')
        if len(partes) == 2:
            pergunta = partes[0].strip()
            try:
                nota = int(partes[1].strip())
                perguntas_respostas.append({'pergunta': pergunta, 'nota': nota})
            except ValueError:
                print(f"Erro ao converter nota para inteiro: {partes[1].strip()}")
                return "Erro ao processar as notas."

    return perguntas_respostas

def consolidar_perguntas(perguntas_respostas):
    perguntas_respostas = parse_string_to_list(perguntas_respostas)
    try:
        consolidado = {}
        # Itera sobre cada item na lista de perguntas e respostas
        for item in perguntas_respostas:
            pergunta = item['pergunta']
            nota = item['nota']
            # Verifica se a pergunta já está no dicionário consolidado
            if pergunta not in consolidado:
                consolidado[pergunta] = {'total_notas': 0, 'contagem': 0}
            # Adiciona a nota e incrementa a contagem
            consolidado[pergunta]['total_notas'] += nota
            consolidado[pergunta]['contagem'] += 1

        # Lista para armazenar o resultado final consolidado
        resultado_consolidado = []
        # Calcula a média para cada pergunta
        for pergunta, dados in consolidado.items():
            media_nota = dados['total_notas'] / dados['contagem']
            resultado_consolidado.append(f"Pergunta: {pergunta}, Média da Nota: {media_nota:.2f}")
    except Exception as e:
        print(f"Erro ao consolidar perguntas: {str(e)}")
        return "Erro ao consolidar perguntas."

    return "\n".join(resultado_consolidado)