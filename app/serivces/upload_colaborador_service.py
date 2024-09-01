import pandas as pd
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Cargo, Colaborador, Departamento, EstadoCivil, Faculdade, FaixaSalarial, Formacao, Genero, NivelEscolaridade, Setor

UPLOAD_FOLDER = 'uploads/'

# Configurar o diretório de uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def processar_csv(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Processar o CSV com pandas
    try:
        df = pd.read_csv(filepath)
        
        # Preencher valores nulos com uma string vazia ou um valor padrão
        df.fillna('', inplace=True)
        
        for index, row in df.iterrows():
            # Recuperar ou criar as referências de FK
            genero = Genero.query.filter_by(descricao=row['genero']).first() or Genero(descricao=row['genero'])
            estado_civil = EstadoCivil.query.filter_by(descricao=row['estadoCivil']).first() or EstadoCivil(descricao=row['estadoCivil'])
            formacao = Formacao.query.filter_by(descricao=row['formacao']).first() or Formacao(descricao=row['formacao'])
            faculdade = Faculdade.query.filter_by(nome=row['faculdade']).first() or Faculdade(nome=row['faculdade'])
            departamento = Departamento.query.filter_by(nome=row['departamento']).first() or Departamento(nome=row['departamento'])
            setor = Setor.query.filter_by(nome=row['setor']).first() or Setor(nome=row['setor'])
            faixa_salarial = FaixaSalarial.query.filter_by(descricao=row['faixaSalarial']).first() or FaixaSalarial(descricao=row['faixaSalarial'])
            cargo = Cargo.query.filter_by(nome=row['cargo']).first() or Cargo(nome=row['cargo'])
            nivel_escolaridade = NivelEscolaridade.query.filter_by(descricao=row['nivelEscolaridade']).first() or NivelEscolaridade(descricao=row['nivelEscolaridade'])

            # Adicionar os novos objetos ao banco de dados se não existirem
            if genero.id is None:
                db.session.add(genero)
            if estado_civil.id is None:
                db.session.add(estado_civil)
            if formacao.id is None:
                db.session.add(formacao)
            if faculdade.id is None:
                db.session.add(faculdade)
            if departamento.id is None:
                db.session.add(departamento)
            if setor.id is None:
                db.session.add(setor)
            if faixa_salarial.id is None:
                db.session.add(faixa_salarial)
            if cargo.id is None:
                db.session.add(cargo)
            if nivel_escolaridade.id is None:
                db.session.add(nivel_escolaridade)

            # Cria ou atualiza o colaborador
            colaborador = Colaborador(
                nome=row['nome'],
                cpf=row['cpf'],
                idade=row['idade'],
                genero=genero,
                estado_civil=estado_civil,
                telefone=row['telefone'],
                email=row['email'],
                formacao=formacao,
                faculdade=faculdade,
                endereco=row['endereco'],
                numero=row['numero'],
                complemento=row['complemento'] if row['complemento'] != '' else None,
                bairro=row['bairro'],
                cidade=row['cidade'],
                estado=row['estado'],
                cep=row['cep'],
                departamento=departamento,
                setor=setor,
                faixa_salarial=faixa_salarial,
                cargo=cargo,
                gerente=row['gerente'],
                tempo_trabalho=row['tempoTrabalho'],
                quantidade_empresas_trabalhou=row['quantidadeEmpresasTrabalhou'],
                quantidade_anos_trabalhados_anteriormente=row['quantidadeAnosTrabalhadosAnteriormente'],
                nivel_escolaridade=nivel_escolaridade,
                ex_funcionario=row['exFuncionario']
            )

            db.session.add(colaborador)
        db.session.commit()

        return 'Arquivo enviado e processado com sucesso'
    except Exception as e:
        raise Exception(f'Erro ao processar o arquivo: {str(e)}')
