-- Inserindo colaborador com senha criptografada
INSERT INTO colaborador (
    nome, 
    cpf, 
    idade, 
    genero_id, 
    estado_civil_id, 
    telefone, 
    email, 
    senha_hash,                -- Campo para senha criptografada
    formacao_id, 
    faculdade_id, 
    endereco, 
    numero, 
    complemento, 
    bairro, 
    cidade, 
    estado, 
    cep, 
    departamento_id, 
    setor_id, 
    salario, 
    cargo_id, 
    gerente, 
    tempo_trabalho, 
    quantidade_empresas_trabalhou, 
    quantidade_anos_trabalhados_anteriormente, 
    nivel_escolaridade_id, 
    ex_funcionario,
    viagem_trabalho_id,
    distancia_casa,
    quantidade_anos_atual_gestor,
    quantidade_anos_na_empresa,
    quantidade_horas_treinamento_ano,
    porcentagem_ultimo_aumento
) VALUES (
    'Arthur',                        -- Nome
    '0',                    -- CPF
    31,                                  -- Idade
    1,                                   -- Genero (1: Masculino)
    2,                                   -- Estado Civil (2: Casado)
    '11999999999',                       -- Telefone
    'rm97804arthur@gmail.com',            -- Email
    '123', -- Senha criptografada gerada (exemplo de hash bcrypt)
    1,                                   -- Formação (1: Ciência da Computação)
    1,                                   -- Faculdade (1: USP)
    'Rua A',                             -- Endereço
    '456',                               -- Número
    'Apto 101',                          -- Complemento
    'Vila Nova',                         -- Bairro
    'São Paulo',                         -- Cidade
    'SP',                                -- Estado
    '01000-000',                         -- CEP
    1,                                   -- Departamento (1: TI)
    1,                                   -- Setor (1: Desenvolvimento)
    10000,                                   -- Faixa Salarial (3: R$ 3.001 - R$ 4.000)
    1,                                   -- Cargo (1: Desenvolvedor)
    'Maria Souza',                       -- Gerente (Nome do gerente)
    '5 anos',                            -- Tempo de Trabalho
    3,                                   -- Quantidade de Empresas Trabalhou
    8,                                   -- Quantidade de Anos Trabalhados Anteriormente
    2,                                   -- Nível de Escolaridade (2: Ensino Superior Completo)
    0,                                   -- Ex-funcionario
    1,
    1,
    1,
    1,
    1,
    13.5
);

-- Inserindo predição para o colaborador recém-criado
INSERT INTO colaborador_predicao (
    colaborador_id,
    evasao,
    motivo,
    sugestao,
    observacao
) VALUES (
    1,                                                      -- ID do colaborador recém-criado
    'Sim',                                                    -- Predição (exemplo de predição)
    'Alta chance de promoção devido ao excelente desempenho.', -- Motivo
    'Considerar promoção para a posição de Gerente de Projeto.', -- Sugestão
    'Observação adicional sobre o colaborador.'              -- Observação
);

-- Associando o colaborador recém-criado a perfis (roles)
-- Exemplo: João Silva é um "colaborador" e também tem perfil de "admin"
INSERT INTO colaborador_perfil (colaborador_id, perfil_id) VALUES (1, 3);  -- Perfil de desenvolvedor

-- Inserindo colaborador com senha criptografada
INSERT INTO colaborador (
    nome, 
    cpf, 
    idade, 
    genero_id, 
    estado_civil_id, 
    telefone, 
    email, 
    senha_hash,                -- Campo para senha criptografada
    formacao_id, 
    faculdade_id, 
    endereco, 
    numero, 
    complemento, 
    bairro, 
    cidade, 
    estado, 
    cep, 
    departamento_id, 
    setor_id, 
    salario, 
    cargo_id, 
    gerente, 
    tempo_trabalho, 
    quantidade_empresas_trabalhou, 
    quantidade_anos_trabalhados_anteriormente, 
    nivel_escolaridade_id, 
    ex_funcionario,
    viagem_trabalho_id,
    distancia_casa,
    quantidade_anos_atual_gestor,
    quantidade_anos_na_empresa,
    quantidade_horas_treinamento_ano,
    porcentagem_ultimo_aumento
) VALUES (
    'Arthur',                        -- Nome
    '1',                    -- CPF
    31,                                  -- Idade
    1,                                   -- Genero (1: Masculino)
    2,                                   -- Estado Civil (2: Casado)
    '11999999999',                       -- Telefone
    'rm97804arthur@gmail.com',            -- Email
    '123', -- Senha criptografada gerada (exemplo de hash bcrypt)
    1,                                   -- Formação (1: Ciência da Computação)
    1,                                   -- Faculdade (1: USP)
    'Rua A',                             -- Endereço
    '456',                               -- Número
    'Apto 101',                          -- Complemento
    'Vila Nova',                         -- Bairro
    'São Paulo',                         -- Cidade
    'SP',                                -- Estado
    '01000-000',                         -- CEP
    1,                                   -- Departamento (1: TI)
    1,                                   -- Setor (1: Desenvolvimento)
    5000,                                   -- Faixa Salarial (3: R$ 3.001 - R$ 4.000)
    1,                                   -- Cargo (1: Desenvolvedor)
    'Maria Souza',                       -- Gerente (Nome do gerente)
    '5 anos',                            -- Tempo de Trabalho
    3,                                   -- Quantidade de Empresas Trabalhou
    8,                                   -- Quantidade de Anos Trabalhados Anteriormente
    2,                                   -- Nível de Escolaridade (2: Ensino Superior Completo)
    0,                                   -- Ex-funcionario
    1,
    1,
    1,
    1,
    1,
    13.5
);

