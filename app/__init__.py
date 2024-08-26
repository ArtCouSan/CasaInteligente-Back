from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Importe o CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configurações do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sdc:sdc@localhost/colaborador_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar o SQLAlchemy com o app
    db.init_app(app)

    # Ativar CORS para o app
    CORS(app)

    # Importa as rotas e registra o Blueprint
    from .routes import bp as colaborador_bp
    app.register_blueprint(colaborador_bp, url_prefix='/api')

    return app
