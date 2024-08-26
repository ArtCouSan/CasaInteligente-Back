from flask import Blueprint, jsonify, request, abort
from .models import db, Colaborador

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
        genero_id=data.get('genero_id'),
        estado_civil_id=data.get('estado_civil_id'),
        telefone=data.get('telefone'),
        email=data.get('email'),
        formacao_id=data.get('formacao_id'),
        faculdade_id=data.get('faculdade_id'),
        endereco=data.get('endereco'),
        numero=data.get('numero'),
        complemento=data.get('complemento'),
        bairro=data.get('bairro'),
        cidade=data.get('cidade'),
        estado=data.get('estado'),
        cep=data.get('cep'),
        departamento_id=data.get('departamento_id'),
        setor_id=data.get('setor_id'),
        faixa_salarial_id=data.get('faixa_salarial_id'),
        cargo_id=data.get('cargo_id'),
        gerente=data.get('gerente'),
        tempo_trabalho=data.get('tempo_trabalho'),
        quantidade_empresas_trabalhou=data.get('quantidade_empresas_trabalhou'),
        quantidade_anos_trabalhados_anteriormente=data.get('quantidade_anos_trabalhados_anteriormente'),
        nivel_escolaridade_id=data.get('nivel_escolaridade_id'),
        acoes=data.get('acoes')
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
    colaborador.genero_id = data.get('genero_id', colaborador.genero_id)
    colaborador.estado_civil_id = data.get('estado_civil_id', colaborador.estado_civil_id)
    colaborador.telefone = data.get('telefone', colaborador.telefone)
    colaborador.email = data.get('email', colaborador.email)
    colaborador.formacao_id = data.get('formacao_id', colaborador.formacao_id)
    colaborador.faculdade_id = data.get('faculdade_id', colaborador.faculdade_id)
    colaborador.endereco = data.get('endereco', colaborador.endereco)
    colaborador.numero = data.get('numero', colaborador.numero)
    colaborador.complemento = data.get('complemento', colaborador.complemento)
    colaborador.bairro = data.get('bairro', colaborador.bairro)
    colaborador.cidade = data.get('cidade', colaborador.cidade)
    colaborador.estado = data.get('estado', colaborador.estado)
    colaborador.cep = data.get('cep', colaborador.cep)
    colaborador.departamento_id = data.get('departamento_id', colaborador.departamento_id)
    colaborador.setor_id = data.get('setor_id', colaborador.setor_id)
    colaborador.faixa_salarial_id = data.get('faixa_salarial_id', colaborador.faixa_salarial_id)
    colaborador.cargo_id = data.get('cargo_id', colaborador.cargo_id)
    colaborador.gerente_id = data.get('gerente', colaborador.gerente)
    colaborador.tempo_trabalho = data.get('tempo_trabalho', colaborador.tempo_trabalho)
    colaborador.quantidade_empresas_trabalhou = data.get('quantidade_empresas_trabalhou', colaborador.quantidade_empresas_trabalhou)
    colaborador.quantidade_anos_trabalhados_anteriormente = data.get('quantidade_anos_trabalhados_anteriormente', colaborador.quantidade_anos_trabalhados_anteriormente)
    colaborador.nivel_escolaridade_id = data.get('nivel_escolaridade_id', colaborador.nivel_escolaridade_id)
    colaborador.acoes = data.get('acoes', colaborador.acoes)

    db.session.commit()
    return jsonify(colaborador.to_dict())

@bp.route('/colaborador/<int:id>', methods=['DELETE'])
def delete_colaborador(id):
    colaborador = Colaborador.query.get_or_404(id)
    db.session.delete(colaborador)
    db.session.commit()
    return jsonify({'message': 'Colaborador excluído com sucesso!'}), 200
