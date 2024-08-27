from flask import Blueprint, jsonify, request
from .models import Cargo, Departamento, EstadoCivil, Faculdade, FaixaSalarial, Formacao, Genero, NivelEscolaridade, Setor, db, Colaborador, AnaliseColaborador

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