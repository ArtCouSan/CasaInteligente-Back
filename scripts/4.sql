INSERT INTO colaborador (
    nome, 
    cpf, 
    idade, 
    genero_id, 
    estado_civil_id, 
    telefone, 
    email, 
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
    faixa_salarial_id, 
    cargo_id, 
    gerente, 
    tempo_trabalho, 
    quantidade_empresas_trabalhou, 
    quantidade_anos_trabalhados_anteriormente, 
    nivel_escolaridade_id, 
    acoes
) VALUES (
    'João Silva',                        -- Nome
    '123.456.789-00',                    -- CPF
    31,                                  -- Idade
    1,                                   -- Genero (1: Masculino)
    2,                                   -- Estado Civil (2: Casado)
    '11999999999',                       -- Telefone
    'joao.silva@example.com',            -- Email
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
    3,                                   -- Faixa Salarial (3: R$ 3.001 - R$ 4.000)
    1,                                   -- Cargo (1: Desenvolvedor)
    'Maria Souza',                       -- Gerente (Nome do gerente)
    '5 anos',                            -- Tempo de Trabalho
    3,                                   -- Quantidade de Empresas Trabalhou
    8,                                   -- Quantidade de Anos Trabalhados Anteriormente
    2,                                   -- Nível de Escolaridade (2: Ensino Superior Completo)
    'Promovido a Desenvolvedor Sênior'   -- Ações
);
