from pathlib import Path
import sqlite3, csv, json, hashlib, shutil, html, re, math, datetime
from collections import Counter
from scipy.stats import fisher_exact
from statsmodels.stats.proportion import proportion_confint

ROOT=Path('/mnt/data/exp012'); OUT=ROOT/'output'; IN=ROOT/'input'; OUT.mkdir(exist_ok=True,parents=True)
DATE='2026-11-11'; PA='FNDE-2024'; HYP='H02,H10,H18,H20'
SRC={
'prova':'https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/998_FNDEINFRA_002_01.PDF',
'preliminar':'https://cdn.cebraspe.org.br/concursos/FNDE_24_PSS/arquivos/GAB_PRELIMINAR_998_FNDEINFRA_002_01.PDF',
'definitivo':'https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/GAB_DEFINITIVO_998_FNDEINFRA_002_01.PDF',
'recursos':'https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/FNDE_24_PSS_JUSTIFICATIVAS_DE_ALTERAES_DE_GABARITO.PDF',
'edital':'https://cdn.cebraspe.org.br/concursos/fnde_24_pss/arquivos/ED_1_2024_FNDE_PSS_INFRA_ABERTURA.PDF'}
# 4 blocos de 20,20,20,10 posições, transcritos das tabelas oficiais, revisão visual das páginas feita nesta execução.
final_blocks=[
'C E X C E C C E C E E E E C C C E C C E',
'C C E E E C E C C E E C C C C E X C E C',
'E C E C C C C E E C E C C E C E C E C C',
'E C C E C E E C E E']
pre_blocks=[
'C E E C E C C E C E E C E C C C E C C E',
'C C E E E C E C C E E C C C C E E C E C',
'E C E C C C C E E C E C C C C E C E C C',
'E C C E C E E C E E']
final=[v for b in final_blocks for v in b.split()]; pre=[v for b in pre_blocks for v in b.split()]
assert len(final)==len(pre)==70
changes={i:(pre[i-51],final[i-51]) for i in range(51,121) if pre[i-51]!=final[i-51]}
assert changes=={53:('E','X'),62:('C','E'),87:('E','X'),104:('C','E')}, changes

prior=list(csv.DictReader((IN/'matriz_11_recursos_documentados.csv').open(encoding='utf-8-sig',newline=''),delimiter=';'))
assert len(prior)==11
# Razões: resumos autorais de documentos oficiais, não texto integral das questões.
fnde={
53:{'motivo':'Redação prejudicou o julgamento objetivo; item exige leitura de diagrama CPM','mecanismo':'ambiguidade_na_redacao','dimensao':'REDAÇÃO / ANULAÇÃO','taxonomia':'INDETERMINAVEL','evidencia':'genérica na justificativa oficial; diagrama indispensável','pagina_prova':1,'gravidade':'alta','figura':1},
62:{'motivo':'Afirmação não condiz com o anexo E da ABNT NBR 6122/2022','mecanismo':'exigencia_normativa_incompatível','dimensao':'NORMA / ALTERAÇÃO','taxonomia':'T03+T11_CANDIDATOS','evidencia':'específica: anexo normativo, sem acesso ao texto licenciado da norma','pagina_prova':1,'gravidade':'alta','figura':0},
87:{'motivo':'Redação prejudicou o julgamento objetivo em questão sobre fiscalização de obra','mecanismo':'ambiguidade_na_redacao','dimensao':'REDAÇÃO / ANULAÇÃO','taxonomia':'INDETERMINAVEL','evidencia':'genérica na justificativa oficial','pagina_prova':3,'gravidade':'alta','figura':0},
104:{'motivo':'Banca aponta divergência entre 1,50 m afirmado e 1,20 m exigido para escada em rota acessível','mecanismo':'limiar_numerico_normativo','dimensao':'VALOR NORMATIVO / ALTERAÇÃO','taxonomia':'T06+T11_CANDIDATOS','evidencia':'específica: valor explícito na justificativa da banca (NBR 9050:2020 referenciada no caderno)','pagina_prova':4,'gravidade':'alta','figura':0}}

# Preparar sínteses do corpus de 15 recursos, preservando rótulos originais.
rows=[]
for p in prior:
  id_=p['id']; caso=p['mecanismo_documentado']
  vague= id_ in ('TRT10-2025-73','TRT10-2025-95')
  rows.append({'id':id_,'orgao':'Câmara dos Deputados' if id_.startswith('CD') else 'TRT-10',
   'ano':2012 if id_.startswith('CD') else 2025, 'numero':int(p['questao']),
   'resposta_pre':p['gabarito_preliminar'],'resposta_final':p['gabarito_final'],
   'situacao':'ANULAÇÃO' if p['gabarito_final']=='X' else 'ALTERAÇÃO',
   'dimensao':'REDAÇÃO / ANULAÇÃO' if vague else ('FUNDAMENTO TÉCNICO / ALTERAÇÃO' if p['gabarito_final']!='X' else 'REFERÊNCIA / ANULAÇÃO'),
   'mecanismo_documentado':caso,'sintese':p['explicacao_documental_resumida'],
   'taxonomia_proposta':p['rotulos_cognitivos_candidatos'],
   'evidencia_especifica':0 if vague else 1,
   'proveniencia':'justificativa oficial; resumo autoral da matriz EXP-011',
   'validacao_humana_independente':0,'gabarito_oculto_nas_etapas_de_classificacao':'a implementar',
   'url':p['fonte']})
