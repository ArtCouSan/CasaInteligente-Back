from . import db

class Genero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

class EstadoCivil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

class Formacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

class Faculdade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

class Departamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

class Setor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

class FaixaSalarial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

class NivelEscolaridade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

class Colaborador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    idade = db.Column(db.Integer, nullable=False)
    genero_id = db.Column(db.Integer, db.ForeignKey('genero.id'))
    estado_civil_id = db.Column(db.Integer, db.ForeignKey('estado_civil.id'))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    formacao_id = db.Column(db.Integer, db.ForeignKey('formacao.id'))
    faculdade_id = db.Column(db.Integer, db.ForeignKey('faculdade.id'))
    endereco = db.Column(db.String(255), nullable=False)
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(255))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(50))
    cep = db.Column(db.String(20))
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'))
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'))
    faixa_salarial_id = db.Column(db.Integer, db.ForeignKey('faixa_salarial.id'))
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo.id'))
    gerente = db.Column(db.String(100))
    tempo_trabalho = db.Column(db.String(50))
    quantidade_empresas_trabalhou = db.Column(db.Integer)
    quantidade_anos_trabalhados_anteriormente = db.Column(db.Integer)
    nivel_escolaridade_id = db.Column(db.Integer, db.ForeignKey('nivel_escolaridade.id'))
    ex_funcionario = db.Column(db.Boolean, default=False)

    genero = db.relationship('Genero', backref='colaboradores')
    estado_civil = db.relationship('EstadoCivil', backref='colaboradores')
    formacao = db.relationship('Formacao', backref='colaboradores')
    faculdade = db.relationship('Faculdade', backref='colaboradores')
    departamento = db.relationship('Departamento', backref='colaboradores')
    setor = db.relationship('Setor', backref='colaboradores')
    faixa_salarial = db.relationship('FaixaSalarial', backref='colaboradores')
    cargo = db.relationship('Cargo', backref='colaboradores')
    nivel_escolaridade = db.relationship('NivelEscolaridade', backref='colaboradores')
    respostas = db.relationship("Resposta", back_populates="colaborador")  # Relação bidirecional

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'idade': self.idade,
            'genero': {'id': self.genero.id, 'descricao': self.genero.descricao},
            'estadoCivil': {'id': self.estado_civil.id, 'descricao': self.estado_civil.descricao},
            'telefone': self.telefone,
            'email': self.email,
            'formacao': {'id': self.formacao.id, 'descricao': self.formacao.descricao},
            'faculdade': {'id': self.faculdade.id, 'nome': self.faculdade.nome},
            'endereco': self.endereco,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'departamento': {'id': self.departamento.id, 'nome': self.departamento.nome},
            'setor': {'id': self.setor.id, 'nome': self.setor.nome},
            'faixaSalarial': {'id': self.faixa_salarial.id, 'descricao': self.faixa_salarial.descricao},
            'cargo': {'id': self.cargo.id, 'nome': self.cargo.nome},
            'gerente': self.gerente,
            'tempoTrabalho': self.tempo_trabalho,
            'quantidadeEmpresasTrabalhou': self.quantidade_empresas_trabalhou,
            'quantidadeAnosTrabalhadosAnteriormente': self.quantidade_anos_trabalhados_anteriormente,
            'nivelEscolaridade': {'id': self.nivel_escolaridade.id, 'descricao': self.nivel_escolaridade.descricao},
            'exFuncionario': self.ex_funcionario,
            'respostas': [resposta.to_dict() for resposta in self.respostas]  # Inclui as respostas relacionadas
        }

class AnaliseColaborador(db.Model):
    __tablename__ = 'colaborador_predicao'
    id = db.Column(db.Integer, primary_key=True)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaborador.id'), nullable=False)
    predicao = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    sugestao = db.Column(db.Text, nullable=False)
    observacao = db.Column(db.Text, nullable=True)

    colaborador = db.relationship('Colaborador', backref='analises', lazy=True)

    def to_dict(self):
        return {
            'colaborador': self.colaborador.to_dict(),
            'motivo': self.motivo,
            'predicao': self.predicao,
            'sugestao': self.sugestao,
            'observacao': self.observacao
        }
    
class Pergunta(db.Model):
    __tablename__ = 'pergunta'
    id = db.Column(db.Integer, primary_key=True, index=True)
    texto = db.Column(db.String(255), nullable=False)

    respostas = db.relationship("Resposta", back_populates="pergunta")

    def to_dict(self, include_respostas=False):
        data = {
            'id': self.id,
            'texto': self.texto,
        }
        if include_respostas:
            data['respostas'] = [resposta.to_dict() for resposta in self.respostas]
        return data

class Resposta(db.Model):
    __tablename__ = 'resposta'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaborador.id'), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('pergunta.id'), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    trimestre = db.Column(db.Enum('Q1', 'Q2', 'Q3', 'Q4'), nullable=False)
    ano = db.Column(db.Integer, nullable=False)

    colaborador = db.relationship("Colaborador", back_populates="respostas")
    pergunta = db.relationship("Pergunta", back_populates="respostas")

    def to_dict(self):
        return {
            'id': self.id,
            'colaborador_id': self.colaborador_id,
            'pergunta_id': self.pergunta_id,
            'nota': self.nota,
            'trimestre': self.trimestre,
            'ano': self.ano,
            'pergunta_texto': self.pergunta.texto if self.pergunta else None
        }