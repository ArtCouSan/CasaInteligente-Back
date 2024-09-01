from flask import Blueprint, Response, jsonify, request
from pymysql import IntegrityError

from app.serivces.upload_colaborador_service import processar_csv
from .models import Cargo, Departamento, EstadoCivil, Faculdade, FaixaSalarial, Formacao, Genero, NivelEscolaridade, Pergunta, Resposta, Setor, db, Colaborador, AnaliseColaborador
from bson import ObjectId
from . import mongo 
from app.chat.chat_service import fazer_pergunta, gerar_contexto_colaborador, gerar_nova_sugestao_ia, gerar_novo_motivo_ia
from flask import send_file

bp = Blueprint('colaborador', __name__)

@bp.route('/colaboradores', methods=['GET'])
def get_colaboradores():
    colaboradores = Colaborador.query.all()
    return jsonify([colaborador.to_dict() for colaborador in colaboradores])

@bp.route('/colaborador/<int:id>', methods=['GET'])
def get_colaborador(id):
    colaborador = Colaborador.query.get_or_404(id)
    return jsonify(colaborador.to_dict())

@bp.route('/colaborador', methods=['POST'])
def create_colaborador():
    data = request.get_json()
    colaborador = Colaborador(
        nome=data.get('nome'),
        cpf=data.get('cpf'),
        idade=data.get('idade'),
        genero_id=data.get('genero')['id'],
        estado_civil_id=data.get('estadoCivil')['id'],
        telefone=data.get('telefone'),
        email=data.get('email'),
        formacao_id=data.get('formacao')['id'],
        faculdade_id=data.get('faculdade')['id'],
        endereco=data.get('endereco'),
        numero=data.get('numero'),
        complemento=data.get('complemento'),
        bairro=data.get('bairro'),
        cidade=data.get('cidade'),
        estado=data.get('estado'),
        cep=data.get('cep'),
        departamento_id=data.get('departamento')['id'],
        setor_id=data.get('setor')['id'],
        faixa_salarial_id=data.get('faixaSalarial')['id'],
        cargo_id=data.get('cargo')['id'],
        gerente=data.get('gerente'),
        tempo_trabalho=data.get('tempoTrabalho'),
        quantidade_empresas_trabalhou=data.get('quantidadeEmpresasTrabalhou'),
        quantidade_anos_trabalhados_anteriormente=data.get('quantidadeAnosTrabalhadosAnteriormente'),
        nivel_escolaridade_id=data.get('nivelEscolaridade')['id'],
        ex_funcionario=data.get('exFuncionario'),
    )
    db.session.add(colaborador)
    db.session.commit()
    return jsonify(colaborador.to_dict()), 201

@bp.route('/colaborador/<int:id>', methods=['PUT'])
def update_colaborador(id):
    colaborador = Colaborador.query.get_or_404(id)
    data = request.get_json()

    colaborador.nome = data.get('nome', colaborador.nome)
    colaborador.cpf = data.get('cpf', colaborador.cpf)
    colaborador.idade = data.get('idade', colaborador.idade)
    colaborador.genero_id = data.get('genero')['id']
    colaborador.estado_civil_id = data.get('estadoCivil')['id']
    colaborador.telefone = data.get('telefone', colaborador.telefone)
    colaborador.email = data.get('email', colaborador.email)
    colaborador.formacao_id = data.get('formacao')['id']
    colaborador.faculdade_id = data.get('faculdade')['id']
    colaborador.endereco = data.get('endereco', colaborador.endereco)
    colaborador.numero = data.get('numero', colaborador.numero)
    colaborador.complemento = data.get('complemento', colaborador.complemento)
    colaborador.bairro = data.get('bairro', colaborador.bairro)
    colaborador.cidade = data.get('cidade', colaborador.cidade)
    colaborador.estado = data.get('estado', colaborador.estado)
    colaborador.cep = data.get('cep', colaborador.cep)
    colaborador.departamento_id = data.get('departamento')['id']
    colaborador.setor_id = data.get('setor')['id']
    colaborador.faixa_salarial_id = data.get('faixaSalarial')['id']
    colaborador.cargo_id = data.get('cargo')['id']
    colaborador.gerente = data.get('gerente', colaborador.gerente)
    colaborador.tempo_trabalho = data.get('tempoTrabalho', colaborador.tempo_trabalho)
    colaborador.quantidade_empresas_trabalhou = data.get('quantidadeEmpresasTrabalhou', colaborador.quantidade_empresas_trabalhou)
    colaborador.quantidade_anos_trabalhados_anteriormente = data.get('quantidadeAnosTrabalhadosAnteriormente', colaborador.quantidade_anos_trabalhados_anteriormente)
    colaborador.nivel_escolaridade_id = data.get('nivelEscolaridade')['id']
    colaborador.ex_funcionario = data.get('exFuncionario', colaborador.ex_funcionario)

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
    analises = AnaliseColaborador.query.all()
    return jsonify([analise.to_dict() for analise in analises])

@bp.route('/analise-colaborador/<int:id>', methods=['GET'])
def get_analise_colaborador(id):
    analise = AnaliseColaborador.query.get_or_404(id)
    return jsonify(analise.to_dict())

