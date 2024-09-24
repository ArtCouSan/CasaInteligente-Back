USE colaborador_db;

CREATE TABLE genero (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) DEFAULT '' 
) ENGINE=InnoDB;

CREATE TABLE estado_civil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE formacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE faculdade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE departamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE setor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE viagem_trabalho (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(100) DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE nivel_escolaridade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE cargo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) DEFAULT ''
);

CREATE TABLE perfil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE colaborador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) DEFAULT '',                                  
    cpf VARCHAR(14) NOT NULL UNIQUE,                               
    idade INT DEFAULT 0,                                           
    genero_id INT DEFAULT NULL,                                    
    estado_civil_id INT DEFAULT NULL,
    telefone VARCHAR(20) DEFAULT '',                              
    email VARCHAR(255) DEFAULT '',
    senha_hash VARCHAR(255) NOT NULL,                              
    formacao_id INT DEFAULT NULL,
    faculdade_id INT DEFAULT NULL,
    endereco VARCHAR(255) DEFAULT '',                              
    numero VARCHAR(10) DEFAULT '',
    complemento VARCHAR(255) DEFAULT '',
    bairro VARCHAR(100) DEFAULT '',
    cidade VARCHAR(100) DEFAULT '',
    estado VARCHAR(50) DEFAULT '',
    cep VARCHAR(20) DEFAULT '',
    departamento_id INT DEFAULT NULL,
    setor_id INT DEFAULT NULL,
    salario DECIMAL(15,2) DEFAULT 0,
    cargo_id INT DEFAULT NULL,
    gerente VARCHAR(100) DEFAULT '',
    tempo_trabalho INT DEFAULT 0,
    quantidade_empresas_trabalhou INT DEFAULT 0,                   
    quantidade_anos_trabalhados_anteriormente INT DEFAULT 0,       
    nivel_escolaridade_id INT DEFAULT NULL,
    ex_funcionario TINYINT(1) DEFAULT 0,  
    viagem_trabalho_id INT DEFAULT NULL,     
    nivel_trabalho INT DEFAULT 1,
    
    porcentagem_ultimo_aumento INT DEFAULT NULL,
    distancia_casa INT DEFAULT NULL, 
    quantidade_anos_atual_gestor INT DEFAULT NULL, 
    quantidade_anos_na_empresa INT DEFAULT NULL,
    quantidade_horas_treinamento_ano INT DEFAULT NULL,

    FOREIGN KEY (genero_id) REFERENCES genero(id),
    FOREIGN KEY (estado_civil_id) REFERENCES estado_civil(id),
    FOREIGN KEY (formacao_id) REFERENCES formacao(id),
    FOREIGN KEY (faculdade_id) REFERENCES faculdade(id),
    FOREIGN KEY (departamento_id) REFERENCES departamento(id),
    FOREIGN KEY (setor_id) REFERENCES setor(id),
    FOREIGN KEY (cargo_id) REFERENCES cargo(id),
    FOREIGN KEY (nivel_escolaridade_id) REFERENCES nivel_escolaridade(id),
    FOREIGN KEY (viagem_trabalho_id) REFERENCES viagem_trabalho(id)
) ENGINE=InnoDB;

CREATE TABLE colaborador_perfil (
    colaborador_id INT,
    perfil_id INT,
    PRIMARY KEY (colaborador_id, perfil_id),
    FOREIGN KEY (colaborador_id) REFERENCES colaborador(id) ON DELETE CASCADE,
    FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE colaborador_predicao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    colaborador_id INT,
    evasao TEXT DEFAULT '',
    porcentagem_evasao INT DEFAULT 0,                                        
    motivo TEXT DEFAULT '',                                        
    sugestao TEXT DEFAULT '',
    observacao TEXT DEFAULT '',
    FOREIGN KEY (colaborador_id) REFERENCES colaborador(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE evasao_feature_importance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    colaborador_predicao_id INT,                                       
    motivo TEXT DEFAULT '', 
    acuracia DECIMAL(15,2) DEFAULT 0,    
    FOREIGN KEY (colaborador_predicao_id) REFERENCES colaborador_predicao(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE pergunta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    texto VARCHAR(255) NOT NULL
) ENGINE=InnoDB;


CREATE TABLE pesquisa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,      
    descricao TEXT DEFAULT '',      
    ano YEAR NOT NULL,
    is_pesquisa_fechada INT DEFAULT NULL,
    is_pesquisa_anonima INT DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE resposta_anonima (
    id INT AUTO_INCREMENT PRIMARY KEY,
    colaborador_id INT NOT NULL,
    pesquisa_id INT NOT NULL,            
    pergunta_id INT NOT NULL,
    nota TINYINT NOT NULL,   
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaborador(id) ON DELETE CASCADE,
    FOREIGN KEY (pesquisa_id) REFERENCES pesquisa(id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta(id) ON DELETE CASCADE,
    UNIQUE (colaborador_id, pesquisa_id, pergunta_id) 
) ENGINE=InnoDB;

CREATE TABLE resposta_fechada (
    id INT AUTO_INCREMENT PRIMARY KEY,
    colaborador_id INT NOT NULL,
    pesquisa_id INT NOT NULL,            
    pergunta_id INT NOT NULL,
    nota TINYINT NOT NULL,   
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaborador(id) ON DELETE CASCADE,
    FOREIGN KEY (pesquisa_id) REFERENCES pesquisa(id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta(id) ON DELETE CASCADE,
    UNIQUE (colaborador_id, pesquisa_id, pergunta_id) 
) ENGINE=InnoDB;

CREATE TABLE resposta_opcao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    texto VARCHAR(255) NOT NULL,
    nota TINYINT NOT NULL, 
    pergunta_id INT NOT NULL,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE pesquisa_pergunta (
    pesquisa_id INT NOT NULL,
    pergunta_id INT NOT NULL,
    PRIMARY KEY (pesquisa_id, pergunta_id),
    FOREIGN KEY (pesquisa_id) REFERENCES pesquisa(id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE contexto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT
);

CREATE TABLE pergunta_contexto (
    contexto_id INT NOT NULL,
    pergunta_id INT NOT NULL,
    PRIMARY KEY (pergunta_id, contexto_id),
    FOREIGN KEY (contexto_id) REFERENCES contexto(id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE termometro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    motivo VARCHAR(500) NOT NULL,
    proximidade_bom DECIMAL(15,2) DEFAULT 0, 
    status VARCHAR(255) NOT NULL,
    contexto_id INT NOT NULL,
    FOREIGN KEY (contexto_id) REFERENCES contexto(id) ON DELETE CASCADE
) ENGINE=InnoDB;