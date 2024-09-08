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
('Ensino Superior - Incompleto');

INSERT INTO faculdade (nome) VALUES 
('Não Respondido'),
('USP'),
('PUC-SP'),
('FGV');

INSERT INTO formacao (descricao) VALUES 
('Não Respondido'),
('Ciência da Computação'),
('Engenharia de Software'),
('Administração');

INSERT INTO departamento (nome) VALUES 
('Não Respondido'),
('Tecnologia da Informação'),
('Financeiro'),
('Rercursos Humanos');

INSERT INTO setor (nome) VALUES 
('Não Respondido'),
('Desenvolvimento'),
('Contabilidade'),
('Recrutamento');

INSERT INTO faixa_salarial (descricao) VALUES 
('R$ 0 - R$ 0'),
('R$ 1.000 - R$ 1.500'),
('R$ 1.501 - R$ 2.000'),
('R$ 2.001 - R$ 2.500'),
('R$ 2.501 - R$ 3.000'),
('R$ 3.001 - R$ 3.500'),
('R$ 3.501 - R$ 4.000'),
('R$ 4.001 - R$ 4.500'),
('R$ 4.501 - R$ 5.000'),
('R$ 5.001 - R$ 5.500'),
('R$ 5.501 - R$ 6.000'),
('R$ 6.001 - R$ 6.500'),
('R$ 6.501 - R$ 7.000'),
('R$ 7.001 - R$ 7.500'),
('R$ 7.501 - R$ 8.000'),
('R$ 8.001 - R$ 8.500'),
('R$ 8.501 - R$ 9.000'),
('R$ 9.001 - R$ 9.500'),
('R$ 9.501 - R$ 10.000'),
('R$ 10.001 - R$ 10.500'),
('R$ 10.501 - R$ 11.000'),
('R$ 11.001 - R$ 11.500'),
('R$ 11.501 - R$ 12.000'),
('R$ 12.001 - R$ 12.500'),
('R$ 12.501 - R$ 13.000'),
('R$ 13.001 - R$ 13.500'),
('R$ 13.501 - R$ 14.000'),
('R$ 14.001 - R$ 14.500'),
('R$ 14.501 - R$ 15.000');

INSERT INTO cargo (nome) VALUES 
('Não Respondido'),
('Desenvolvedor'),
('Analista Financeiro'),
('Gerente de TI');

INSERT INTO pergunta (texto) VALUES 
('Qual é o seu nível de satisfação com o seu ambiente de trabalho?'),
('Como você descreveria seu nível de envolvimento com suas tarefas e responsabilidades no trabalho?'),
('Quão satisfeito você está com seu trabalho atual?'),
('Como você avalia sua satisfação com os relacionamentos profissionais que você tem na empresa (com colegas, supervisores, etc.)?'),
('Quão satisfeito você está com o equilíbrio entre sua vida profissional e pessoal?');

INSERT INTO perfil(nome) VALUES
('colaborador'),
('dp'),
('desenvolvedor')