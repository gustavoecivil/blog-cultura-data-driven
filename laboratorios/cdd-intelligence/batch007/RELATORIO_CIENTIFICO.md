# CDD Intelligence — BATCH-007
## Avaliação A/B de recuperação automática de evidências técnicas na resolução de questões Cebraspe de Engenharia Civil
**Data:** 12/11/2026  
**Estado:** executado, inferência cega e avaliação separadas, resultados negativos preservados  
**Repositório privado:** `gustavoecivil/GSA-Study-Pipeline`

### 1. Pergunta científica
Acrescentar à mesma IA pequenos trechos de documentos técnicos oficiais, selecionados automaticamente, aumenta a acurácia em itens C/E de Engenharia Civil de provas não utilizadas antes para medir o acerto do modelo?

### 2. Pré-registro e amostra
- Protocolo fixado no commit `366f840db3d7e2e86ccd46bb10fcb45b8d907c96` (`cdd_intelligence/BATCH007_PROTOCOLO_PRE_REGISTRADO.md`) antes de abrir gabaritos para a comparação.
- Cadernos inteiros selecionados: `TRF62025` (70 itens específicos) e `TCEAC2024AUD` (70 itens específicos). Essas provas já integravam o corpus de classificação, mas **não haviam sido avaliadas com o modelo de resolução**. Não alegar cegamento histórico absoluto.
- Total: 140 posições; 134 elegíveis para resolução texto-apenas por critérios prévios de qualidade de extração e ausência de referência visual explícita; seis não elegíveis permanecem no corpus. Entre as 134, quatro foram anuladas no gabarito definitivo e excluídas *somente* da taxa de acerto; 130 válidas.
- Modelo em ambos os braços: `Qwen/Qwen2.5-1.5B-Instruct`, CPU, decodificação determinística, mesma instrução de julgamento C/E. Sem treinamento supervisionado nem acesso do solucionador aos gabaritos.

### 3. Base documental prévia à prova
Fontes oficiais públicas, todos os documentos com edição anterior à aplicação das provas:

| Identificador | Documento | Páginas | Trechos | SHA-256 PDF |
|---|---|---:|---:|---|
| NR18-2020 | MTE — NR-18, edição histórica 2020 | 54 | 277 | `e1fe192e9b772feb0e2ff357c6f43708a5f515d2f343251bf2b94d4cfe4f11f9` |
| DNIT-IPR719 | DNIT — Manual de Pavimentação IPR 719, versão corrigida 2022 | 277 | 997 | `518539e2ffc8fed8e6d638180a82b9a984ec03d4d4ccb947d86c7f564d152864` |
| DNIT-IPR698 | DNER/DNIT — Manual de Projeto de Obras de Arte Especiais IPR 698 (1996) | 233 | 572 | `3bb781426b6cae19bafc5eba777f2a01c19df44a2deb97e96eaae80042a6762f` |

Total **1.846 trechos indexados**. Método de recuperação: TF–IDF com 1–2 gramas; corte predefinido de similaridade ≥0,115; até dois trechos de 610 caracteres recuperados por questão. Fonte, URL, página, offset, similaridade e hash foram preservados. Similaridade lexical não atesta validade técnica, nem constitui probabilidade de acerto. Documentos posteriores às provas não foram colocados na biblioteca primária. Não foi utilizado material ABNT restrito nem extraída informação de recursos/gabaritos para o solucionador.

### 4. Condições experimentais
- **A, baseline:** Qwen responde apenas ao texto do item, C ou E.
- **B, RAG:** mesma IA recebe, além do item, até dois trechos recuperados; quando nenhum trecho alcança o limiar, B=A, sem segunda inferência desnecessária.
- **C, controle negativo:** a cada cinco itens com recuperação, insere-se um trecho não pertinente de outra fonte na biblioteca, em teste separado. O controle ficou muito pequeno: três execuções, duas válidas após anulações. **Não tirar conclusões a partir dele.**

