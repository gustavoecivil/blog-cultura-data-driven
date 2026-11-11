# EXP-010 — CDD Intelligence

O experimento é uma continuação preservada de EXP-009, sem alterar sua base original.

## Arquivos
- `index.html`: painel estático, publicado no GitHub Pages.
- `dados_painel.json`: visões agregadas e textos públicos de pesquisa (sem gabaritos).
- `classificacao_multirotulo_38.csv`: resultados de duas baselines transparentes.
- `fila_revisao_38.csv`: registros sem convergência (22 questões).
- `payload_externo_38_sem_gabarito.jsonl`: entradas para eventual teste futuro de LLM/Jev/Laya, **não executado**.
- `rastreabilidade_interna_38.csv`: identificação documental interna; não usar para avaliação cega.
- `cdd_intelligence_exp010.sqlite3`: cópia do banco anterior com nova tabela.
- `exp010_run.py`: script reproduzível.
- `EXP010_RELATORIO_CIENTIFICO.md`: método e resultados.
- `MANIFESTO_SHA256.json`: hashes dos artefatos gerados.

## Reprodução
Instalar `scikit-learn`. Colocar as entradas do EXP-009 em uma pasta `input/` irmã da pasta dos scripts, mantendo os nomes documentados. Executar `python exp010_run.py` e `python render_exp010.py`. Não requer chaves de API e não executa IA externa. **Nenhuma acurácia de classificação foi estimada.**