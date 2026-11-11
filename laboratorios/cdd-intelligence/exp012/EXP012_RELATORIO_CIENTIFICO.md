# CDD Intelligence — EXP-012: auditoria externa FNDE/2024 e mecanismos documentados

**Data:** 2026-11-11 • **Estado:** auditoria documental executada, validação humana e preditiva pendentes.

## Pergunta central

Os mecanismos identificados nas justificativas oficiais se repetem entre diferentes provas de Engenharia Civil? É possível separá-los dos enunciados anulados por indeterminação sem transformar coincidências em predição?

## Fontes

- prova: https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/998_FNDEINFRA_002_01.PDF

- preliminar: https://cdn.cebraspe.org.br/concursos/FNDE_24_PSS/arquivos/GAB_PRELIMINAR_998_FNDEINFRA_002_01.PDF

- definitivo: https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/GAB_DEFINITIVO_998_FNDEINFRA_002_01.PDF

- recursos: https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/FNDE_24_PSS_JUSTIFICATIVAS_DE_ALTERAES_DE_GABARITO.PDF

- edital: https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/ED_1_2024_FNDE_PSS_INFRA_ABERTURA.PDF

## Procedimentos realmente executados

- Indexação de 70 gabaritos finais FNDE/2024 com comparação célula a célula com os preliminares, conforme imagens oficiais consultadas na web; controle de consistência automatizado.

- Quatro mudanças detectadas automaticamente: 53 (E→X), 62 (C→E), 87 (E→X), 104 (C→E).

- União sem sobrescrever o EXP-011 dos quatro novos recursos com sete da Câmara/2012 e quatro do TRT-10/2025: 15 casos distintos.

- Classificação exploratória de motivos como específicos (11) ou genéricos (4). Não houve revisão cega, análise da ABNT integral ou execução de Jev/Laya.

- Banco SQLite em cópia nova, 70 itens adicionais e 15 justificativas documentais, links de fonte, provas de integridade.

## Resultados da prova FNDE/2024

- Gabarito: C=37, E=31, anuladas=2.

- Questão 53: redação contestada em item dependente de diagrama CPM; sem razão oficial detalhada suficiente para rotular mecanismo com segurança.

- Questão 62: gabarito C→E por divergência frente à NBR 6122/2022, anexo E, segundo a justificativa oficial. Verificação do texto integral da norma não realizada.

- Questão 87: anulação por redação considerada insuficiente para julgamento objetivo; mecanismo técnico exato ainda indeterminável.

- Questão 104: gabarito C→E. Banca afirma mínimo de 1,20 m, não 1,50 m, para escada em rota acessível; não confundir explicação oficial com revisão normativa independente.

## Comparação das três provas — apenas recursos conhecidos

| Prova | Alterações/anulações | Itens | Frequência descritiva |

|---|---:|---:|---:|

| Câmara dos Deputados 2012 | 7 | 80 | 8.75% |

| TRT-10 2025 | 4 | 70 | 5.71% |

| FNDE 2024 | 4 | 70 | 5.71% |

A soma é 15/220 (6,82%) e NÃO representa incidência de mecanismos em todas as questões nem tendência estável do Cebraspe. Amostras são selecionadas pelos recursos publicados.

## Achado metodológico

**11/15 justificativas** permitem formular um mecanismo técnico/documental específico; **4/15** são genéricas sobre ambiguidade/redação e não permitem determinar a operação cognitiva exata. A divisão é uma codificação exploratória do assistente, não uma classificação independente homologada.

O item FNDE 53 depende de diagrama. Logo, registrar texto sem preservar a figura resulta em corpus inadequado para classificação válida.

## Transferência: hipóteses, não confirmações

- FNDE 62 ↔ TRT-10 80: exceções/condições normativas disputadas, mas referentes a normas e situações técnicas diferentes. Categoria T03/T11 proposta, **não validada**.

- FNDE 104 ↔ Câmara 114: exatidão quantitativa altera o julgamento, mas trata-se de grandezas técnicas e tarefas cognitivas distintas. T06 proposta, **não validada**.

- FNDE 53/87 ↔ TRT-10 73/95: anulação por redação/ambiguidade não autoriza inferir uma única operação cognitiva. Abster.

## Limites e integridade

- PDFs consultados por visualização web com páginas conferidas; binários não baixados, portanto sem hash nem extração integral de 70 enunciados.

- O corpus FNDE foi consultado após a escolha da prova, inclusive justificativas e gabaritos: **não é teste cego** nem experimento de predição.

- Revisores humanos independentes: **zero**. Execuções Jev/Laya/LLM conectadas: **zero**. H20: não testada.

- A taxa de recursos é um fenômeno influenciado por contestação e decisões administrativas, não estimativa da probabilidade de um tipo de erro entre todos os itens.

- Os rótulos Txx são sugestões, não gabarito cognitivo oficial.

## Próximo portão

Proteger um novo conjunto de prova antes do acesso ao gabarito, importar integralmente figuras e texto, solicitar duas revisões humanas independentes e executar classificadores com inputs idênticos. Preservar hipóteses H01–H20, H-ORI-01 e todas as versões anteriores.

## Proveniência

Dados publicáveis: metadados e paráfrases autorais, não enunciados integrais; contexto privado de aprendizagem não é publicado. Scripts, controles e banco armazenados em pasta EXP-012 da Biblioteca.