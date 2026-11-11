# EXP-012 — Protocolo de revisão independente (pré-registro)

Status: **ainda não executado**. A presente análise é retrospectiva, pois os gabaritos e as justificativas foram consultados antes da classificação.

1. Importar cadernos e anexos normativos com hash SHA-256; preservar figuras e tabelas.
2. Escolher um concurso distinto ainda não explorado e não usar seu gabarito na construção da rubrica.
3. Dois revisores técnicos humanos, trabalhando separadamente, recebem o texto sem gabarito, códigos de prova, fontes ou justificativas.
4. Para cada questão: identificar conceito, condições de validade, norma e versão, operação cognitiva T01–T11 (multi-rótulo) e classe INDETERMINÁVEL quando for o caso. Anotar evidências e tempo.
5. Congelar classificações, auditá-las contra fontes contemporâneas, resolver discordâncias com fundamentação. Não usar julgamento do mesmo LLM como revisão humana independente.
6. Calcular concordância por categoria (Kappa/AC1 ou macro-F1) com intervalos; comparar baselines, Jev, Laya, LLM em corpus previamente reservado. Registrar versões, prompts, tempo, custo e abstenções.
7. Só depois testar H20 no candidato com tempo igual de estudo e avaliação em questões novas; se não houver respostas, H20 permanece não testada.

Regra: anulação por ambiguidade não recebe resposta C/E forçada, e casos com figura sem figura disponível exigem abstenção.