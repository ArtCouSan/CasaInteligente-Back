USE colaborador_db;

CREATE TABLE genero (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE estado_civil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE formacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE faculdade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE departamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE setor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE faixa_salarial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE nivel_escolaridade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE cargo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE perfil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE colaborador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    idade INT NOT NULL,
    genero_id INT,
    estado_civil_id INT,
    telefone VARCHAR(20),
    email VARCHAR(255),
    senha_hash VARCHAR(255) NOT NULL,
    formacao_id INT,
    faculdade_id INT,
    endereco VARCHAR(255) NOT NULL,
    numero VARCHAR(10),
    complemento VARCHAR(255),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(50),
    cep VARCHAR(20),
    departamento_id INT,
    setor_id INT,
    faixa_salarial_id INT,
    cargo_id INT,
    gerente VARCHAR(100),
    tempo_trabalho VARCHAR(50),
    quantidade_empresas_trabalhou INT,
    quantidade_anos_trabalhados_anteriormente INT,
    nivel_escolaridade_id INT,
    ex_funcionario BOOL,
    FOREIGN KEY (genero_id) REFERENCES genero(id),
    FOREIGN KEY (estado_civil_id) REFERENCES estado_civil(id),
    FOREIGN KEY (formacao_id) REFERENCES formacao(id),
    FOREIGN KEY (faculdade_id) REFERENCES faculdade(id),
    FOREIGN KEY (departamento_id) REFERENCES departamento(id),
    FOREIGN KEY (setor_id) REFERENCES setor(id),
    FOREIGN KEY (faixa_salarial_id) REFERENCES faixa_salarial(id),
    FOREIGN KEY (cargo_id) REFERENCES cargo(id),
    FOREIGN KEY (nivel_escolaridade_id) REFERENCES nivel_escolaridade(id)
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
    predicao INT,
    motivo TEXT,
    sugestao TEXT,
    observacao TEXT,
    FOREIGN KEY (colaborador_id) REFERENCES colaborador(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE pergunta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    texto VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE resposta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    colaborador_id INT NOT NULL,
    pergunta_id INT NOT NULL,
    nota TINYINT NOT NULL,
    trimestre ENUM('Q1', 'Q2', 'Q3', 'Q4') NOT NULL,
    ano YEAR NOT NULL,
    FOREIGN KEY (colaborador_id) REFERENCES colaborador(id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta(id) ON DELETE CASCADE,
    UNIQUE (colaborador_id, pergunta_id, trimestre, ano)
) ENGINE=InnoDB;