@bp.route('/analise-colaborador', methods=['POST'])
def create_analise_colaborador():
    data = request.get_json()
    colaborador_id = data['colaborador']['id']
    colaborador = Colaborador.query.get_or_404(colaborador_id)

    analise = AnaliseColaborador(
        colaborador_id=colaborador.id,
        predicao=data['predicao'],
        motivo=data['motivo'],
        sugestao=data['sugestao'],
        observacao=data.get('observacao', '')
    )

    db.session.add(analise)
    db.session.commit()
    return jsonify(analise.to_dict()), 201

@bp.route('/analise-colaborador/<int:id>', methods=['PUT'])
def update_analise_colaborador(id):
    analise = AnaliseColaborador.query.get_or_404(id)
    data = request.get_json()

    analise.predicao = data.get('predicao', analise.predicao)
    analise.motivo = data.get('motivo', analise.motivo)
    analise.sugestao = data.get('sugestao', analise.sugestao)
    analise.observacao = data.get('observacao', analise.observacao)

    db.session.commit()
    return jsonify(analise.to_dict())

@bp.route('/analise-colaborador/<int:id>', methods=['DELETE'])
def delete_analise_colaborador(id):
    analise = AnaliseColaborador.query.get_or_404(id)
    db.session.delete(analise)
    db.session.commit()
    return jsonify({'message': 'Análise excluída com sucesso!'}), 200

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

@bp.route('/setores', methods=['GET'])
def listar_setores():
    setores = Setor.query.all()
    return jsonify([setor.to_dict() for setor in setores])

@bp.route('/cargos', methods=['GET'])
def listar_cargos():
    cargos = Cargo.query.all()
    return jsonify([cargo.to_dict() for cargo in cargos])

@bp.route('/faixas-salariais', methods=['GET'])
def listar_faixas_salariais():
    faixas_salariais = FaixaSalarial.query.all()
    return jsonify([faixa_salarial.to_dict() for faixa_salarial in faixas_salariais])

# Rota para listar todas as perguntas
@bp.route('/perguntas', methods=['GET'])
def get_perguntas():
    perguntas = Pergunta.query.all()
    return jsonify([pergunta.to_dict(include_respostas=False) for pergunta in perguntas])

# Rota para adicionar uma nova pergunta
@bp.route('/pergunta', methods=['POST'])
def create_pergunta():
    data = request.get_json()
    pergunta = Pergunta(
        texto=data.get('texto')
    )
    db.session.add(pergunta)
    db.session.commit()
    return jsonify(pergunta.to_dict()), 201

# Rota para listar todas as respostas de um colaborador
@bp.route('/colaborador/<int:colaborador_id>/respostas', methods=['GET'])
def get_respostas(colaborador_id):
    respostas = Resposta.query.filter_by(colaborador_id=colaborador_id).all()
    return jsonify([resposta.to_dict() for resposta in respostas])

# Rota para adicionar uma resposta de um colaborador a uma pergunta
@bp.route('/colaborador/<int:colaborador_id>/resposta', methods=['POST'])
def create_or_update_resposta(colaborador_id):
    data = request.get_json()

    # Tente encontrar uma resposta existente com a mesma combinação de colaborador, pergunta, trimestre e ano
    resposta_existente = Resposta.query.filter_by(
        colaborador_id=colaborador_id,
        pergunta_id=data['pergunta_id'],
        trimestre=data['trimestre'],
        ano=data['ano']
    ).first()

    if resposta_existente:
        # Se a resposta existir, atualize a nota
        resposta_existente.nota = data['nota']
        db.session.commit()
        return jsonify(resposta_existente.to_dict()), 200
    else:
        try:
            # Se não existir, crie uma nova resposta
            nova_resposta = Resposta(
                colaborador_id=colaborador_id,
                pergunta_id=data['pergunta_id'],
                nota=data['nota'],
                trimestre=data['trimestre'],
                ano=data['ano']
            )
            db.session.add(nova_resposta)
            db.session.commit()
            return jsonify(nova_resposta.to_dict()), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "Erro ao tentar criar a resposta."}), 400

# Rota para atualizar uma resposta existente
@bp.route('/resposta/<int:id>', methods=['PUT'])
def update_resposta(id):
    resposta = Resposta.query.get_or_404(id)
    data = request.get_json()

    resposta.nota = data.get('nota', resposta.nota)
    resposta.trimestre = data.get('trimestre', resposta.trimestre)
    resposta.ano = data.get('ano', resposta.ano)

    db.session.commit()
    return jsonify(resposta.to_dict())

# Rota para deletar uma resposta
@bp.route('/resposta/<int:id>', methods=['DELETE'])
def delete_resposta(id):
    resposta = Resposta.query.get_or_404(id)
    db.session.delete(resposta)
    db.session.commit()
    return jsonify({'message': 'Resposta excluída com sucesso!'}), 200

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
    
@bp.route('/download-template', methods=['GET'])
def download_template():
    filepath = '../app/templates/colaborador.csv'

    with open(filepath, 'r', encoding='utf-8') as file:
        data = file.read()

    response = Response(
        data,
        mimetype='text/csv; charset=utf-8',
        headers={"Content-disposition": "attachment; filename=template_colaboradores.csv"}
    )