INSERT INTO genero (descricao) VALUES 
('Não Respondido'),
('Masculino'),
('Feminino'),
('Outros');

INSERT INTO estado_civil (descricao) VALUES 
('Não Respondido'),
('Solteiro'),
('Casado'),
('Viuvo'),
('Divorciado'),
('Solteira'),
('Casada'),
('Viuva'),
('Divorciada');

INSERT INTO nivel_escolaridade (descricao) VALUES 
('Não Respondido'),
('Ensino Fundamental - Completo'),
('Ensino Fundamental - Incompleto'),
('Ensino Médio - Completo'),
('Ensino Médio - Incompleto'),
('Ensino Superior - Completo'),
('Ensino Superior - Incompleto'),
('Bacharelado'),
('Mestrado'),
('Doutorado');

INSERT INTO faculdade (nome) VALUES 
('Não Respondido'),
('USP'),
('PUC-SP'),
('FGV');

INSERT INTO viagem_trabalho (descricao) VALUES 
('Não Respondido'),
('Não Viaja'),
('Viaja Raramente'),
('Viaja Frequentemente');

INSERT INTO formacao (descricao) VALUES 
('Não Respondido'),
('Ciência da Computação'),
('Engenharia de Software'),
('Administração'),
('Ciências da Vida'),
('Saude'),
('Marketing'),
('TI'),
('Outros'),
('RH');

INSERT INTO departamento (nome) VALUES 
('Não Respondido'),
('Tecnologia da Informação'),
('Financeiro'),
('Rercursos Humanos'),
('Pesquisa e Desenvolvimento'),
('Vendas');


INSERT INTO setor (nome) VALUES 
('Não Respondido'),
('Desenvolvimento'),
('Contabilidade'),
('Recrutamento');

INSERT INTO cargo (nome) VALUES 
('Não Respondido'),
('Desenvolvedor'),
('Analista Financeiro'),
('Gerente de TI'),
('Executivo de Vendas'),
('Pesquisador'),
('Tecnico Laboratorial'),
('Diretor de Manufatura'),
('Representante de Saude'),
('Representante de Vendas'),
('Diretor de Pesquisa'),
('Recursos Humanos');

-- Inserir a pesquisa
INSERT INTO pesquisa (titulo, descricao, ano)
VALUES ('Pesquisa de Satisfação no Trabalho', 'Avaliação de diferentes aspectos do trabalho', 2024);

-- Obter o ID da pesquisa criada
SET @pesquisa_id = LAST_INSERT_ID();

-- 1. Pergunta: Satisfação no Trabalho
INSERT INTO pergunta (texto) VALUES ('Qual é o seu nível de satisfação no trabalho?');
SET @pergunta_satisfacao_trabalho = LAST_INSERT_ID();
INSERT INTO pesquisa_pergunta (pesquisa_id, pergunta_id) 
VALUES (@pesquisa_id, @pergunta_satisfacao_trabalho);
INSERT INTO resposta_opcao (pergunta_id, texto, nota) VALUES
(@pergunta_satisfacao_trabalho, 'Baixa', 1),
(@pergunta_satisfacao_trabalho, 'Média', 2),
(@pergunta_satisfacao_trabalho, 'Alta', 3),
(@pergunta_satisfacao_trabalho, 'Muito Alta', 4);

-- 2. Pergunta: Satisfação com o Ambiente
INSERT INTO pergunta (texto) VALUES ('Como você avalia a sua satisfação com o ambiente de trabalho?');
SET @pergunta_satisfacao_ambiente = LAST_INSERT_ID();
INSERT INTO pesquisa_pergunta (pesquisa_id, pergunta_id) 
VALUES (@pesquisa_id, @pergunta_satisfacao_ambiente);
INSERT INTO resposta_opcao (pergunta_id, texto, nota) VALUES
(@pergunta_satisfacao_ambiente, 'Baixa', 1),
(@pergunta_satisfacao_ambiente, 'Média', 2),
(@pergunta_satisfacao_ambiente, 'Alta', 3),
(@pergunta_satisfacao_ambiente, 'Muito Alta', 4);

-- 3. Pergunta: Envolvimento no Trabalho
INSERT INTO pergunta (texto) VALUES ('Qual é o seu nível de envolvimento com o trabalho?');
SET @pergunta_envolvimento_trabalho = LAST_INSERT_ID();
INSERT INTO pesquisa_pergunta (pesquisa_id, pergunta_id) 
VALUES (@pesquisa_id, @pergunta_envolvimento_trabalho);
INSERT INTO resposta_opcao (pergunta_id, texto, nota) VALUES
(@pergunta_envolvimento_trabalho, 'Baixo', 1),
(@pergunta_envolvimento_trabalho, 'Médio', 2),
(@pergunta_envolvimento_trabalho, 'Alto', 3),
(@pergunta_envolvimento_trabalho, 'Muito Alto', 4);

