from flask import Blueprint, jsonify, request, session
from pymysql import IntegrityError
from sqlalchemy import asc, desc, func 
from app.serivces.email_service import enviar_email
from app.serivces.evasao_service import verificar_evasao_colaborador
from app.serivces.termometro_service import analisar, categorizar_nota, salvar_pergunta_contexto
from app.serivces.upload_colaborador_service import processar_csv
from app.serivces.upload_perguntas_service import processar_csv_perguntas_respostas
from app.serivces.upload_questionario_service import processar_csv_pesquisa
from .models import *
from bson import ObjectId
from . import mongo     
from app.chat.ia_service import fazer_pergunta, gerar_nova_sugestao_ia, gerar_novo_motivo_ia
from flask import send_file
import os
from math import ceil
from sqlalchemy.orm import joinedload

bp = Blueprint('colaborador', __name__)

from sqlalchemy.orm import joinedload

@bp.route('/colaboradores', methods=['GET'])
def get_colaboradores():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    search_query = request.args.get('search', '', type=str)
    sort_column = request.args.get('sortColumn', '', type=str)
    sort_direction = request.args.get('sortDirection', 'asc', type=str)

    # Filtro de busca
    query = Colaborador.query.join(Colaborador.departamento)  # Faz o join com a tabela Departamento
    
    if search_query:
        # Acesse diretamente a coluna `nome` da tabela `Departamento`
        query = query.filter(
            Colaborador.nome.ilike(f"%{search_query}%") |
            Colaborador.cpf.ilike(f"%{search_query}%") |
            Departamento.nome.ilike(f"%{search_query}%")  # Altere `nome` para a coluna correta no modelo Departamento
        )

    # Aplicando a ordenação
    if sort_column and sort_direction:
        # Verifica se a coluna pertence ao modelo Colaborador
        if hasattr(Colaborador, sort_column):
            if sort_direction == 'asc':
                query = query.order_by(asc(getattr(Colaborador, sort_column)))
            elif sort_direction == 'desc':
                query = query.order_by(desc(getattr(Colaborador, sort_column)))
        # Verifica se a coluna pertence ao modelo Departamento
        elif hasattr(Departamento, sort_column):
            if sort_direction == 'asc':
                query = query.order_by(asc(getattr(Departamento, sort_column)))
            elif sort_direction == 'desc':
                query = query.order_by(desc(getattr(Departamento, sort_column)))

    # Paginação
    paginated_colaboradores = query.paginate(page=page, per_page=per_page, error_out=False)
    colaboradores = paginated_colaboradores.items

    total_items = paginated_colaboradores.total  # Número total de registros na tabela

    return jsonify({
        'colaboradores': [colaborador.to_dict() for colaborador in colaboradores],
        'total_pages': paginated_colaboradores.pages,
        'current_page': page,
        'total_items': total_items
    })

@bp.route('/colaborador/<int:id>', methods=['GET'])
def get_colaborador(id):
    colaborador = Colaborador.query.get_or_404(id)
    return jsonify(colaborador.to_dict())

@bp.route('/colaborador', methods=['POST'])
def create_colaborador():
    data = request.get_json()
    
    colaborador = Colaborador(
        nome=data.get('nome', ''),
        cpf=data.get('cpf', ''),
        idade=data.get('idade', 0),
        genero_id=data.get('genero', {}).get('id', 1),
        estado_civil_id=data.get('estadoCivil', {}).get('id', 1),
        telefone=data.get('telefone', ''),
        email=data.get('email', ''),
        formacao_id=data.get('formacao', {}).get('id', 1),
        faculdade_id=data.get('faculdade', {}).get('id', 1),
        endereco=data.get('endereco', ''),
        numero=data.get('numero', ''),
        complemento=data.get('complemento', ''),
        bairro=data.get('bairro', ''),
        cidade=data.get('cidade', ''),
        estado=data.get('estado', ''),
        cep=data.get('cep', ''),
        departamento_id=data.get('departamento', {}).get('id', 1),
        setor_id=data.get('setor', {}).get('id', 1),
        viagem_trabalho_id=data.get('viagemTrabalho', {}).get('id', 1),
        salario=data.get('salario', 0),
        cargo_id=data.get('cargo', {}).get('id', 1),
        gerente=data.get('gerente', ''),
        tempo_trabalho=data.get('tempoTrabalho', ''),
        quantidade_empresas_trabalhou=data.get('quantidadeEmpresasTrabalhou', 0),
        quantidade_anos_trabalhados_anteriormente=data.get('quantidadeAnosTrabalhadosAnteriormente', 0),
        nivel_escolaridade_id=data.get('nivelEscolaridade', {}).get('id', 1),
        ex_funcionario=data.get('exFuncionario', False),
        distancia_casa=data.get('distanciaCasa', 0),
        quantidade_anos_atual_gestor=data.get('quantidadeAnosAtualGestor', 0),
        quantidade_anos_na_empresa=data.get('quantidadeAnosNaEmpresa', 0),
        quantidade_horas_treinamento_ano=data.get('quantidadeHorasTreinamentoAno', 0),
        porcentagem_ultimo_aumento=data.get('porcentagemUltimoAumento', 0),
        nivel_trabalho=data.get('nivelTrabalho', 1),
        senha_hash=123
    )

    # Adicionando e salvando o colaborador
    db.session.add(colaborador)
    db.session.commit()  # Após o commit, o ID é gerado e associado ao objeto

    # Obter o ID recém-criado
    colaborador_id = colaborador.id
    colaborador = Colaborador.query.get_or_404(colaborador_id)

    # Verificar a análise de evasão do colaborador
    analise = verificar_evasao_colaborador(colaborador.to_dict())

    # Adicionar ou atualizar a análise na sessão
    db.session.add(analise)
    db.session.commit()

    return jsonify(colaborador.to_dict()), 201

