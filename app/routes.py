from flask import Blueprint, jsonify, request, session
from pymysql import IntegrityError 
from app.serivces.upload_colaborador_service import processar_csv
from .models import Cargo, Departamento, EstadoCivil, Faculdade, FaixaSalarial, Formacao, Genero, NivelEscolaridade, Pergunta, Pesquisa, PesquisaPergunta, Resposta, RespostaOpcao, Setor, db, Colaborador, AnaliseColaborador
from bson import ObjectId
from . import mongo 
from app.chat.ia_service import fazer_pergunta, gerar_contexto_colaborador, gerar_nova_sugestao_ia, gerar_novo_motivo_ia
from flask import send_file
import os

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
        faixa_salarial_id=data.get('faixaSalarial', {}).get('id', 1),
        cargo_id=data.get('cargo', {}).get('id', 1),
        gerente=data.get('gerente', ''),
        tempo_trabalho=data.get('tempoTrabalho', ''),
        quantidade_empresas_trabalhou=data.get('quantidadeEmpresasTrabalhou', 0),
        quantidade_anos_trabalhados_anteriormente=data.get('quantidadeAnosTrabalhadosAnteriormente', 0),
        nivel_escolaridade_id=data.get('nivelEscolaridade', {}).get('id', 1),
        ex_funcionario=data.get('exFuncionario', False),
        senha_hash=123
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
    colaborador.faixa_salarial_id = data.get('faixaSalarial', {}).get('id', colaborador.faixa_salarial_id or 1)
    colaborador.cargo_id = data.get('cargo', {}).get('id', colaborador.cargo_id or 1)
    colaborador.gerente = data.get('gerente', colaborador.gerente)
    colaborador.tempo_trabalho = data.get('tempoTrabalho', colaborador.tempo_trabalho)
    colaborador.quantidade_empresas_trabalhou = data.get('quantidadeEmpresasTrabalhou', colaborador.quantidade_empresas_trabalhou)
    colaborador.quantidade_anos_trabalhados_anteriormente = data.get('quantidadeAnosTrabalhadosAnteriormente', colaborador.quantidade_anos_trabalhados_anteriormente)
    colaborador.nivel_escolaridade_id = data.get('nivelEscolaridade', {}).get('id', colaborador.nivel_escolaridade_id or 1)
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

    print(opcoes_resposta)
    
    for opcao in opcoes_resposta:
        resposta_opcao = RespostaOpcao(
            texto=opcao.get('texto'),
            nota=opcao.get('nota'),
            pergunta_id=pergunta.id
        )
        db.session.add(resposta_opcao)

    db.session.commit()

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

    return jsonify(pergunta.to_dict(include_respostas=True))

# Rota para deletar uma pergunta
@bp.route('/pergunta/<int:id>', methods=['DELETE'])
def delete_pergunta(id):
    pergunta = Pergunta.query.get_or_404(id)
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

# Rota para listar todas as respostas de um colaborador
@bp.route('/colaborador/<int:colaborador_id>/respostas', methods=['GET'])
def get_respostas(colaborador_id):
    respostas = Resposta.query.filter_by(colaborador_id=colaborador_id).all()
    return jsonify([resposta.to_dict() for resposta in respostas])

