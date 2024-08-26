from . import db

class Genero(db.Model):
    __tablename__ = 'genero'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

class EstadoCivil(db.Model):
    __tablename__ = 'estado_civil'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

class Formacao(db.Model):
    __tablename__ = 'formacao'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)

class Faculdade(db.Model):
    __tablename__ = 'faculdade'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)

class Departamento(db.Model):
    __tablename__ = 'departamento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Setor(db.Model):
    __tablename__ = 'setor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class FaixaSalarial(db.Model):
    __tablename__ = 'faixa_salarial'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

class NivelEscolaridade(db.Model):
    __tablename__ = 'nivel_escolaridade'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

class Cargo(db.Model):
    __tablename__ = 'cargo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Colaborador(db.Model):
    __tablename__ = 'colaborador'
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
    acoes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'idade': self.idade,
            'genero_id': self.genero_id,
            'estado_civil_id': self.estado_civil_id,
            'telefone': self.telefone,
            'email': self.email,
            'formacao_id': self.formacao_id,
            'faculdade_id': self.faculdade_id,
            'endereco': self.endereco,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'departamento_id': self.departamento_id,
            'setor_id': self.setor_id,
            'faixa_salarial_id': self.faixa_salarial_id,
            'cargo_id': self.cargo_id,
            'gerente': self.gerente,
            'tempo_trabalho': self.tempo_trabalho,
            'quantidade_empresas_trabalhou': self.quantidade_empresas_trabalhou,
            'quantidade_anos_trabalhados_anteriormente': self.quantidade_anos_trabalhados_anteriormente,
            'nivel_escolaridade_id': self.nivel_escolaridade_id,
            'acoes': self.acoes
        }
    
class ColaboradorPredicao(db.Model):
    __tablename__ = 'colaborador_predicao'
    id = db.Column(db.Integer, primary_key=True)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaborador.id', ondelete='CASCADE'))
    predicao = db.Column(db.Integer)
    motivo = db.Column(db.Text)
    sugestao = db.Column(db.Text)
    observacao = db.Column(db.Text)