@bp.route('/colaborador/<int:id>', methods=['PUT'])
def update_colaborador(id):
    colaborador = Colaborador.query.get_or_404(id)
    data = request.get_json()

    colaborador.nome = data.get('nome', colaborador.nome)
    colaborador.cpf = data.get('cpf', colaborador.cpf)
    colaborador.idade = data.get('idade', colaborador.idade)
    colaborador.genero_id = data.get('genero', {}).get('id', colaborador.genero_id or 1)
    colaborador.estado_civil_id = data.get('estadoCivil', {}).get('id', colaborador.estado_civil_id or 1)
    colaborador.telefone = data.get('telefone', colaborador.telefone)
    colaborador.email = data.get('email', colaborador.email)
    colaborador.formacao_id = data.get('formacao', {}).get('id', colaborador.formacao_id or 1)
    colaborador.faculdade_id = data.get('faculdade', {}).get('id', colaborador.faculdade_id or 1)
    colaborador.endereco = data.get('endereco', colaborador.endereco)
    colaborador.numero = data.get('numero', colaborador.numero)
    colaborador.complemento = data.get('complemento', colaborador.complemento)
    colaborador.bairro = data.get('bairro', colaborador.bairro)
    colaborador.cidade = data.get('cidade', colaborador.cidade)
    colaborador.estado = data.get('estado', colaborador.estado)
    colaborador.cep = data.get('cep', colaborador.cep)
    colaborador.departamento_id = data.get('departamento', {}).get('id', colaborador.departamento_id or 1)
    colaborador.setor_id = data.get('setor', {}).get('id', colaborador.setor_id or 1)
    colaborador.viagem_trabalho_id = data.get('viagemTrabalho', {}).get('id', colaborador.viagem_trabalho_id or 1)
    colaborador.salario = data.get('salario', colaborador.salario)
    colaborador.cargo_id = data.get('cargo', {}).get('id', colaborador.cargo_id or 1)
    colaborador.gerente = data.get('gerente', colaborador.gerente)
    colaborador.tempo_trabalho = data.get('tempoTrabalho', colaborador.tempo_trabalho)
    colaborador.quantidade_empresas_trabalhou = data.get('quantidadeEmpresasTrabalhou', colaborador.quantidade_empresas_trabalhou)
    colaborador.quantidade_anos_trabalhados_anteriormente = data.get('quantidadeAnosTrabalhadosAnteriormente', colaborador.quantidade_anos_trabalhados_anteriormente)
    colaborador.nivel_escolaridade_id = data.get('nivelEscolaridade', {}).get('id', colaborador.nivel_escolaridade_id or 1)
    colaborador.ex_funcionario = data.get('exFuncionario', colaborador.ex_funcionario)
    colaborador.distancia_casa = data.get('distanciaCasa', 0)
    colaborador.quantidade_anos_atual_gestor = data.get('quantidadeAnosAtualGestor', 0)
    colaborador.quantidade_anos_na_empresa = data.get('quantidadeAnosNaEmpresa', 0)
    colaborador.quantidade_horas_treinamento_ano =data.get('quantidadeHorasTreinamentoAno', 0)
    colaborador.porcentagem_ultimo_aumento =data.get('porcentagemUltimoAumento', 0)
    colaborador.nivel_trabalho = data.get('nivelTrabalho', 1),

    # Salvar alterações no colaborador
    db.session.commit()

    # Verificar a análise de evasão do colaborador
    analise = verificar_evasao_colaborador(colaborador.to_dict())

    # Adicionar ou atualizar a análise na sessão
    db.session.add(analise)

    # Commit de todas as alterações
    db.session.commit()

    return jsonify(colaborador.to_dict())

@bp.route('/colaborador/<int:id>', methods=['DELETE'])
def delete_colaborador(id):
    colaborador = Colaborador.query.get_or_404(id)
    db.session.delete(colaborador)
    db.session.commit()
    return jsonify({'message': 'Colaborador excluído com sucesso!'}), 200

