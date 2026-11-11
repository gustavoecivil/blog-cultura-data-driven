# CDD INTELLIGENCE — EXP-011 | Auditoria documental externa de mecanismos e recursos

**Execução:** 11/11/2026. **Status:** auditoria documental concluída, validação preditiva e técnica independente pendentes.

## Escopo e controle de continuidade
Este experimento preserva as 20 hipóteses H01–H20 e o desenho EXP-010. Testa parcialmente a H18 (recursos e anulações) e organiza uma prova externa para testes futuros de H02, H10 e H20. **Não** testa H20 (efeito no aprendizado), não executa Jev, Laya ou LLM, e não declara generalização de mecanismos cognitivos.

## Fonte externa inédita no pipeline anterior
TRT 10ª Região, cargo 6 — Analista Judiciário, Engenharia Civil, aplicado em 16/03/2025, código **050_TRT10_006_01**. Conferidos o caderno oficial, o gabarito definitivo e as justificativas de recursos do Cebraspe. O arquivo binário PDF não pôde ser baixado neste ambiente; o índice registra os números, páginas e gabaritos, **não** os enunciados íntegros. As 70 células foram manualmente copiadas e verificadas visualmente; segunda conferência independente ainda é necessária.

Fontes primárias:
- [Caderno oficial](https://cdn.cebraspe.org.br/concursos/trt10_24/arquivos/050_TRT10_006_01.pdf)
- [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/trt10_24/arquivos/Gab_Definitivo_050_TRT10_006_01.pdf)
- [Justificativas dos recursos](https://cdn.cebraspe.org.br/concursos/trt10_24/arquivos/TRT10_24_Justificativas_de_altera%C3%A7%C3%B5es_de_gabarito.pdf)
- [Justificativas Câmara 2012](https://cdn.cebraspe.org.br/concursos/CAMARA2012/arquivos/CD_2012_JUSTIFICATIVAS_DE_ALTERA____ES_DE_GABARITO_RETIFICADO.PDF)

## Evidências de alteração nesta prova (n=70)
| Item | Preliminar → final | Tipo | Motivo documental | Status da interpretação |
|---|---|---|---|---|
| 73 | C → anulada | Anulação | Redação dúbia | Explicação oficial; sem rótulo cognitivo homologado |
| 80 | C → E | Alteração | NR-18 não admite a exceção de proteção alegada | Explicação oficial; T03 e T11 somente candidatos |
| 95 | E → anulada | Anulação | Mais de uma interpretação possível | Explicação oficial; sem rótulo cognitivo homologado |
| 120 | C → anulada | Anulação | Verbo 'dever' em vez de 'deve' | Explicação oficial; T03 somente candidato |

**Controle de independência:** a justificativa sobre o verbo do item 120 reaparece em diferentes especialidades da mesma seleção (Arquitetura, Arquivologia, Comunicação Social, Engenharia Civil e História). Essas linhas não constituem cinco itens independentes: são um mesmo padrão documental reutilizado. A unidade de análise é item de prova, com chave de origem e deduplicação.

## Estudo cruzado 2012 × 2025: apenas casos com recurso
| Prova | Itens específicos | Itens com gabarito alterado ou anulado | Anulados | Proporção de mudanças |
|---|---:|---:|---:|---:|
| Câmara 2012 | 80 | 7 | 2 | 8,75% |
| TRT-10 2025 | 70 | 4 | 3 | 5,71% |

Fisher bilateral para proporção de alteração ou anulação: **p=0.5439**. Para anulações isoladas: **p=0.6646**. Não há base para afirmar diferença estável com tão poucas provas, e seleção por recursos não representa a distribuição de todos os mecanismos da banca.

## O que observamos e o que ainda é hipótese
**Fato documental:** o TRT10 expôs dois casos de ambiguidade, um de exceção normativa indevida e um de forma verbal. Entre os sete casos documentados da Câmara 2012, também surgem terminologia, exigências/condições, relações de garantia, cálculos e conflitos bibliográficos. **Hipótese:** parte dessas operações de raciocínio é recorrente, pode ser classificada sem contaminação por gabarito e pode ajudar o candidato; os dados atuais ainda não demonstram isso.

**Limites decisivos:** (1) os onze recursos são escolhidos após conhecer o resultado; (2) faltam controles com itens não recorridos e revisão técnica dupla; (3) as etiquetas Txx são sugestões, não validações; (4) o pesquisador já inspecionou materiais do TRT10, de modo que futuras avaliações não serão verdadeiramente inéditas para ele; (5) nenhuma alegação de desempenho de Jev/Laya/LLM.

## Entrega objetiva e próximos portões
- Base SQLite EXP-011 imutável em relação ao EXP-009, índice oficial de 70, matriz documental de 11 recursos, deduplicação do item 120, script reprodutível e painel web.
- Portão A: importar PDFs oficiais com hash e revisar **todos** os textos individualmente; manter texto licenciado em espaço interno.
- Portão B: duas classificações genuinamente independentes sem gabarito, com taxonomia congelada e opção de abstenção; os recursos permanecem como referência de casos contestados, não como gold standard do corpus.
- Portão C: teste fora do desenvolvimento em outro concurso ainda não analisado, comparação de modelos e validação de H20 em treino de candidato com tempo equivalente.

## Registro de decisão
EXP-011 = evidência documental externa + estrutura de teste, não avaliação de generalização validada. Nenhuma ampliação da hipótese H20 ou nova prioridade estratégica.