for n,obj in fnde.items():
 rows.append({'id':f'FNDE-2024-{n}','orgao':'FNDE','ano':2024,'numero':n,
 'resposta_pre':pre[n-51],'resposta_final':final[n-51],
 'situacao':'ANULAÇÃO' if final[n-51]=='X' else 'ALTERAÇÃO',
 'dimensao':obj['dimensao'],'mecanismo_documentado':obj['mecanismo'],
 'sintese':obj['motivo'],'taxonomia_proposta':obj['taxonomia'],
 'evidencia_especifica':0 if n in (53,87) else 1,
 'proveniencia':'justificativa oficial consultada e conferida pela imagem PDF',
 'validacao_humana_independente':0,'gabarito_oculto_nas_etapas_de_classificacao':'a implementar',
 'url':SRC['recursos']})
assert len(rows)==15
assert Counter(r['orgao'] for r in rows)=={'Câmara dos Deputados':7,'TRT-10':4,'FNDE':4}
assert sum(r['evidencia_especifica'] for r in rows)==11

# Banco imutável: cópia versionada do EXP-011
shutil.copy2(IN/'cdd_intelligence_exp011.sqlite3',OUT/'cdd_intelligence_exp012.sqlite3')
c=sqlite3.connect(OUT/'cdd_intelligence_exp012.sqlite3')
c.execute('PRAGMA foreign_keys=ON')
c.execute('''CREATE TABLE IF NOT EXISTS exp012_fnde_70 (id TEXT PRIMARY KEY, numero INT UNIQUE NOT NULL, preliminar TEXT NOT NULL, definitivo TEXT NOT NULL,
 em_recurso INT NOT NULL, texto_integral INTEGER NOT NULL DEFAULT 0, dupla_revisao INTEGER NOT NULL DEFAULT 0, fonte_prova TEXT,fonte_gab TEXT)''')
for i in range(51,121):
 c.execute('INSERT INTO exp012_fnde_70 VALUES (?,?,?,?,?,?,?,?,?)',(f'FNDE-2024-{i}',i,pre[i-51],final[i-51],int(i in fnde),0,0,SRC['prova'],SRC['definitivo']))
c.execute('''CREATE TABLE IF NOT EXISTS exp012_recursos_15 (id TEXT PRIMARY KEY,orgao TEXT,ano INT,numero INT,preliminar TEXT,final TEXT,
 situacao TEXT,dimensao TEXT,mecanismo_documentado TEXT,sintese TEXT,taxonomia_proposta TEXT,evidencia_especifica INT,
 validacao_humana_independente INT,fonte TEXT)''')