@bp.route('/analise-colaboradores', methods=['GET'])
def get_analises_colaboradores():
    # Captura os parâmetros da query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    search_query = request.args.get('search', '', type=str)
    sort_column = request.args.get('sortColumn', '', type=str)
    sort_direction = request.args.get('sortDirection', 'asc', type=str)  # Valor padrão 'asc'

    # Filtro de busca
    query = AnaliseColaborador.query.join(AnaliseColaborador.colaborador)  # Faz o join com a tabela Colaborador

    if search_query:
        # Assumindo que 'colaborador' é a relação e 'nome' e 'cargo' são os atributos do modelo Colaborador
        query = query.filter(
            Colaborador.nome.ilike(f"%{search_query}%") |
            Colaborador.cpf.ilike(f"%{search_query}%")
        )

    # Aplicando a ordenação
    if sort_column and sort_direction:
        # Verifica se a coluna pertence ao modelo AnaliseColaborador
        if hasattr(AnaliseColaborador, sort_column):
            if sort_direction == 'asc':
                query = query.order_by(asc(getattr(AnaliseColaborador, sort_column)))
            elif sort_direction == 'desc':
                query = query.order_by(desc(getattr(AnaliseColaborador, sort_column)))
        # Verifica se a coluna pertence ao modelo Colaborador
        elif hasattr(Colaborador, sort_column):
            if sort_direction == 'asc':
                query = query.order_by(asc(getattr(Colaborador, sort_column)))
            elif sort_direction == 'desc':
                query = query.order_by(desc(getattr(Colaborador, sort_column)))

    # Paginação
    paginated_analises = query.paginate(page=page, per_page=per_page, error_out=False)
    analises = paginated_analises.items

    total_items = paginated_analises.total  # Número total de registros na tabela

    # Retorna os dados em formato JSON
    return jsonify({
        'analises': [analise.to_dict() for analise in analises],
        'total_pages': paginated_analises.pages,
        'current_page': page,
        'total_items': total_items
    })

@bp.route('/analise-colaborador/<int:id>', methods=['GET'])
def get_analise_colaborador(id):
    analise = AnaliseColaborador.query.get_or_404(id)
    return jsonify(analise.to_dict())

@bp.route('/generos', methods=['GET'])
def listar_generos():
    generos = Genero.query.all()
    return jsonify([genero.to_dict() for genero in generos])

@bp.route('/estados-civis', methods=['GET'])
def listar_estados_civis():
    estados_civis = EstadoCivil.query.all()
    return jsonify([estado_civil.to_dict() for estado_civil in estados_civis])

@bp.route('/niveis-escolaridade', methods=['GET'])
def listar_niveis_escolaridade():
    niveis_escolaridade = NivelEscolaridade.query.all()
    return jsonify([nivel_escolaridade.to_dict() for nivel_escolaridade in niveis_escolaridade])

@bp.route('/faculdades', methods=['GET'])
def listar_faculdades():
    faculdades = Faculdade.query.all()
    return jsonify([faculdade.to_dict() for faculdade in faculdades])

@bp.route('/formacoes', methods=['GET'])
def listar_formacoes():
    formacoes = Formacao.query.all()
    return jsonify([formacao.to_dict() for formacao in formacoes])

@bp.route('/departamentos', methods=['GET'])
def listar_departamentos():
    departamentos = Departamento.query.all()
    return jsonify([departamento.to_dict() for departamento in departamentos])

@bp.route('/viagem-trabalho', methods=['GET'])
def listar_viagens():
    tipos = ViagemTrabalho.query.all()
    return jsonify([tipo.to_dict() for tipo in tipos])

@bp.route('/setores', methods=['GET'])
def listar_setores():
    setores = Setor.query.all()
    return jsonify([setor.to_dict() for setor in setores])

@bp.route('/cargos', methods=['GET'])
def listar_cargos():
    cargos = Cargo.query.all()
    return jsonify([cargo.to_dict() for cargo in cargos])

# Rota para listar todas as perguntas
@bp.route('/pergunta', methods=['GET'])
def get_perguntas():
    # Carrega todas as perguntas, incluindo as opções de resposta
    perguntas = Pergunta.query.all()
    return jsonify([pergunta.to_dict(include_respostas=True) for pergunta in perguntas])

# Rota para adicionar uma nova pergunta
@bp.route('/pergunta', methods=['POST'])
def create_pergunta():
    data = request.get_json()

    # Cria a nova pergunta
    pergunta = Pergunta(
        texto=data.get('texto')
    )
    db.session.add(pergunta)
    db.session.commit()

    # Verifica se há opções de resposta associadas e as adiciona
    opcoes_resposta = data.get('opcoes_resposta', [])

    for opcao in opcoes_resposta:
        resposta_opcao = RespostaOpcao(
            texto=opcao.get('texto'),
            nota=opcao.get('nota'),
            pergunta_id=pergunta.id
        )
        db.session.add(resposta_opcao)

    db.session.commit()

    salvar_pergunta_contexto(pergunta)

    # Retorna a pergunta com as opções de resposta
    return jsonify(pergunta.to_dict(include_respostas=True)), 201

# Rota para atualizar uma pergunta existente
@bp.route('/pergunta/<int:id>', methods=['PUT'])
def update_pergunta(id):
    pergunta = Pergunta.query.get_or_404(id)
    data = request.get_json()

    # Atualiza o texto da pergunta
    pergunta.texto = data.get('texto', pergunta.texto)

    # Atualiza ou insere novas opções de resposta
    novas_opcoes = data.get('opcoes_resposta', [])
    
    # Deleta as opções antigas
    RespostaOpcao.query.filter_by(pergunta_id=pergunta.id).delete()

    # Adiciona ou edita as novas opções de resposta
    for opcao in novas_opcoes:
        nova_resposta_opcao = RespostaOpcao(
            texto=opcao.get('texto'),
            nota=opcao.get('nota'),
            pergunta_id=pergunta.id
        )
        db.session.add(nova_resposta_opcao)

    # Salva as alterações no banco de dados
    db.session.commit()

    salvar_pergunta_contexto(pergunta)

    return jsonify(pergunta.to_dict(include_respostas=True))