-- Inserindo predição para o colaborador recém-criado
INSERT INTO colaborador_predicao (
    colaborador_id,
    evasao,
    motivo,
    sugestao,
    observacao
) VALUES (
    2,                                                      -- ID do colaborador recém-criado
    'Sim',                                                     -- Predição (exemplo de predição)
    'Alta chance de promoção devido ao excelente desempenho.', -- Motivo
    'Considerar promoção para a posição de Gerente de Projeto.', -- Sugestão
    'Observação adicional sobre o colaborador.'              -- Observação
);

INSERT INTO colaborador_perfil (colaborador_id, perfil_id) VALUES (2, 1);  -- Perfil de colaborador

-- Inserindo colaborador com senha criptografada
INSERT INTO colaborador (
    nome, 
    cpf, 
    idade, 
    genero_id, 
    estado_civil_id, 
    telefone, 
    email, 
    senha_hash,                -- Campo para senha criptografada
    formacao_id, 
    faculdade_id, 
    endereco, 
    numero, 
    complemento, 
    bairro, 
    cidade, 
    estado, 
    cep, 
    departamento_id, 
    setor_id, 
    salario, 
    cargo_id, 
    gerente, 
    tempo_trabalho, 
    quantidade_empresas_trabalhou, 
    quantidade_anos_trabalhados_anteriormente, 
    nivel_escolaridade_id, 
    ex_funcionario,
    viagem_trabalho_id,
    distancia_casa,
    quantidade_anos_atual_gestor,
    quantidade_anos_na_empresa,
    quantidade_horas_treinamento_ano,
    porcentagem_ultimo_aumento
) VALUES (
    'Arthur',                        -- Nome
    '2',                    -- CPF
    31,                                  -- Idade
    1,                                   -- Genero (1: Masculino)
    2,                                   -- Estado Civil (2: Casado)
    '11999999999',                       -- Telefone
    'rm97804arthur@gmail.com',            -- Email
    '123', -- Senha criptografada gerada (exemplo de hash bcrypt)
    1,                                   -- Formação (1: Ciência da Computação)
    1,                                   -- Faculdade (1: USP)
    'Rua A',                             -- Endereço
    '456',                               -- Número
    'Apto 101',                          -- Complemento
    'Vila Nova',                         -- Bairro
    'São Paulo',                         -- Cidade
    'SP',                                -- Estado
    '01000-000',                         -- CEP
    1,                                   -- Departamento (1: TI)
    1,                                   -- Setor (1: Desenvolvimento)
    3000,                                   -- Faixa Salarial (3: R$ 3.001 - R$ 4.000)
    1,                                   -- Cargo (1: Desenvolvedor)
    'Maria Souza',                       -- Gerente (Nome do gerente)
    '5 anos',                            -- Tempo de Trabalho
    3,                                   -- Quantidade de Empresas Trabalhou
    8,                                   -- Quantidade de Anos Trabalhados Anteriormente
    2,                                   -- Nível de Escolaridade (2: Ensino Superior Completo)
    0,                                   -- Ex-funcionario
    1,
    1,
    1,
    1,
    1,
    13.5
);

-- Inserindo predição para o colaborador recém-criado
INSERT INTO colaborador_predicao (
    colaborador_id,
    evasao,
    motivo,
    sugestao,
    observacao
) VALUES (
    3,                                                     -- ID do colaborador recém-criado
    'Sim',                                                     -- Predição (exemplo de predição)
    'Alta chance de promoção devido ao excelente desempenho.', -- Motivo
    'Considerar promoção para a posição de Gerente de Projeto.', -- Sugestão
    'Observação adicional sobre o colaborador.'              -- Observação
);

INSERT INTO colaborador_perfil (colaborador_id, perfil_id) VALUES (3, 2);  -- Perfil de colaborador