# Rota para adicionar ou atualizar uma resposta de um colaborador a uma pergunta
@bp.route('/colaborador/<int:colaborador_id>/resposta', methods=['POST'])
def create_or_update_resposta(colaborador_id):
    data = request.get_json()

    try:
        # Tente encontrar uma resposta existente com a mesma combinação de colaborador, pergunta, trimestre e ano
        resposta_existente = Resposta.query.filter_by(
            colaborador_id=colaborador_id,
            pergunta_id=data['pergunta_id']
        ).first()

        if resposta_existente:
            # Se a resposta existir, atualize a nota e qualquer outro campo necessário
            resposta_existente.nota = data['nota']

            # Verifica se a resposta deve ser marcada como fechada ou anônima
            if 'is_pesquisa_fechada' in data:
                resposta_existente.is_pesquisa_fechada = data['is_pesquisa_fechada']
            if 'is_pesquisa_anonima' in data:
                resposta_existente.is_pesquisa_anonima = data['is_pesquisa_anonima']

            db.session.commit()
            return jsonify(resposta_existente.to_dict()), 200
        else:
            # Se não existir, crie uma nova resposta
            nova_resposta = Resposta(
                colaborador_id=colaborador_id,
                pergunta_id=data['pergunta_id'],
                pesquisa_id=data['pesquisa_id'],
                nota=data['nota'],
                is_pesquisa_fechada=data.get('is_pesquisa_fechada', None),  # Define como None se não fornecido
                is_pesquisa_anonima=data.get('is_pesquisa_anonima', None)   # Define como None se não fornecido
            )
            db.session.add(nova_resposta)
            db.session.commit()
            return jsonify(nova_resposta.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Erro ao tentar criar ou atualizar a resposta."}), 400

@bp.route('/resposta/<int:id>', methods=['PUT'])
def update_resposta(id):
    resposta = Resposta.query.get_or_404(id)
    data = request.get_json()

    # Atualiza os campos fornecidos no corpo da requisição
    resposta.nota = data.get('nota', resposta.nota)
    resposta.is_pesquisa_fechada = data.get('is_pesquisa_fechada', resposta.is_pesquisa_fechada)
    resposta.is_pesquisa_anonima = data.get('is_pesquisa_anonima', resposta.is_pesquisa_anonima)

    # Salva a data e hora automaticamente (já configurado no modelo)
    db.session.commit()
    return jsonify(resposta.to_dict()), 200

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
    # Ajusta o caminho para ser absoluto
    filepath = os.path.abspath(os.path.join('app', 'templates', 'colaborador.csv'))
    
    # Verifica se o arquivo existe
    if not os.path.exists(filepath):
        return {"error": "Template file not found"}, 404
    
    # Retorna o arquivo para download
    return send_file(filepath, as_attachment=True, download_name='colaborador.csv', mimetype='text/csv')

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

    print(perfis_data)

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

# Rota para listar todas as respostas de uma pesquisa específica
@bp.route('/pesquisa/<int:pesquisa_id>/respostas', methods=['GET'])
def get_respostas_by_pesquisa(pesquisa_id):
    respostas = Resposta.query.filter_by(pesquisa_id=pesquisa_id).all()
    return jsonify([resposta.to_dict() for resposta in respostas])

# Rota para adicionar uma resposta de um colaborador a uma pergunta em uma pesquisa
@bp.route('/pesquisa/<int:pesquisa_id>/colaborador/<int:colaborador_id>/resposta', methods=['POST'])
def create_or_update_resposta_by_pesquisa(pesquisa_id, colaborador_id):
    data = request.get_json()
    
    # Procura por uma resposta existente
    resposta_existente = Resposta.query.filter_by(
        colaborador_id=colaborador_id,
        pergunta_id=data['pergunta_id'],
        pesquisa_id=pesquisa_id
    ).first()

    if resposta_existente:
        resposta_existente.nota = data['nota']  # Atualiza a nota se a resposta existir
    else:
        nova_resposta = Resposta(
            colaborador_id=colaborador_id,
            pergunta_id=data['pergunta_id'],
            pesquisa_id=pesquisa_id,  # Associar a pesquisa
            nota=data['nota'],
            trimestre=data['trimestre'],
            ano=data['ano']
        )
        db.session.add(nova_resposta)

    try:
        db.session.commit()
        return jsonify(nova_resposta.to_dict() if nova_resposta else resposta_existente.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro ao salvar resposta'}), 400
    
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

        # Comitar as alterações
        db.session.commit()
        return jsonify(pesquisa.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