@bp.route('/pergunta/<int:id>', methods=['DELETE'])
def delete_pergunta(id):
    # Obtém a pergunta, ou retorna 404 se não existir
    pergunta = Pergunta.query.get_or_404(id)
    
    # Deletar todas as associações na tabela PerguntaContexto
    PerguntaContexto.query.filter_by(pergunta_id=pergunta.id).delete()

    # Agora, exclui a pergunta
    db.session.delete(pergunta)
    db.session.commit()
    return jsonify({'message': 'Pergunta excluída com sucesso!'}), 200

# Rota para upload de CSV de perguntas
# @bp.route('/upload-perguntas', methods=['POST'])
# def upload_perguntas():
#     if 'file' not in request.files:
#         return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
    
#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({'error': 'Nenhum arquivo foi selecionado'}), 400
    
#     if file and file.filename.endswith('.csv'):
#         try:
#             resultado = processar_csv_pergunta(file)
#             return jsonify({'message': resultado}), 200
#         except Exception as e:
#             return jsonify({'error': f'Erro ao processar o arquivo: {str(e)}'}), 500
#     else:
#         return jsonify({'error': 'Tipo de arquivo não permitido, apenas CSVs são aceitos'}), 400

# Rota para download de um template CSV de perguntas
@bp.route('/download-template-perguntas', methods=['GET'])
def download_template_perguntas():
    filepath = os.path.abspath(os.path.join('app', 'templates', 'pergunta.csv'))
    
    if not os.path.exists(filepath):
        return {"error": "Template file not found"}, 404
    
    return send_file(filepath, as_attachment=True, download_name='pergunta.csv', mimetype='text/csv')