-- 4. Pergunta: Satisfação com o Relacionamento
INSERT INTO pergunta (texto) VALUES ('Como você avalia a sua satisfação com o relacionamento com colegas e gestores?');
SET @pergunta_satisfacao_relacionamento = LAST_INSERT_ID();
INSERT INTO pesquisa_pergunta (pesquisa_id, pergunta_id) 
VALUES (@pesquisa_id, @pergunta_satisfacao_relacionamento);
INSERT INTO resposta_opcao (pergunta_id, texto, nota) VALUES
(@pergunta_satisfacao_relacionamento, 'Baixa', 1),
(@pergunta_satisfacao_relacionamento, 'Média', 2),
(@pergunta_satisfacao_relacionamento, 'Alta', 3),
(@pergunta_satisfacao_relacionamento, 'Muito Alta', 4);

-- 5. Pergunta: Equilíbrio Trabalho-Vida
INSERT INTO pergunta (texto) VALUES ('Como você avalia o equilíbrio entre trabalho e vida pessoal?');
SET @pergunta_equilibrio_trabalho_vida = LAST_INSERT_ID();
INSERT INTO pesquisa_pergunta (pesquisa_id, pergunta_id) 
VALUES (@pesquisa_id, @pergunta_equilibrio_trabalho_vida);
INSERT INTO resposta_opcao (pergunta_id, texto, nota) VALUES
(@pergunta_equilibrio_trabalho_vida, 'Ruim', 1),
(@pergunta_equilibrio_trabalho_vida, 'Bom', 2),
(@pergunta_equilibrio_trabalho_vida, 'Melhor', 3),
(@pergunta_equilibrio_trabalho_vida, 'Ótimo', 4);

INSERT INTO perfil(nome) VALUES
('colaborador'),
('dp'),
('desenvolvedor');


INSERT INTO contexto (nome, descricao)
VALUES
('Liderança e Gestão', 'Avaliação sobre líderes e gestores, comunicação e suporte.'),
('Ambiente de Trabalho', 'Qualidade e conforto do espaço físico e recursos.'),
('Cultura Organizacional', 'Alinhamento de valores, inclusão e respeito à diversidade.'),
('Engajamento e Motivação', 'Satisfação com responsabilidades e reconhecimento.'),
('Desenvolvimento e Carreira', 'Oportunidades de crescimento e desenvolvimento.'),
('Relacionamento Interpessoal', 'Qualidade das interações e clima entre colegas.'),
('Equilíbrio Trabalho-Vida', 'Facilidade para balancear demandas pessoais e profissionais.'),
('Comunicação e Feedback', 'Clareza e abertura na comunicação e feedbacks.'),
('Processos e Eficiência', 'Eficácia dos processos internos e autonomia.'),
('Satisfação com Benefícios e Compensações', 'Adequação dos benefícios e compensações.'),
('Saúde e Bem-Estar', 'Acesso a programas de bem-estar e suporte.'),
('Inovação e Criatividade', 'Espaço para inovação e participação em projetos.');

-- 1. Satisfação no Trabalho -> Engajamento e Motivação (contexto_id = 4)
INSERT INTO pergunta_contexto (contexto_id, pergunta_id)
VALUES 
(4, 1);

-- 2. Satisfação com o Ambiente -> Ambiente de Trabalho (contexto_id = 2)
INSERT INTO pergunta_contexto (contexto_id, pergunta_id)
VALUES 
(2, 2);

-- 3. Envolvimento no Trabalho -> Engajamento e Motivação (contexto_id = 4)
INSERT INTO pergunta_contexto (contexto_id, pergunta_id)
VALUES 
(4, 3);

-- 4. Satisfação com o Relacionamento -> Relacionamento Interpessoal (contexto_id = 6)
INSERT INTO pergunta_contexto (contexto_id, pergunta_id)
VALUES 
(6, 4);

-- 5. Equilíbrio Trabalho-Vida -> Equilíbrio Trabalho-Vida (contexto_id = 7)
INSERT INTO pergunta_contexto (contexto_id, pergunta_id)
VALUES 
(7, 5);

-- Termômetro para 'Liderança e Gestão'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 1);

-- Termômetro para 'Ambiente de Trabalho'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 2);

-- Termômetro para 'Cultura Organizacional'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 3);

-- Termômetro para 'Engajamento e Motivação'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 4);

-- Termômetro para 'Desenvolvimento e Carreira'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 5);

-- Termômetro para 'Relacionamento Interpessoal'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 6);

-- Termômetro para 'Equilíbrio Trabalho-Vida'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 7);

-- Termômetro para 'Comunicação e Feedback'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 8);

-- Termômetro para 'Processos e Eficiência'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 9);

-- Termômetro para 'Satisfação com Benefícios e Compensações'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 10);

-- Termômetro para 'Saúde e Bem-Estar'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 11);

-- Termômetro para 'Inovação e Criatividade'
INSERT INTO termometro (motivo, proximidade_bom, status, contexto_id)
VALUES ('', 0, '', 12);