for x in rows:
 c.execute('INSERT INTO exp012_recursos_15 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(x['id'],x['orgao'],x['ano'],x['numero'],x['resposta_pre'],x['resposta_final'],x['situacao'],x['dimensao'],x['mecanismo_documentado'],x['sintese'],x['taxonomia_proposta'],x['evidencia_especifica'],0,x['url']))
c.execute('''CREATE TABLE IF NOT EXISTS exp012_evidencia (id TEXT PRIMARY KEY,assertiva TEXT,status TEXT, justificativa TEXT, fonte TEXT)''')
evidence=[
('EV-001','FNDE 53 e 87: anulações relacionadas a redação','FATO DOCUMENTAL','Motivo genérico impede inferir com segurança mecanismo cognitivo específico.',SRC['recursos']),
('EV-002','FNDE 62: contestação de requisito normativo','FATO DOCUMENTAL','Cebraspe cita anexo E da ABNT NBR 6122/2022; texto integral da norma não auditado.',SRC['recursos']),
('EV-003','FNDE 104: troca do limiar dimensional','FATO DOCUMENTAL','Cebraspe apresenta 1,20 m em vez de 1,50 m; a alegação não equivale à auditoria independente da norma.',SRC['recursos']),
('EV-004','Relações de mecanismos em três provas','HIPÓTESE','Quatro grupos análogos; seleção por recurso impede estimar frequência geral.',SRC['recursos']),
('EV-005','Concordância humana independente','NÃO EXECUTADO','Sem dois revisores externos preenchendo a rubrica, não calcular kappa nem F1.',None),
('EV-006','Acurácia Jev/Laya/LLM','NÃO EXECUTADO','Sem corpus ouro auditado e sem chamadas operacionais, não reportar métricas.',None)]
c.executemany('INSERT INTO exp012_evidencia VALUES (?,?,?,?,?)', evidence)
c.commit()
qa={
 'fnde_70':c.execute('SELECT COUNT(*) FROM exp012_fnde_70').fetchone()[0],
 'fnde_recursos_4':c.execute('SELECT COUNT(*) FROM exp012_fnde_70 WHERE em_recurso=1').fetchone()[0],
 'recursos_15':c.execute('SELECT COUNT(*) FROM exp012_recursos_15').fetchone()[0],
 'exp011_preservado':c.execute("SELECT COUNT(*) FROM exp011_recursos").fetchone()[0]==11,
 'integridade_fk':c.execute('PRAGMA foreign_key_check').fetchall(),
 'integridade_db':c.execute('PRAGMA integrity_check').fetchone()[0],
 'texto_integrais_fnDE':c.execute('SELECT SUM(texto_integral) FROM exp012_fnde_70').fetchone()[0],
 'revisao_independente_fnDE':c.execute('SELECT SUM(dupla_revisao) FROM exp012_fnde_70').fetchone()[0],
 'unicos_FNDE':c.execute('SELECT COUNT(DISTINCT numero) FROM exp012_fnde_70').fetchone()[0],
 'alteracoes_FNDE':c.execute("SELECT COUNT(*) FROM exp012_fnde_70 WHERE em_recurso=1").fetchone()[0],
 'zero_chamadas_jev_exp006':c.execute('SELECT COUNT(*) FROM exp006_chamadas_modelos').fetchone()[0]==0,
}
assert qa['fnde_70']==70 and qa['recursos_15']==15 and qa['integridade_db']=='ok' and qa['integridade_fk']==[] and qa['unicos_FNDE']==70
c.close()

# métricas descritivas sem inferência causal
fndeN=Counter(final); n=70
items=[('Câmara dos Deputados',2012,7,80),('TRT-10',2025,4,70),('FNDE',2024,4,70)]
rates=[]
for org,year,k,den in items:
 low,high=proportion_confint(k,den,alpha=.05,method='wilson')
 rates.append({'orgao':org,'ano':year,'recursos':k,'itens':den,'taxa':k/den,'ic_wilson':[low,high]})
count_specific=sum(x['evidencia_especifica'] for x in rows)
metrics={'experimento':'EXP-012','data':DATE,'prova_nova':'FNDE 2024 Engenharia Civil','gabaritos_indexados':70,
         'fnde_gabaritos':dict(fndeN),'fnde_recursos':4,'total_casos_recursos':15,
         'casos_justificativa_especifica':count_specific,'casos_justificativa_generica':15-count_specific,
         'taxas_descritivas':rates,'humanos_independentes':0,'execucoes_jev':0,'execucoes_laya':0,'llm_externa':0,
         'validacao_preditiva_realizada':False,'fonte_pdf_binario_baixado':False,
         'qa':qa}
assert sum(fndeN.values())==70

# public/source file summaries
with (OUT/'fnde_70_indice.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['id','numero','gabarito_preliminar','gabarito_definitivo','recurso','fonte_prova','fonte_gabarito','enunciado_integro','revisao_independente']);w.writeheader();
 for i in range(51,121):w.writerow(dict(id=f'FNDE-2024-{i}',numero=i,gabarito_preliminar=pre[i-51],gabarito_definitivo=final[i-51],recurso='sim' if i in fnde else 'não',fonte_prova=SRC['prova'],fonte_gabarito=SRC['definitivo'],enunciado_integro='não',revisao_independente='pendente'))
with (OUT/'15_recursos_evidencia.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=list(rows[0]); w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
with (OUT/'casos_fnde_piloto.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['id','numero','figura_essencial','condicao_normativa','operacao_proposta','criterio_de_checagem','racional_oficial','status','fonte'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for n,o in fnde.items():w.writerow({'id':f'FNDE-2024-{n}','numero':n,'figura_essencial':int(bool(o['figura'])),'condicao_normativa':'ABNT NBR 6122/2022 Anexo E' if n==62 else 'ABNT NBR 9050:2020' if n==104 else 'Não especificada no recurso', 'operacao_proposta':o['taxonomia'],'criterio_de_checagem':o['evidencia'],'racional_oficial':o['motivo'],'status':'documental / taxonomia não homologada','fonte':SRC['recursos']})
with (OUT/'metricas_exp012.json').open('w',encoding='utf8') as f:json.dump(metrics,f,indent=2,ensure_ascii=False)
with (OUT/'controle_qualidade.json').open('w',encoding='utf8') as f:json.dump(qa,f,indent=2,ensure_ascii=False)

# Teste futuro com rubrica congelada e gabaritos indisponíveis à inferência
(OUT/'PROCOLO_REVISAO_CEGA.md').write_text('''# EXP-012 — Protocolo de revisão independente (pré-registro)

Status: **ainda não executado**. A presente análise é retrospectiva, pois os gabaritos e as justificativas foram consultados antes da classificação.

1. Importar cadernos e anexos normativos com hash SHA-256; preservar figuras e tabelas.
2. Escolher um concurso distinto ainda não explorado e não usar seu gabarito na construção da rubrica.
3. Dois revisores técnicos humanos, trabalhando separadamente, recebem o texto sem gabarito, códigos de prova, fontes ou justificativas.
4. Para cada questão: identificar conceito, condições de validade, norma e versão, operação cognitiva T01–T11 (multi-rótulo) e classe INDETERMINÁVEL quando for o caso. Anotar evidências e tempo.
5. Congelar classificações, auditá-las contra fontes contemporâneas, resolver discordâncias com fundamentação. Não usar julgamento do mesmo LLM como revisão humana independente.
6. Calcular concordância por categoria (Kappa/AC1 ou macro-F1) com intervalos; comparar baselines, Jev, Laya, LLM em corpus previamente reservado. Registrar versões, prompts, tempo, custo e abstenções.
7. Só depois testar H20 no candidato com tempo igual de estudo e avaliação em questões novas; se não houver respostas, H20 permanece não testada.

Regra: anulação por ambiguidade não recebe resposta C/E forçada, e casos com figura sem figura disponível exigem abstenção.
''',encoding='utf8')

# Relatório científico em Markdown
parts=['# CDD Intelligence — EXP-012: auditoria externa FNDE/2024 e mecanismos documentados',
 f'**Data:** {DATE} • **Estado:** auditoria documental executada, validação humana e preditiva pendentes.',
 '## Pergunta central',
 'Os mecanismos identificados nas justificativas oficiais se repetem entre diferentes provas de Engenharia Civil? É possível separá-los dos enunciados anulados por indeterminação sem transformar coincidências em predição?',
 '## Fontes',
 *[f'- {k}: {v}' for k,v in SRC.items()],
 '## Procedimentos realmente executados',
 '- Indexação de 70 gabaritos finais FNDE/2024 com comparação célula a célula com os preliminares, conforme imagens oficiais consultadas na web; controle de consistência automatizado.',
 '- Quatro mudanças detectadas automaticamente: 53 (E→X), 62 (C→E), 87 (E→X), 104 (C→E).',
 '- União sem sobrescrever o EXP-011 dos quatro novos recursos com sete da Câmara/2012 e quatro do TRT-10/2025: 15 casos distintos.',
 '- Classificação exploratória de motivos como específicos (11) ou genéricos (4). Não houve revisão cega, análise da ABNT integral ou execução de Jev/Laya.',
 '- Banco SQLite em cópia nova, 70 itens adicionais e 15 justificativas documentais, links de fonte, provas de integridade.',
 '## Resultados da prova FNDE/2024',
 f'- Gabarito: C={fndeN.get("C",0)}, E={fndeN.get("E",0)}, anuladas={fndeN.get("X",0)}.',
 '- Questão 53: redação contestada em item dependente de diagrama CPM; sem razão oficial detalhada suficiente para rotular mecanismo com segurança.',
 '- Questão 62: gabarito C→E por divergência frente à NBR 6122/2022, anexo E, segundo a justificativa oficial. Verificação do texto integral da norma não realizada.',
 '- Questão 87: anulação por redação considerada insuficiente para julgamento objetivo; mecanismo técnico exato ainda indeterminável.',
 '- Questão 104: gabarito C→E. Banca afirma mínimo de 1,20 m, não 1,50 m, para escada em rota acessível; não confundir explicação oficial com revisão normativa independente.',
 '## Comparação das três provas — apenas recursos conhecidos',
 '| Prova | Alterações/anulações | Itens | Frequência descritiva |', '|---|---:|---:|---:|',
 *[f'| {o} {y} | {k} | {d} | {k/d:.2%} |' for o,y,k,d in items],
 'A soma é 15/220 (6,82%) e NÃO representa incidência de mecanismos em todas as questões nem tendência estável do Cebraspe. Amostras são selecionadas pelos recursos publicados.',
 '## Achado metodológico',
 '**11/15 justificativas** permitem formular um mecanismo técnico/documental específico; **4/15** são genéricas sobre ambiguidade/redação e não permitem determinar a operação cognitiva exata. A divisão é uma codificação exploratória do assistente, não uma classificação independente homologada.',
 'O item FNDE 53 depende de diagrama. Logo, registrar texto sem preservar a figura resulta em corpus inadequado para classificação válida.',
 '## Transferência: hipóteses, não confirmações',
 '- FNDE 62 ↔ TRT-10 80: exceções/condições normativas disputadas, mas referentes a normas e situações técnicas diferentes. Categoria T03/T11 proposta, **não validada**.',
 '- FNDE 104 ↔ Câmara 114: exatidão quantitativa altera o julgamento, mas trata-se de grandezas técnicas e tarefas cognitivas distintas. T06 proposta, **não validada**.',
 '- FNDE 53/87 ↔ TRT-10 73/95: anulação por redação/ambiguidade não autoriza inferir uma única operação cognitiva. Abster.',
 '## Limites e integridade',
 '- PDFs consultados por visualização web com páginas conferidas; binários não baixados, portanto sem hash nem extração integral de 70 enunciados.',
 '- O corpus FNDE foi consultado após a escolha da prova, inclusive justificativas e gabaritos: **não é teste cego** nem experimento de predição.',
 '- Revisores humanos independentes: **zero**. Execuções Jev/Laya/LLM conectadas: **zero**. H20: não testada.',
 '- A taxa de recursos é um fenômeno influenciado por contestação e decisões administrativas, não estimativa da probabilidade de um tipo de erro entre todos os itens.',
 '- Os rótulos Txx são sugestões, não gabarito cognitivo oficial.',
 '## Próximo portão',
 'Proteger um novo conjunto de prova antes do acesso ao gabarito, importar integralmente figuras e texto, solicitar duas revisões humanas independentes e executar classificadores com inputs idênticos. Preservar hipóteses H01–H20, H-ORI-01 e todas as versões anteriores.',
 '## Proveniência',
 'Dados publicáveis: metadados e paráfrases autorais, não enunciados integrais; contexto privado de aprendizagem não é publicado. Scripts, controles e banco armazenados em pasta EXP-012 da Biblioteca.']
(OUT/'EXP012_RELATORIO_CIENTIFICO.md').write_text('\n\n'.join(parts)+'\n',encoding='utf8')
(OUT/'README.md').write_text('''# EXP-012 — CDD Intelligence

Auditoria documental FNDE/2024 + comparação de 15 recursos oficiais em três provas de Engenharia Civil.

**Não é teste cego, nem execução de Jev/Laya, nem validação de eficácia.** Os arquivos públicos contêm apenas dados oficiais já publicados e sínteses autorais. Não há respostas de candidato.

- `index.html`: painel estático auto-contido para GitHub Pages.
- `fnde_70_indice.csv`: gabaritos e links documentais, sem texto integral.
- `15_recursos_evidencia.csv`: motivos e status de evidência.
- `casos_fnde_piloto.csv`: quatro fichas documentais.
- `metricas_exp012.json` e `controle_qualidade.json`: resumo verificável.
- `cdd_intelligence_exp012.sqlite3`: cópia acrescida da base anterior.
- `PROCOLO_REVISAO_CEGA.md`: portão científico para estudo confirmatório.
- `EXP012_RELATORIO_CIENTIFICO.md`: relatório e limites.
- `build_exp012.py`: programa reproduzível a partir dos arquivos do EXP-011.
''',encoding='utf8')

# HTML auto-contido, sem dependências e sem enunciados integrais
pub=[{k:r[k] for k in ('id','orgao','ano','numero','situacao','dimensao','mecanismo_documentado','sintese','taxonomia_proposta','evidencia_especifica','url')} for r in rows]
pub_items=[{'numero':i,'gabarito':final[i-51],'preliminar':pre[i-51],'recurso':i in fnde} for i in range(51,121)]
js=json.dumps({'recursos':pub,'itens':pub_items,'taxas':rates,'total':len(rows),'especificas':count_specific,'fontes':SRC,'fnde':fnde},ensure_ascii=False).replace('</','<\\/')
style='''*{box-sizing:border-box} :root{--bg:#0b0d11;--panel:#151921;--muted:#98a2b3;--border:#2a313a;--gold:#d9b36b;--white:#f3f1ed;--teal:#9edbd2} body{margin:0;background:var(--bg);color:var(--white);font-family:Inter,system-ui,Arial,sans-serif}a{color:var(--gold)}.shell{max-width:1250px;margin:auto;padding:34px 24px 70px}.eyebrow{letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-size:11px;font-weight:800}.header{display:flex;justify-content:space-between;gap:20px;align-items:center;border-bottom:1px solid var(--border);padding-bottom:20px}.pill{border:1px solid #4d4330;color:#e5c792;padding:8px 12px;border-radius:20px;font-size:12px}.hero{padding:43px 0 20px;max-width:950px}h1{font-size:clamp(28px,4.5vw,52px);letter-spacing:-.04em;margin:10px 0 16px}p{line-height:1.62}.lead{font-size:17px;color:#b6bdc7;max-width:850px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}.stat,.card{border:1px solid var(--border);background:var(--panel);border-radius:16px;padding:20px}.stat .n{font-size:31px;color:var(--white);font-weight:800}.stat .lab{color:var(--muted);font-size:12px;margin-top:6px}.section{margin-top:36px}.section h2{font-size:22px;letter-spacing:-.02em}.sub{color:var(--muted);font-size:14px}.tabs{display:flex;flex-wrap:wrap;gap:8px;margin:28px 0 10px}.tab{border:1px solid var(--border);background:transparent;border-radius:10px;color:var(--muted);padding:10px 15px;cursor:pointer}.tab.active{background:#2c241a;color:var(--gold);border-color:#635235}.view{display:none}.view.active{display:block}.controls{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}input,select{background:#151921;border:1px solid #3b414b;border-radius:10px;padding:11px 12px;color:var(--white);min-width:190px;max-width:100%}.case-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.card h3{font-size:17px;margin:8px 0 5px}.card .mini{font-size:12px;color:var(--gold)}.card p{font-size:14px;color:#c8cdd4}.badge{display:inline-block;font-size:11px;padding:5px 9px;border-radius:40px;border:1px solid #454c54;color:#ced4da}.badge.warn{color:#e6c68c;border-color:#655338}.badge.ok{color:#9edbd2;border-color:#305a54}.barrow{display:grid;grid-template-columns:190px 1fr 74px;gap:14px;align-items:center;margin:15px 0}.track{height:18px;border-radius:30px;background:#282e36;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#b59562,#e5c791);border-radius:30px}.label{font-size:13px}.muted{color:var(--muted)}.numeric{font-variant-numeric:tabular-nums}.tablebox{overflow:auto;border:1px solid var(--border);border-radius:14px;margin-top:12px}table{border-collapse:collapse;width:100%;min-width:630px}th,td{border-bottom:1px solid var(--border);padding:11px 14px;text-align:left;font-size:13px}th{background:#20262e;color:#c6ccd2;position:sticky;top:0}tr:hover td{background:#1d242d}td small{color:var(--muted)}.source{font-size:12px}.callout{border-left:3px solid var(--gold);padding:15px 18px;background:#191a1e;margin:23px 0;color:#e3e0d8}.topnav{display:flex;gap:16px;flex-wrap:wrap;font-size:13px}.footer{border-top:1px solid var(--border);margin-top:60px;padding-top:22px;color:var(--muted);font-size:12px}.empty{color:var(--muted)}@media(max-width:800px){.stats{grid-template-columns:repeat(2,1fr)}.case-grid{grid-template-columns:1fr}.barrow{grid-template-columns:120px 1fr 60px}.topnav{display:none}}'''
htmlsrc='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0b0d11"><title>CDD Intelligence — EXP-012</title><style>''' + style + '''</style></head><body><main class="shell">
<header class="header"><div><div class="eyebrow">CULTURA DATA-DRIVEN / LABORATÓRIO</div><strong>CDD Intelligence</strong></div><nav class="topnav"><a href="../exp009/">EXP-009</a><a href="../exp010/">EXP-010</a><a href="../exp011/">EXP-011</a></nav><span class="pill">EXP-012 · estudo exploratório</span></header>
<section class="hero"><div class="eyebrow">ANATOMIA DAS QUESTÕES · ENGENHARIA CIVIL</div><h1>Por que uma questão está certa, errada ou foi anulada?</h1><p class="lead">Comparação de recursos oficiais em três concursos, agora com uma nova prova do FNDE. Os mecanismos são hipóteses auditáveis, não regras mágicas para acertar itens.</p></section>
<div class="stats"><div class="stat"><div class="n">70</div><div class="lab">Itens FNDE indexados</div></div><div class="stat"><div class="n">15</div><div class="lab">Recursos oficiais comparados</div></div><div class="stat"><div class="n">11</div><div class="lab">Motivos com evidência específica</div></div><div class="stat"><div class="n">0</div><div class="lab">Revisões humanas independentes</div></div></div>
<div class="callout"><strong>Estado científico:</strong> fontes oficiais e gabaritos conferidos; taxonomia cognitiva ainda provisória. FNDE não é teste cego: o gabarito e as justificativas já foram consultados. Jev, Laya e LLMs externas não foram executados nesta etapa.</div>
<div class="tabs"><button class="tab active" data-target="overview">Panorama</button><button class="tab" data-target="resources">Casos com recursos</button><button class="tab" data-target="gabaritos">70 gabaritos FNDE</button><button class="tab" data-target="methods">Método e fontes</button></div>
<section id="overview" class="view active"><div class="section"><h2>Frequência de alterações e anulações</h2><p class="sub">Apenas casos com recurso publicado. As porcentagens não representam frequência dos mecanismos em todas as questões.</p><div id="bars"></div></div><div class="section"><h2>O que os recursos realmente permitem inferir</h2><div class="case-grid"><article class="card"><span class="badge ok">Evidência documental</span><h3>Razão específica</h3><p>11 dos 15 documentos dão base para formular uma hipótese sobre mecanismo técnico, normativo ou procedimental. Isso não equivale à validação humana do rótulo.</p></article><article class="card"><span class="badge warn">Abstenção necessária</span><h3>Ambiguidade genérica</h3><p>4 justificativas apenas informam que o julgamento foi prejudicado. Sem mais evidência, seria inventado atribuir uma operação cognitiva precisa.</p></article><article class="card"><span class="badge">Controle de qualidade</span><h3>Figuras contam</h3><p>O FNDE 53 depende de diagrama CPM. Analisar somente a transcrição textual sem preservar o desenho torna o item inadequado para classificação técnica completa.</p></article><article class="card"><span class="badge">Próximo portão</span><h3>Classificação independente</h3><p>Precisamos do corpus completo, referências normativas versionadas e dois revisores separados. Só depois faz sentido medir a precisão de Jev, Laya e LLMs.</p></article></div></div></section>
<section id="resources" class="view"><div class="section"><h2>15 justificativas oficiais</h2><p class="sub">Selecione órgão ou tipo de decisão. Os rótulos são descritivos e não constituem diagnóstico validado de cada questão.</p><div class="controls"><input id="q" placeholder="Buscar termo, número, motivo..." aria-label="Pesquisar recursos"><select id="org"><option value="">Todos os órgãos</option><option>FNDE</option><option>TRT-10</option><option>Câmara dos Deputados</option></select><select id="state"><option value="">Todas as decisões</option><option>ANULAÇÃO</option><option>ALTERAÇÃO</option></select></div><div id="cases" class="case-grid"></div></div></section>
<section id="gabaritos" class="view"><div class="section"><h2>FNDE 2024 · Engenharia Civil</h2><p class="sub">70 itens específicos, questões 51–120; gabarito definitivo oficial. Não incluímos enunciados integrais. Um registro de gabarito não valida o mecanismo.</p><div class="controls"><select id="answer"><option value="">Todos</option><option value="C">Certo</option><option value="E">Errado</option><option value="X">Anulado</option></select><label style="display:flex;gap:8px;align-items:center;color:var(--muted);font-size:13px"><input id="onlychanged" type="checkbox" style="min-width:unset"> Somente com recurso</label></div><div class="tablebox"><table><thead><tr><th>Questão</th><th>Preliminar</th><th>Definitivo</th><th>Situação</th></tr></thead><tbody id="answers"></tbody></table></div></div></section>
<section id="methods" class="view"><div class="section"><h2>Protocolo, status e limites</h2><div class="case-grid"><article class="card"><h3>O que está documentado</h3><p>Quatro fontes FNDE: prova, gabaritos preliminar/definitivo e decisões de recursos. Verificações automatizadas confirmaram 70 números únicos e quatro diferenças entre gabaritos.</p></article><article class="card"><h3>O que não foi feito</h3><p>Nenhuma revisão dupla humana, nem execução de Jev/Laya/LLM. Não foram baixados os PDFs binários, nem extraídos 70 enunciados íntegros. Nenhum teste de eficácia H20.</p></article></div><div class="section"><h2>Documentos oficiais FNDE</h2><div id="sources" class="case-grid"></div></div><div class="section"><h2>Repositório e estudo</h2><p><a href="EXP012_RELATORIO_CIENTIFICO.md">Relatório científico completo</a> · <a href="PROCOLO_REVISAO_CEGA.md">Protocolo de validação</a> · <a href="15_recursos_evidencia.csv">Matriz de mecanismos</a></p></div></div></section>
<footer class="footer">Cultura Data-Driven · “A realidade dá sinais.” · Registro experimental EXP-012 · Versão 11/11/2026 · Sem dados pessoais publicados.</footer></main><script>const D=__DATA__;
const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct=v=>(100*v).toLocaleString('pt-BR',{maximumFractionDigits:2})+'%';
function renderBars(){document.querySelector('#bars').innerHTML=D.taxas.map(a=>`<div class="barrow"><span class="label">${E(a.orgao)} ${a.ano}</span><div class="track"><div class="fill" style="width:${Math.max(0,a.taxa*100/0.12)}%"></div></div><span class="numeric muted">${pct(a.taxa)}</span></div>`).join('')+`<p class="sub">A escala das barras vai de 0% a 12%. Totais: 7/80, 4/70, 4/70.</p>`}
function renderCases(){let q=document.querySelector('#q').value.toLocaleLowerCase('pt-BR'),org=document.querySelector('#org').value,state=document.querySelector('#state').value;let arr=D.recursos.filter(x=>(!org||x.orgao===org)&&(!state||x.situacao===state)&&JSON.stringify(x).toLocaleLowerCase('pt-BR').includes(q));document.querySelector('#cases').innerHTML=arr.map(x=>`<article class="card"><span class="mini">${E(x.orgao)} · ${x.ano} · QUESTÃO ${x.numero}</span><h3>${E(x.dimensão||x.dimensao)}</h3><span class="badge ${x.situacao==='ANULAÇÃO'?'warn':'ok'}">${E(x.situacao)}</span><p>${E(x.sintese)}</p><p class="muted">Mecanismo documental: ${E(x.mecanismo_documentado)}. Taxonomia: ${E(x.taxonomia_proposta)}.</p><p class="source"><a href="${E(x.url)}" target="_blank" rel="noopener noreferrer">Justificativa oficial</a> · ${x.evidencia_especifica?'Fundamento específico':'Motivo genérico; abstenção técnica'}</p></article>`).join('')||'<p class="empty">Nenhum caso corresponde ao filtro.</p>'}
function renderAnswers(){let v=document.querySelector('#answer').value,only=document.querySelector('#onlychanged').checked;let arr=D.itens.filter(x=>(!v||x.gabarito===v)&&(!only||x.recurso));document.querySelector('#answers').innerHTML=arr.map(x=>`<tr><td>${x.numero}</td><td>${E(x.preliminar)}</td><td><strong>${E(x.gabarito)}</strong></td><td>${x.recurso?'<span class="badge warn">Recurso</span>':'<small>Sem alteração</small>'}</td></tr>`).join('')||'<tr><td colspan="4">Nenhum item</td></tr>'}
function renderSources(){let labels={prova:'Prova oficial',preliminar:'Gabarito preliminar',definitivo:'Gabarito definitivo',recursos:'Justificativas oficiais',edital:'Edital de Engenharia Civil'};document.querySelector('#sources').innerHTML=Object.entries(D.fontes).map(([k,url])=>`<article class="card"><h3>${labels[k]||k}</h3><p><a href="${E(url)}" target="_blank" rel="noopener noreferrer">Abrir documento no Cebraspe</a></p></article>`).join('')}
for(const b of document.querySelectorAll('.tab'))b.addEventListener('click',()=>{document.querySelectorAll('.tab,.view').forEach(z=>z.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.target).classList.add('active')});
for(const s of ['q','org','state'])document.querySelector('#'+s).addEventListener('input',renderCases);for(const s of ['answer','onlychanged'])document.querySelector('#'+s).addEventListener('input',renderAnswers);renderBars();renderCases();renderAnswers();renderSources();</script></body></html>'''.replace('__DATA__',js)
(OUT/'index.html').write_text(htmlsrc,encoding='utf8')

# canonico append-only
old=(IN/'CDD_Intelligence_Canonico_v2_7_2026-11-11.md').read_text(encoding='utf8')
canon=old+f'''\n\n---\n\n# Adendo canônico v2.8 — EXP-012, {DATE}\n\n**Status:** auditoria documental e cruzamento de mecanismos concluídos; revisão dupla e modelos conectados NÃO executados. Mantidos integralmente H01–H20, H-ORI-01, critérios de evidência, histórico e experimentos anteriores.\n\n- **Novo corpus:** FNDE/2024, cargo Engenheiro Civil (998_FNDEINFRA_002_01), 70 gabaritos oficiais (51–120) indexados; só metadados/recursos, **sem 70 enunciados integrais**. PDFs consultados pela web, binários não baixados; não atribuir hash às fontes oficiais.\n- **Quatro eventos com recurso:** 53 E→X (redação/figura CPM), 62 C→E (ABNT NBR 6122/2022, anexo E), 87 E→X (redação), 104 C→E (escada acessível: banca indica mínimo 1,20 m, e não 1,50 m). Não equiparar explicação da banca à auditoria externa da norma.\n- **Comparação documental cumulativa:** Câmara/2012 7/80, TRT10/2025 4/70, FNDE/2024 4/70, **15/220** alterações/anulações no total. As 15 ocorrências são selecionadas após recursos e NÃO medem incidência de mecanismos no universo.\n- **Taxonomia e revisão:** 11/15 justificativas possuem motivo suficientemente específico para formular rótulo candidato; 4/15 são genéricas e exigem abstenção quanto ao mecanismo exato. Esta divisão é codificação exploratória não revisada independentemente. Rótulos Txx não homologados.\n- **D-012-01:** distinguir anulação por indeterminação, alteração C→E por mérito técnico e erro de transcrição; não tratar anulados como gabaritos binários.\n- **D-012-02:** preservar figuras essenciais e contexto de origem antes de classificar.\n- **D-012-03:** FNDE é **amostra externa retrospectiva**, não prova confirmatória cega, pois o gabarito e justificativas já foram consultados.\n- **D-012-04:** zero revisores humanos independentes, zero execuções Jev/Laya/LLM, H20 não testada; não afirmar métricas de acurácia nem ganho de aprendizagem.\n- **D-012-05:** publicar somente dados documentais, sínteses autorais, scripts e painel GitHub Pages; separar arquivos privados em biblioteca.\n- **Próximo portão:** obter textos oficiais integrais e referências normativas versionadas, congelar estudo em prova ainda não explorada, revisão dupla humana e inferência estruturada Jev/Laya/LLM sob mesmas condições.\n\nArtefatos: Biblioteca `/CDD_Intelligence/01_Experimentos/EXP-012` (SQLite, CSV, relatório, painel, script e manifesto). GitHub Pages em `/laboratorios/cdd-intelligence/exp012/` sujeito à confirmação de implantação; preservar EXP-009/010/011.\n'''
(OUT/'CDD_Intelligence_Canonico_v2_8_2026-11-11.md').write_text(canon,encoding='utf8')

# manifesto local; no official PDF downloaded
manifest={}
for p in OUT.iterdir():
 if p.is_file(): manifest[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
(OUT/'MANIFESTO_SHA256_LOCAL.json').write_text(json.dumps({'arquivos_locais':manifest,'pdfs_originais_no_container':False,'observacao':'Hashes não cobrem os PDFs oficiais; apenas artefatos próprios.'},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'metrics':metrics,'files':{p.name:p.stat().st_size for p in OUT.iterdir()}},ensure_ascii=False,indent=2))