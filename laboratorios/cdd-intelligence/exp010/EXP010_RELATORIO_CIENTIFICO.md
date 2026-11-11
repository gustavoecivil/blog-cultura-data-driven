# CDD Intelligence — EXP-010
## Classificação multiparâmetros de operações cognitivas: duas baselines transparentes

**Data de execução:** 11/11/2026  
**Estado:** EXPERIMENTO EXPLORATÓRIO REPRODUZIDO, SEM VALIDAÇÃO TÉCNICA INDEPENDENTE.  
**Continuidade:** EXP-009 (código e amostra), H02/H10/H19/H20. H01–H20 e H-ORI-01 preservadas, sem reformulação.

### 1. Pergunta científica
Uma atribuição multilabel de até três operações cognitivas reduz a falta de convergência entre dois métodos simples, comparada à atribuição única do EXP-009? **Não** confundir aumento de coincidência com aumento de acurácia ou eficácia de aprendizagem.

### 2. Dados e protocolo
- Os **mesmos 38 enunciados** de duas provas exploradas anteriormente (20 Câmara dos Deputados/2012 e 18 MPGO/2024), sem revisão humana dupla e sem separação externa inédita.
- Taxonomia congelada de **T01–T11**, obtida do EXP-009. Gabaritos e justificativas não entraram nas entradas dos algoritmos nem no arquivo de payload externo.
- Baseline A: ocorrências de expressões técnicas definidas no código; atribui 0–3 operações quando a contagem e o corte relativo alcançam os limiares fixados na implementação.
- Baseline B: similaridade TF-IDF de n-gramas de caracteres com 11 descrições prototípicas; atribui 0–3 operações, com limiar absoluto **0,095** e corte relativo **72% do máximo**.
- A interseção entre conjuntos e o índice de Jaccard são medidos por questão. **Ambos são algoritmos determinísticos de triagem; não são duas revisões humanas independentes.**
- As regras do EXP-010 foram propostas após observar os resultados agregados do EXP-009. Portanto, a comparação é *exploratória e sujeita a ajuste retrospectivo*, não experimento pre-registrado cego.

### 3. Resultados efetivamente obtidos

| Medida | Resultado |
|---|---:|
| Questões analisadas | 38 |
| Baseline A com ao menos um rótulo | 22/38 (57,9%) |
| Baseline B com ao menos um rótulo | 27/38 (71,1%) |
| Interseção não vazia entre as duas classificações | **16/38 (42,1%)** |
| Nenhuma categoria comum com algum rótulo emitido | 15/38 (39,5%) |
| Dupla abstenção (ambos sem rótulo) | 7/38 (18,4%) |
| Média de Jaccard, contando dupla abstenção como 1 | 0,465 |
| Média de Jaccard sem dupla abstenção | 0,344 |
| Itens multilabel no método A / B | 5 / 12 |
| Referências técnicas independentes homologadas | 0 |
| Execuções externas Jev / Laya / LLM | 0 / 0 / 0 |

**Nota sobre Jaccard:** uma dupla abstenção tem união vazia e é tratada como Jaccard=1 por convenção computacional, **mas não é sucesso substantivo**. Para interpretação técnica, usar sobretudo o valor que exclui duplas abstenções.

### 4. Relação com EXP-009 e limites
O EXP-009 encontrou **9/38 acordos com categoria definida** em uma tarefa de rótulo único. O EXP-010 encontra **16/38 com interseção não vazia** em tarefa de múltiplos rótulos. As grandezas **não são equivalentes**; não se deve declarar melhora de 9 para 16, nem calcular percentual de ganho como se ambos medissem acerto. Multiplicar o número de rótulos torna a interseção mais provável mesmo sem melhorar a qualidade.

Estão identificadas **22 questões sem categoria compartilhada**, incluindo sete sem qualquer sinal; elas são prioridade de revisão. Os 16 casos de sobreposição **também não estão validados** e devem ser avaliados por revisão técnica; não são um conjunto aprovado para treinamento.

### 5. Casos âncora e observação negativa
Duas questões da amostra têm recurso da banca com fundamentação documental (Câmara/2012: 108, terminologia, e 114, cálculo de armadura). Na análise exploratória, os dois métodos **não convergiram em uma categoria** para esses casos: um método reconheceu T05 na questão 108 e o outro retornou T08; ambos abstiveram-se na 114. Esse pequeno exame de consistência não é teste cego nem estimativa de desempenho. Mostra por que automação não pode homologar rótulos sem revisão especializada.

### 6. Integridade e auditabilidade
- Banco SQLite do EXP-009 preservado; EXP-010 cria **nova cópia** com tabela `exp010_multirotulo`.
- 38 identificadores únicos e hashes de transcrição correspondentes aos registros de origem.
- Inputs enviados a classificadores não incluem gabarito, número da questão, nome do concurso ou rótulos gerados pelos métodos.
- Painel público não expõe histórico individual de aprendizagem nem a chave restrita de respostas.
- O hash dos arquivos científicos identifica **os artefatos locais**, não os PDFs originais dos concursos.
- Teste funcional do painel em navegador Chromium: 38 registros, filtro por estado, filtro por operação e busca textual. Console sem exceções.

### 7. Decisões
**D-010-01:** autorizar multi-rótulo somente como **candidato de classificação** e não como gabarito técnico.  
**D-010-02:** manter a categoria `SEM_SINAL` e a opção de abstenção.  
**D-010-03:** não declarar eficácia nem superioridade por mais sobreposições.  
**D-010-04:** publicar EXP-010 no GitHub Pages, preservando EXP-009 no endereço anterior.  
**D-010-05:** próximo portão: selecionar e revisar de forma independente uma amostra externa inédita com normas e fontes contemporâneas, então executar os modelos conectados em condições equivalentes. H20 (ganho na aprendizagem) permanece **NÃO TESTADA**.

### 8. Fontes documentais de origem
- Prova Câmara/2012: https://cdn.cebraspe.org.br/concursos/CAMARA2012/arquivos/CAMDEP12_003_06.pdf
- Justificativas da Câmara/2012: https://cdn.cebraspe.org.br/concursos/CAMARA2012/arquivos/CD_2012_JUSTIFICATIVAS_DE_ALTERA____ES_DE_GABARITO_RETIFICADO.PDF
- Prova MPGO/2024: https://cdn.cebraspe.org.br/concursos/mp_go_24_servidor/arquivos/964_MPGO_002_01.PDF

**O EXP-010 não serve para prever a alternativa C/E. Serve para identificar onde nossos classificadores estão convergindo ou onde precisamos de evidência técnica antes de ensinar um mecanismo.**