### 5. Integridade e temporalidade da avaliação
- Workflow cego `43222721189`: conclusão **success**. Inferência realizada em ambiente isolado contendo script e banco de enunciados, sem cofre de respostas.
- Hash SHA-256 das previsões A/B congeladas antes da comparação: `8ce33f02046ccfeb996bd2c97561c683d247ec591597f83a3a1dc05941b03ed9`.
- Workflow avaliador `43223717005`: conclusão **success**, iniciado após o workflow cego. Gabaritos acessados apenas em `cofre_gabaritos_ce_expandido.sqlite3`, fora do ambiente da inferência. Verificação de integridade SQLite e consistência de faixa concluída.
- Código: `cdd_intelligence/batch007_rag.py`, `batch007_avaliar.py`. Artefatos privados: `results/batch007_predicoes_ab_congeladas.json`, `batch007_fontes_auditoria.json`, `batch007_avaliacao_rag_ab.json`.

### 6. Resultado principal
| Indicador | Sem recuperação (A) | Com recuperação (B) |
|---|---:|---:|
| Questões válidas | 130 | 130 |
| Acertos | **82** | **79** |
| Acurácia | **63,08%** | **60,77%** |
| Intervalo de Wilson 95% | 54,52–70,89% | 52,18–68,74% |

Diferença pareada B−A **−2,31 pontos percentuais**. IC bootstrap pareado 95% **−6,15 a +1,54 pontos percentuais**. McNemar exato bicaudal **p=0,453125**. Não rejeitar igualdade de desempenho. Resultado negativo descritivo nesta coorte, **não** evidência de que RAG seja universalmente inferior.

Por prova: TRF-6, **37/62 (59,68%)** sem RAG e **36/62 (58,06%)** com RAG; TCE-AC, **45/68 (66,18%)** sem RAG e **43/68 (63,24%)** com RAG.

### 7. Análise do mecanismo: cobertura da recuperação
- Trechos acima do limiar encontrados em somente **16/134** questões selecionadas; **118** permaneceram sem evidência inserida.
- Entre os 16, **14 válidas** e duas anuladas. Nos 14 itens válidos com evidência, A obteve **12 acertos** e B **9 acertos** (−21,43 p.p. descritivos). Amostra muito pequena, com IC pareado amplo e p=0,453125: **não** interpretar como efeito populacional conclusivo.
- Mudanças de previsão: **8 no total**, das quais **2 correções, 5 pioras e uma alteração em item anulado**.
- QIDs corrigidas: `TRF62025-55` (DNIT IPR698, p.202) e `TRF62025-57` (DNIT IPR719, p.171).
- QIDs prejudicadas: `TCEAC2024AUD-59` (DNIT IPR719, p.74); `TCEAC2024AUD-74` (DNIT IPR698, p.24); `TRF62025-69` (DNIT IPR719, p.51); `TRF62025-82` (DNIT IPR698, p.202); `TRF62025-99` (NR18 histórica, p.11).
- Alteração anulada: `TRF62025-110` (NR18 histórica, pp.15/51).
- Controle placebo: **3 previsões realizadas, 2 válidas**; uma correta. Não há poder estatístico para testar diferença de contexto irrelevante.

### 8. Interpretação limitada, sem pós-otimização
A baixa taxa de acionamento do recuperador e o predomínio de pioras nos poucos itens alterados sugerem investigar a **pertinência, contextualização, edição temporal e aplicabilidade** do trecho, e não apenas quantidade de PDFs ou similaridade textual. Isso ainda é uma *hipótese de mecanismo*; os relatórios não permitem atribuir causalidade direta a um trecho sem outro experimento.

**TRF62025 e TCEAC2024AUD são agora testes consumidos**. Não modificar o limiar, as fontes, o prompt ou o método e reapresentá-las como “novo teste”. O próximo ensaio deve ser desenvolvido em outros conjuntos, fixar regras antes de ver gabaritos e usar outras provas inteiras não pontuadas, separando a unidade por prova e o componente visual da avaliação textual.

### 9. Implicação operacional para preparação do candidato
Ainda não adicionar documentos automaticamente a todas as respostas. Antes, implementar uma etapa automatizada que pergunta se a evidência é de fato aplicável ao conteúdo do item, à época da prova e à área normativa adequada, com abstenção quando insuficiente. Manter o corpus integral para pesquisa e filtrar por edital atual apenas na fase futura de treinamento pessoal. Nenhuma revisão operacional deve ser delegada ao candidato.