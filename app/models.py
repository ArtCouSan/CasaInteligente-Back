from . import db

# Genero Table
class Genero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

# Estado Civil Table
class EstadoCivil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

# Formacao Table
class Formacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

# Faculdade Table
class Faculdade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

# Departamento Table
class Departamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

# Setor Table
class Setor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

# Faixa Salarial Table
class FaixaSalarial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

# Nivel Escolaridade Table
class NivelEscolaridade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }

# Cargo Table
class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

# Colaborador Table
class Colaborador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), default='')
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    idade = db.Column(db.Integer, default=0)
    genero_id = db.Column(db.Integer, db.ForeignKey('genero.id'), nullable=True)
    estado_civil_id = db.Column(db.Integer, db.ForeignKey('estado_civil.id'), nullable=True)
    telefone = db.Column(db.String(20), default='')
    email = db.Column(db.String(255), default='')
    senha_hash = db.Column(db.String(255), nullable=False)
    formacao_id = db.Column(db.Integer, db.ForeignKey('formacao.id'), nullable=True)
    faculdade_id = db.Column(db.Integer, db.ForeignKey('faculdade.id'), nullable=True)
    endereco = db.Column(db.String(255), default='')
    numero = db.Column(db.String(10), default='')
    complemento = db.Column(db.String(255), default='')
    bairro = db.Column(db.String(100), default='')
    cidade = db.Column(db.String(100), default='')
    estado = db.Column(db.String(50), default='')
    cep = db.Column(db.String(20), default='')
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=True)
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=True)
    faixa_salarial_id = db.Column(db.Integer, db.ForeignKey('faixa_salarial.id'), nullable=True)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=True)
    gerente = db.Column(db.String(100), default='')
    tempo_trabalho = db.Column(db.String(50), default='')
    quantidade_empresas_trabalhou = db.Column(db.Integer, default=0)
    quantidade_anos_trabalhados_anteriormente = db.Column(db.Integer, default=0)
    nivel_escolaridade_id = db.Column(db.Integer, db.ForeignKey('nivel_escolaridade.id'), nullable=True)
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
    respostas_colaborador = db.relationship("Resposta", back_populates="colaborador", cascade="all, delete-orphan")
    perfis = db.relationship('Perfil', secondary='colaborador_perfil', backref='colaboradores')

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
            'endereco': self.endereco,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'formacao': {'id': self.formacao.id, 'descricao': self.formacao.descricao},
            'faculdade': {'id': self.faculdade.id, 'nome': self.faculdade.nome},
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
            'perfis': [perfil.to_dict() for perfil in self.perfis],
            'respostas': [resposta.to_dict() for resposta in self.respostas_colaborador]  # Inclui as respostas associadas
        }
    
    def to_dict_somente_dados(self):
        return {
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
            'respostas': [resposta.to_dict() for resposta in self.respostas] 
        }

# Perfil Table
class Perfil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

# Tabela de relacionamento entre Colaborador e Perfil
class ColaboradorPerfil(db.Model):
    __tablename__ = 'colaborador_perfil'
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaborador.id'), primary_key=True)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfil.id'), primary_key=True)

# Pesquisa Table
class Pesquisa(db.Model):
    __tablename__ = 'pesquisa'
    id = db.Column(db.Integer, primary_key=True, index=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, default='')
    ano = db.Column(db.Integer, nullable=False)

    respostas_pesquisa = db.relationship("Resposta", back_populates="pesquisa", cascade="all, delete-orphan")

# Pergunta Table
class Pergunta(db.Model):
    __tablename__ = 'pergunta'
    id = db.Column(db.Integer, primary_key=True, index=True)
    texto = db.Column(db.String(255), nullable=False)

    respostas_pergunta = db.relationship("RespostaOpcao", backref="pergunta", cascade="all, delete-orphan")

    def to_dict(self, include_respostas=False):
        data = {
            'id': self.id,
            'texto': self.texto,
        }
        if include_respostas:
            data['opcoes_resposta'] = [resposta.to_dict() for resposta in self.respostas_pergunta]
        return data

# RespostaOpcao Table
class RespostaOpcao(db.Model):
    __tablename__ = 'resposta_opcao'
    id = db.Column(db.Integer, primary_key=True, index=True)
    texto = db.Column(db.String(255), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('pergunta.id', ondelete='CASCADE'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'texto': self.texto,
            'nota': self.nota
        }

# Resposta Table
class Resposta(db.Model):
    __tablename__ = 'resposta'
    id = db.Column(db.Integer, primary_key=True, index=True)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaborador.id', ondelete='CASCADE'), nullable=False)
    pesquisa_id = db.Column(db.Integer, db.ForeignKey('pesquisa.id', ondelete='CASCADE'), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('pergunta.id', ondelete='CASCADE'), nullable=False)
    nota = db.Column(db.Integer, nullable=False)

    colaborador = db.relationship("Colaborador", back_populates="respostas_colaborador")
    pergunta = db.relationship("Pergunta", backref="respostas")
    pesquisa = db.relationship("Pesquisa", back_populates="respostas_pesquisa")

    def to_dict(self):
        return {
            'id': self.id,
            'colaborador_id': self.colaborador_id,
            'pesquisa_id': self.pesquisa_id,
            'pergunta_id': self.pergunta_id,
            'nota': self.nota
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
    
    def to_dict_predicao(self):
        return {
            'motivo': self.motivo,
            'predicao': self.predicao,
            'sugestao': self.sugestao,
            'observacao': self.observacao
        }