# Rota para adicionar ou atualizar uma resposta de um colaborador a uma pergunta
@bp.route('/colaborador/<int:colaborador_id>/resposta', methods=['POST'])
def create_or_update_resposta(colaborador_id):
    data = request.get_json()

    try:
        # Verifique se a pesquisa é anônima ou fechada
        is_pesquisa_fechada = data.get('is_pesquisa_fechada', False)
        is_pesquisa_anonima = data.get('is_pesquisa_anonima', False)

        # Se for uma pesquisa anônima, use o modelo RespostaAnonima
        if is_pesquisa_anonima:
            resposta_existente = RespostaAnonima.query.filter_by(
                colaborador_id=colaborador_id,
                pergunta_id=data['pergunta_id'],
                pesquisa_id=data['pesquisa_id']
            ).first()
            if resposta_existente:
                resposta_existente.nota = data['nota']
            else:
                nova_resposta = RespostaAnonima(
                    colaborador_id=colaborador_id,
                    pergunta_id=data['pergunta_id'],
                    pesquisa_id=data['pesquisa_id'],
                    nota=data['nota']
                )
                db.session.add(nova_resposta)
        # Se for uma pesquisa fechada, use o modelo RespostaFechada
        elif is_pesquisa_fechada:
            resposta_existente = RespostaFechada.query.filter_by(
                colaborador_id=colaborador_id,
                pergunta_id=data['pergunta_id'],
                pesquisa_id=data['pesquisa_id']
            ).first()
            if resposta_existente:
                resposta_existente.nota = data['nota']
            else:
                nova_resposta = RespostaFechada(
                    colaborador_id=colaborador_id,
                    pergunta_id=data['pergunta_id'],
                    pesquisa_id=data['pesquisa_id'],
                    nota=data['nota']
                )
                db.session.add(nova_resposta)

        db.session.commit()
        return jsonify({"message": "Resposta criada ou atualizada com sucesso"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Erro ao tentar criar ou atualizar a resposta."}), 400

@bp.route('/colaborador/<int:colaborador_id>/respostas/fechadas', methods=['GET'])
def get_respostas_fechadas(colaborador_id):
    """
    Retorna as respostas do colaborador para pesquisas fechadas.
    """
    try:
        respostas_fechadas = RespostaFechada.query.join(Pesquisa).filter(
            RespostaFechada.colaborador_id == colaborador_id,
            Pesquisa.is_pesquisa_fechada == 1
        ).all()

        if respostas_fechadas:
            return jsonify([resposta.to_dict() for resposta in respostas_fechadas]), 200
        else:
            return jsonify({'message': 'Nenhuma resposta encontrada para pesquisas fechadas.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/colaborador/<int:colaborador_id>/respostas/anonimas', methods=['GET'])
def get_respostas_anonimas(colaborador_id):
    """
    Retorna as respostas do colaborador para pesquisas anônimas.
    """
    try:
        respostas_anonimas = RespostaAnonima.query.join(Pesquisa).filter(
            RespostaAnonima.colaborador_id == colaborador_id,
            Pesquisa.is_pesquisa_anonima == 1
        ).all()

        if respostas_anonimas:
            return jsonify([resposta.to_dict() for resposta in respostas_anonimas]), 200
        else:
            return jsonify({'message': 'Nenhuma resposta encontrada para pesquisas anônimas.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/colaborador/<int:colaborador_id>/messages', methods=['GET'])
def get_messages(colaborador_id):
    messages = mongo.db.messages.find({'colaborador_id': colaborador_id})
    return jsonify([{'_id': str(ObjectId(msg['_id'])), 'text': msg['text'], 'sender': msg['sender']} for msg in messages])

@bp.route('/colaborador/<int:colaborador_id>/messages', methods=['POST'])
def add_message(colaborador_id):
    data = request.get_json()
    
    # Salvar mensagem do usuário
    user_message_id = mongo.db.messages.insert_one({
        'text': data['text'], 
        'colaborador_id': colaborador_id,
        'sender': 'user'
    }).inserted_id
    
    # Gerar e salvar resposta do bot
    bot_response = fazer_pergunta(data['text'], colaborador_id)
    bot_message_id = mongo.db.messages.insert_one({
        'text': bot_response, 
        'colaborador_id': colaborador_id,
        'sender': 'bot'
    }).inserted_id
    
    # Retornar a mensagem do bot para o frontend
    return jsonify({
        '_id': str(ObjectId(bot_message_id)), 
        'text': bot_response, 
        'sender': 'bot'
    }), 201

@bp.route('/analise-colaborador/<int:colaborador_id>/gerar-novo-motivo', methods=['POST'])
def gerar_novo_motivo(colaborador_id):

    colaborador = AnaliseColaborador.query.filter_by(colaborador_id=colaborador_id).first()

    if not colaborador:
        return jsonify({'error': 'Colaborador não encontrado'}), 404
    
    novo_motivo = gerar_novo_motivo_ia(colaborador_id)

    colaborador.motivo = novo_motivo
    db.session.commit()

    return jsonify({
        'success': 'Motivo atualizado com sucesso',
        'novo_motivo': novo_motivo
    }), 200

@bp.route('/analise-colaborador/<int:colaborador_id>/gerar-nova-sugestao', methods=['POST'])
def gerar_nova_sugestao(colaborador_id):

    colaborador = AnaliseColaborador.query.filter_by(colaborador_id=colaborador_id).first()

    if not colaborador:
        return jsonify({'error': 'Colaborador não encontrado'}), 404
    
    nova_sugestao = gerar_nova_sugestao_ia(colaborador_id)

    colaborador.sugestao = nova_sugestao
    db.session.commit()

    return jsonify({
        'success': 'Sugestao atualizada com sucesso',
        'nova_sugestao': nova_sugestao
    }), 200

@bp.route('/colaborador/upload', methods=['POST'])
def upload_colaboradores():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo foi selecionado'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            resultado = processar_csv(file)
            return jsonify({'message': resultado}), 200
        except Exception as e:
            return jsonify({'error': f'Erro ao processar o arquivo: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Tipo de arquivo não permitido, apenas CSVs são aceitos'}), 400
    
@bp.route('/pergunta/upload', methods=['POST'])
def upload_pergunta():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo foi selecionado'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            resultado = processar_csv_perguntas_respostas(file)
            return jsonify({'message': resultado}), 200
        except Exception as e:
            return jsonify({'error': f'Erro ao processar o arquivo: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Tipo de arquivo não permitido, apenas CSVs são aceitos'}), 400
    
@bp.route('/pesquisa/upload', methods=['POST'])
def upload_pesquisa():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo foi selecionado'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            resultado = processar_csv_pesquisa(file)
            return jsonify({'message': resultado}), 200
        except Exception as e:
            return jsonify({'error': f'Erro ao processar o arquivo: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Tipo de arquivo não permitido, apenas CSVs são aceitos'}), 400
    
@bp.route('/colaborador/download-template', methods=['GET'])
def download_template():
    # Ajusta o caminho para ser absoluto
    filepath = os.path.abspath(os.path.join('app', 'templates', 'colaborador.csv'))
    
    # Verifica se o arquivo existe
    if not os.path.exists(filepath):
        return {"error": "Template file not found"}, 404
    
    # Retorna o arquivo para download
    return send_file(filepath, as_attachment=True, download_name='colaborador.csv', mimetype='text/csv')

@bp.route('/pergunta/download-template', methods=['GET'])
def download_pergunta():
    # Ajusta o caminho para ser absoluto
    filepath = os.path.abspath(os.path.join('app', 'templates', 'pergunta.csv'))
    
    # Verifica se o arquivo existe
    if not os.path.exists(filepath):
        return {"error": "Template file not found"}, 404
    
    # Retorna o arquivo para download
    return send_file(filepath, as_attachment=True, download_name='pergunta.csv', mimetype='text/csv')

@bp.route('/pesquisa/download-template', methods=['GET'])
def download_pesquisa():
    # Ajusta o caminho para ser absoluto
    filepath = os.path.abspath(os.path.join('app', 'templates', 'pesquisa.csv'))
    
    # Verifica se o arquivo existe
    if not os.path.exists(filepath):
        return {"error": "Template file not found"}, 404
    
    # Retorna o arquivo para download
    return send_file(filepath, as_attachment=True, download_name='pesquisa.csv', mimetype='text/csv')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    cpf = data.get('cpf')
    password = data.get('password')

    colaborador = Colaborador.query.filter_by(cpf=cpf).first()

    if colaborador is None:
        return jsonify({"error": "Colaborador não encontrado"}), 404

    if colaborador.senha_hash != password:
        return jsonify({"error": "Credenciais inválidas"}), 401

    perfis = colaborador.perfis
    perfis_data = [perfil.to_dict() for perfil in perfis]

    return jsonify(colaborador.to_dict()), 200
    
@bp.route('/logout', methods=['POST'])
def logout():
    session.pop('colaborador_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

# Rota para listar todas as pesquisas com perguntas
@bp.route('/pesquisa', methods=['GET'])
def get_pesquisas():
    pesquisas = Pesquisa.query.all()
    return jsonify([pesquisa.to_dict(include_perguntas=True) for pesquisa in pesquisas])

# Rota para adicionar uma nova pesquisa
@bp.route('/pesquisa', methods=['POST'])
def create_pesquisa():
    data = request.get_json()
    
    # Criar a pesquisa com os dados fornecidos
    pesquisa = Pesquisa(
        titulo=data.get('titulo'),
        descricao=data.get('descricao', ''),
        ano=data.get('ano'),  # Define o ano padrão como o atual se não fornecido,
        is_pesquisa_fechada=data.get('is_pesquisa_fechada', None),  # Valor simples
        is_pesquisa_anonima=data.get('is_pesquisa_anonima', None)   # Valor simples
    )
    
    # Extrair os IDs das perguntas
    perguntas = data.get('perguntas', [])
    perguntas_ids = [pergunta.get('id') for pergunta in perguntas if pergunta.get('id')]

    if perguntas_ids:
        # Buscar as perguntas no banco de dados
        perguntas_obj = Pergunta.query.filter(Pergunta.id.in_(perguntas_ids)).all()
        # Associar as perguntas à pesquisa
        pesquisa.perguntas = perguntas_obj
    
    try:
        # Adicionar a pesquisa à sessão e commit
        db.session.add(pesquisa)
        db.session.commit()
        return jsonify(pesquisa.to_dict(include_perguntas=True)), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro ao adicionar pesquisa'}), 400

@bp.route('/pesquisa/<int:id>', methods=['PUT'])
def update_pesquisa(id):
    pesquisa = Pesquisa.query.get_or_404(id)
    data = request.get_json()

    # Atualiza os dados da pesquisa
    pesquisa.titulo = data.get('titulo', pesquisa.titulo)
    pesquisa.descricao = data.get('descricao', pesquisa.descricao)
    pesquisa.ano = data.get('ano', pesquisa.ano)

    # Atualiza as perguntas associadas à pesquisa
    perguntas_data = data.get('perguntas', [])
    if perguntas_data:
        # Extrair os IDs das perguntas fornecidas no payload
        perguntas_ids = [pergunta.get('id') for pergunta in perguntas_data if pergunta.get('id')]
        
        # Buscar as perguntas no banco de dados
        perguntas_obj = Pergunta.query.filter(Pergunta.id.in_(perguntas_ids)).all()
        
        # Associar as perguntas encontradas à pesquisa
        pesquisa.perguntas = perguntas_obj
    
    try:
        db.session.commit()
        return jsonify(pesquisa.to_dict(include_perguntas=True)), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar pesquisa'}), 400

# Rota para deletar uma pesquisa
@bp.route('/pesquisa/<int:id>', methods=['DELETE'])
def delete_pesquisa(id):
    pesquisa = Pesquisa.query.get_or_404(id)
    
    try:
        db.session.delete(pesquisa)
        db.session.commit()
        return jsonify({'message': 'Pesquisa excluída com sucesso!'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro ao excluir pesquisa'}), 400

@bp.route('/pesquisa/fechada', methods=['GET'])
def get_pesquisa_fechada():
    pesquisa = Pesquisa.query.filter_by(is_pesquisa_fechada=1).first()
    if not pesquisa:
        return jsonify({'error': 'Nenhuma pesquisa fechada encontrada'}), 404

    # Inclui as opções de resposta de cada pergunta
    return jsonify(pesquisa.to_dict(include_perguntas=True))

@bp.route('/pesquisa/anonima', methods=['GET'])
def get_pesquisa_anonima():
    pesquisa = Pesquisa.query.filter_by(is_pesquisa_anonima=1).first()
    if not pesquisa:
        return jsonify({'error': 'Nenhuma pesquisa anonima encontrada'}), 404

    # Inclui as opções de resposta de cada pergunta
    return jsonify(pesquisa.to_dict(include_perguntas=True))

@bp.route('/pesquisa/marcar/<int:id>', methods=['PATCH'])
def marcar_pesquisa(id):
    data = request.get_json()

    # Verificar se a pesquisa existe
    pesquisa = Pesquisa.query.get_or_404(id)

    # Definir os campos a serem atualizados
    is_fechada = data.get('is_pesquisa_fechada', None)
    is_anonima = data.get('is_pesquisa_anonima', None)

    try:
        # Desmarcar todas as outras pesquisas como fechadas/anônimas
        if is_fechada is not None:
            # Desmarca todas as outras pesquisas
            Pesquisa.query.update({Pesquisa.is_pesquisa_fechada: None})
            # Marca a pesquisa atual como fechada
            pesquisa.is_pesquisa_fechada = is_fechada

        if is_anonima is not None:
            # Desmarca todas as outras pesquisas
            Pesquisa.query.update({Pesquisa.is_pesquisa_anonima: None})
            # Marca a pesquisa atual como anônima
            pesquisa.is_pesquisa_anonima = is_anonima

        colaboradores = Colaborador.query.filter(Colaborador.ex_funcionario == False).limit(2).all()
        for colaborador in colaboradores:
            enviar_email(colaborador, pesquisa)

        # Comitar as alterações
        db.session.commit()
        return jsonify(pesquisa.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/colaborador/<int:colaborador_id>/pesquisas-fechadas', methods=['GET'])
def get_pesquisas_fechadas_com_respostas(colaborador_id):
    try:
        # Log para verificar o colaborador_id
        print(f"Colaborador ID recebido: {colaborador_id}")

        # Consulta para obter todas as pesquisas que possuem respostas do colaborador
        pesquisas_fechadas = db.session.query(Pesquisa).join(RespostaFechada).filter(
            RespostaFechada.colaborador_id == colaborador_id
        ).order_by(Pesquisa.ano.desc(), Pesquisa.titulo.asc()).all()

        # Verifica se encontrou pesquisas
        if not pesquisas_fechadas:
            return jsonify([]), 200

        resultado = []
        for pesquisa in pesquisas_fechadas:
            # Log para cada pesquisa respondida encontrada
            print(f"Pesquisa respondida encontrada: {pesquisa.titulo} ({pesquisa.ano})")

            # Obtém as respostas associadas a essa pesquisa para o colaborador
            respostas = RespostaFechada.query.filter_by(
                colaborador_id=colaborador_id,
                pesquisa_id=pesquisa.id
            ).all()

            # Log para verificar se respostas foram encontradas
            if not respostas:
                print(f"Nenhuma resposta encontrada para a pesquisa {pesquisa.titulo} e colaborador {colaborador_id}")

            # Constrói o dicionário de pesquisa
            pesquisa_dict = {
                'id': pesquisa.id,
                'titulo': pesquisa.titulo,
                'ano': pesquisa.ano,
                'descricao': pesquisa.descricao,
                'respostas': [resposta.to_dict() for resposta in respostas]  # Inclui as respostas
            }

            resultado.append(pesquisa_dict)

        # Retorna o resultado final como JSON
        return jsonify(resultado), 200
    except Exception as e:
        # Captura e loga qualquer erro
        print(f"Erro ao obter pesquisas respondidas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/analise-colaborador/<int:colaborador_id>/recarregar-evasao', methods=['GET'])
def recarregar_evasao_colaborador(colaborador_id):
    colaborador = Colaborador.query.get_or_404(colaborador_id)

    # Salvar alterações no colaborador
    db.session.commit()

    # Verificar a análise de evasão do colaborador
    analise = verificar_evasao_colaborador(colaborador.to_dict())

    # Adicionar ou atualizar a análise na sessão
    db.session.add(analise)

    # Commit de todas as alterações
    db.session.commit()
    
    return jsonify({'sucesso': 'Atualizado evasao'}), 200

@bp.route('/analise-colaborador/recarregar-todas-evasoes', methods=['GET'])
def recarregar_evasao_todos_colaboradores():
    # Buscar todos os colaboradores no banco de dados
    colaboradores_ativos = Colaborador.query.filter_by(ex_funcionario=False).all()
    
    # Loop para atualizar a análise de evasão de cada colaborador
    for colaborador in colaboradores_ativos:
        # Verificar a análise de evasão do colaborador
        analise = verificar_evasao_colaborador(colaborador.to_dict())
        
        # Adicionar ou atualizar a análise na sessão
        db.session.add(analise)
    
    # Commit de todas as alterações
    db.session.commit()
    
    return jsonify({'sucesso': 'Análise de evasão atualizada para todos os colaboradores'}), 200
    
@bp.route('/termometro/<int:contexto_id>', methods=['GET'])
def analisar_respostas_por_contexto_especifico(contexto_id):
    try:
        # Obter o termômetro específico
        termometro = Termometro.query.filter_by(contexto_id=contexto_id).first()
        contexto = Contexto.query.filter_by(id=contexto_id).first()

        if not termometro:
            return jsonify({'error': 'Termômetro não encontrado.'}), 404
        
        # Obter perguntas e respostas associadas ao contexto
        respostas = db.session.query(
            Pergunta.texto.label('pergunta_texto'),
            RespostaAnonima.nota.label('nota')
        ).join(
            Pergunta, RespostaAnonima.pergunta_id == Pergunta.id
        ).join(
            PerguntaContexto, PerguntaContexto.pergunta_id == Pergunta.id
        ).filter(
            PerguntaContexto.contexto_id == contexto_id
        ).all()

        # Preparar informações para análise
        perguntas_respostas = "\n".join(
            [f"Pergunta: {resposta.pergunta_texto}, Nota: {resposta.nota}" for resposta in respostas]
        )

        resultado = db.session.query(
            Contexto.id.label('contexto_id'),
            Contexto.nome.label('contexto_nome'),
            func.avg(RespostaAnonima.nota).label('media_nota'),
            func.min(RespostaOpcao.nota).label('min_nota'),
            func.max(RespostaOpcao.nota).label('max_nota'),
            func.count(RespostaAnonima.id).label('total_respostas')
        ).join(
            PerguntaContexto, PerguntaContexto.contexto_id == Contexto.id
        ).outerjoin(
            RespostaAnonima, RespostaAnonima.pergunta_id == PerguntaContexto.pergunta_id
        ).outerjoin(
            RespostaOpcao, RespostaOpcao.pergunta_id == PerguntaContexto.pergunta_id
        ).group_by(
            Contexto.id, Contexto.nome
        ).filter(
            Contexto.id == contexto_id
        ).first()

        print(resultado)

        # Calcular a proximidade_bom e a categoria
        proximidade_bom, status =  categorizar_nota(resultado.media_nota, resultado.min_nota, resultado.max_nota)

        # Atualizar o valor de proximidade_bom no termômetro
        termometro.proximidade_bom = proximidade_bom
        termometro.status = status

        # Gerar análise usando a nova métrica
        analise = analisar(termometro, contexto, perguntas_respostas, resultado.min_nota, resultado.max_nota, resultado.media_nota)

        # Dividir a análise em motivo e sugestões
        if "Sugestões:" in analise:
            motivo, sugestoes = analise.split("Sugestões:")
            motivo = motivo.strip()
            sugestoes = sugestoes.strip()
        else:
            motivo = analise
            sugestoes = "Nenhuma sugestão adicional fornecida."

        # Atualizar o motivo e sugestões no termômetro
        termometro.motivo = motivo
        termometro.sugestao = sugestoes

        db.session.commit()

        return jsonify(termometro.to_dict()), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@bp.route('/termometros', methods=['GET'])
def listar_todos_termometros():
    try:
        # Consulta para obter todos os contextos
        todos_contextos = db.session.query(Contexto).all()

        # Consulta para agrupar respostas por contexto e calcular média das notas
        resultados = db.session.query(
            Contexto.id.label('contexto_id'),
            Contexto.nome.label('contexto_nome'),
            func.avg(RespostaAnonima.nota).label('media_nota'),
            func.min(RespostaOpcao.nota).label('min_nota'),
            func.max(RespostaOpcao.nota).label('max_nota'),
            func.count(RespostaAnonima.id).label('total_respostas')
        ).join(
            PerguntaContexto, PerguntaContexto.contexto_id == Contexto.id
        ).outerjoin(
            RespostaAnonima, RespostaAnonima.pergunta_id == PerguntaContexto.pergunta_id
        ).outerjoin(
            RespostaOpcao, RespostaOpcao.pergunta_id == PerguntaContexto.pergunta_id
        ).group_by(
            Contexto.id, Contexto.nome
        ).all()

        # Cria um dicionário de resultados para facilitar o preenchimento
        resultados_dict = {}
        for resultado in resultados:
            proximidade_bom, status = categorizar_nota(resultado.media_nota, resultado.min_nota, resultado.max_nota) if resultado.media_nota is not None else (None, 'neutro')
            resultados_dict[resultado.contexto_id] = {
                'contexto_id': resultado.contexto_id,
                'contexto_nome': resultado.contexto_nome,
                'proximidade_bom': round(proximidade_bom, 2) if proximidade_bom is not None else None,
                'status': status,
                'total_respostas': resultado.total_respostas,
                'motivo': f'O status para este contexto é {status} com base na média das respostas.'
                if resultado.media_nota is not None else 'Nenhuma resposta disponível para este contexto.'
            }

        # Atualiza ou insere os valores na tabela 'termometro'
        for contexto in todos_contextos:
            if contexto.id in resultados_dict:
                resultado = resultados_dict[contexto.id]
                # Verifica se já existe um termômetro para o contexto
                termometro_existente = Termometro.query.filter_by(contexto_id=contexto.id).first()
                if termometro_existente:
                    # Atualiza os dados do termômetro existente
                    termometro_existente.proximidade_bom = resultado['proximidade_bom']
                    termometro_existente.status = resultado['status']
                else:
                    # Cria um novo termômetro para o contexto
                    novo_termometro = Termometro(
                        contexto_id=contexto.id,
                        proximidade_bom=resultado['proximidade_bom'],
                        motivo=resultado['motivo'],
                        status=resultado['status']
                    )
                    db.session.add(novo_termometro)
            else:
                # Contextos sem respostas são adicionados como 'neutro' no termômetro
                termometro_existente = Termometro.query.filter_by(contexto_id=contexto.id).first()
                if termometro_existente:
                    # Atualiza para 'neutro' se necessário
                    if termometro_existente.status != 'neutro':
                        termometro_existente.proximidade_bom = None
                        termometro_existente.motivo = 'Nenhuma resposta disponível para este contexto.'
                        termometro_existente.status = 'neutro'
                else:
                    # Cria um novo termômetro para contextos que não existem na tabela
                    novo_termometro = Termometro(
                        contexto_id=contexto.id,
                        proximidade_bom=None,
                        motivo='Nenhuma resposta disponível para este contexto.',
                        status='neutro'
                    )
                    db.session.add(novo_termometro)

        # Commit das alterações no banco de dados
        db.session.commit()

        # Retorna todos os termômetros atualizados
        termometros_atualizados = Termometro.query.all()
        termometros_response = [termometro.to_dict() for termometro in termometros_atualizados]

        return jsonify(termometros_response), 200

    except Exception as e:
        db.session.rollback()  # Reverter alterações em caso de erro
        return jsonify({'error': str(e)}), 500
