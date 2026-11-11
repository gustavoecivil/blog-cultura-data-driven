#!/usr/bin/env python3
"""CDD Intelligence EXP-010 — deterministic multi-label triage; no Jev/Laya/LLM claims.
Run from EXP-010 folder with 'input' sibling containing EXP-009 inputs.
All labels are heuristic candidates. No answer key is read or needed.
"""
import csv, hashlib, json, math, re, shutil, sqlite3, statistics, unicodedata
from pathlib import Path
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

OUT=Path(__file__).resolve().parent
SRC=OUT.parent/'input'
# Can also run in a self-contained folder with input/ under the current directory
if not SRC.exists(): SRC=OUT/'input'

def read_csv(name,sep=';'):
    with (SRC/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f,delimiter=sep))

def write_csv(name, rows, sep=';'):
    if not rows:return
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=sep);w.writeheader();w.writerows(rows)

def dump(name, data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def norm(s):return unicodedata.normalize('NFKC',s).lower().replace('\u00a0',' ')

lex={
'T01':[r'\bclassificad',r'\bcategor',r'\bgrupo',r'\btipos?\b',r'\bfunda[cç][oõ]es?\b'],
'T02':[r'\bsondag',r'\bensaio',r'\bmedi[cç][aã]o',r'\bresist[eê]ncia',r'\bindicador',r'\bindice'],
'T03':[r'\bdispens',r'\bindependent',r'\bqualquer',r'\btod[ao]s?\b',r'\bnunca\b',r'\bsempre\b',r'\bno m[aá]ximo',r'\bno m[ií]nimo',r'\bsomente'],
'T04':[r'\bconcreto\b',r'\bdeforma',r'\bflu[eê]ncia',r'\bretra[cç][aã]o',r'\bdilata[cç]',r'\bcarga',r'\btens[aã]o'],
'T05':[r'\bdenomin',r'\bdefin',r'\bsignific',r'\bconceito',r'\bsigla',r'\bestados? limites?'],
'T06':[r'\b\d+[,.]?\d*\s*(?:cm|mm|m|%|kg|h|hora|dias?)\b',r'\bprodutividade\b',r'\bespa[cç]ad',r'\bc[aá]lcul',r'\bpercent',r'\b[áa]rea de a[cç]o'],
'T07':[r'\betapas?\b',r'\bsequ[eê]nci',r'\bproced',r'\bexecutad',r'\bpreench',r'\batualizad',r'\bprotocolo'],
'T08':[r'\bcompatib',r'\bharmonia',r'\bintegra[cç]',r'\binterfac',r'\bcompatibiliza'],
'T09':[r'\brefer[eê]ncia',r'\bconflito',r'\bdiverg[eê]n',r'\bfontes?\b',r'\bmanual',r'\bbibliogr'],
'T10':[r'\bor[cç]ament',r'\bcusto',r'\bmanuten[cç]',r'\bdi[aá]rio de obra',r'\bfiscaliza[cç]',r'\bplanejament'],
'T11':[r'\bnorma',r'\blei\b',r'\bn[rú]\s*\d+',r'\bart\b',r'\babnt\b',r'\bcreto',r'\bcontrat',r'\bdever[aáo]'],
}
prototypes={
'T01':'Classificar categoria técnica por suas propriedades, distinguir grupos de fundações superficiais e profundas, tipos e subclassificações.',
'T02':'Interpretar ensaios, medições de solo, sondagem SPT, resistência, indicadores e critérios de medição experimental.',
'T03':'Verificar condições de validade, exceções, escopo, quantificadores totais, sempre, nunca, dispensas e afirmações universais.',
'T04':'Interpretar modelos e fenômenos físicos: concretagem, carga, tensão, deformação, retração, fluência, dilatação e comportamento dos materiais.',
'T05':'Checar terminologia técnica exata, nomes, definições, siglas, significado de termos e conceitos de engenharia.',
'T06':'Efetuar cálculo quantitativo, unidades, comparações numéricas, área, bitola, espaçamento, índices, percentuais, produtividade.',
'T07':'Conferir sequência de procedimentos, fases, etapas executivas, responsabilidades e fluxo de documentação.',
'T08':'Verificar compatibilidade entre projetos e disciplinas, interfaces, harmonização, limites de garantias de coordenação.',
'T09':'Comparar normas, referências, fontes divergentes e bibliografia, condições de aplicabilidade e incerteza.',
'T10':'Avaliar gestão da construção, orçamento, manutenção, fiscalização, medição de obras, planejamento, controles e custos.',
'T11':'Aplicar norma técnica, legislação, lei, contratação pública, NR, ABNT e exigências normativas em sua vigência.',
}

codebook=read_csv('taxonomia_canonica_11.csv');codes=[r['codigo'] for r in codebook]
assert len(codes)==11 and set(codes)==set(lex)==set(prototypes)
previous=read_csv('predicoes_38_modelos_transparentes.csv')
texts=read_csv('enunciados_38_para_auditoria.csv',sep=',')
assert len(previous)==len(texts)==38
hash_text={r['hash_texto']:r for r in texts}
assert len(hash_text)==38
# Keep opaquely identified items in public outputs. Never use the answer-key tables.
linked=[]
for p in previous:
    e=hash_text.get(p['texto_sha256'])
    if e is None: raise RuntimeError('Source hash mismatch: '+p['sample_id'])
    assert len(e['texto'])>20
    linked.append((p,e))

v=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),strip_accents='unicode',sublinear_tf=True)
m=v.fit_transform([prototypes[k] for k in codes]+[e['texto'] for _,e in linked])
sims=cosine_similarity(m[len(codes):],m[:len(codes)])

def score_lex(t):
    t=norm(t)
    counts={k:sum(len(re.findall(p,t,re.I)) for p in lex[k]) for k in codes}
    hits={k:sorted({t[z.start():z.end()] for pat in lex[k] for z in re.finditer(pat,t,re.I)}) for k in codes}
    ranked=sorted(codes,key=lambda k:(-counts[k],k))
    # Multi-label heuristic, max 3; abstain with no score >=2.
    mx=counts[ranked[0]]
    selected=[k for k in ranked if counts[k]>=2 and counts[k]>=max(2,math.ceil(mx*.5))][:3]
    return selected,counts,hits

def score_sim(arr):
    values={k:float(arr[i]) for i,k in enumerate(codes)}
    ranked=sorted(codes,key=lambda k:-values[k]);mx=values[ranked[0]]
    selected=[k for k in ranked if values[k]>=.095 and values[k]>=mx*.72][:3]
    return selected,values

rows=[];outputs=[];source_refs=[]
for i,(p,e) in enumerate(linked):
    a,counts,hits=score_lex(e['texto']);b,sc=score_sim(sims[i]);
    union=sorted(set(a)|set(b));intersection=sorted(set(a)&set(b));
    j=len(intersection)/len(union) if union else 1.0
    # Cases only close automatically if both methods agree on at least 1 label; not validated.
    triage=('SEM_SINAL' if not union else 'INTERSECAO_PARCIAL' if intersection else 'SEM_CONVERGENCIA')
    priority=('ALTA' if not intersection else 'MEDIA')
    rows.append({'sample_id':p['sample_id'],'sha256_texto':p['texto_sha256'],'lexical_multilabel':'|'.join(a),'prototipos_multilabel':'|'.join(b),'intersecao':'|'.join(intersection),'uniao':'|'.join(union),'n_lexical':len(a),'n_prototipos':len(b),'jaccard':round(j,4),'status':triage,'prioridade':priority,'revisao':'PENDENTE_REVISAO_INDEPENDENTE'})
    outputs.append({'sample_id':p['sample_id'],'texto':e['texto'],'tipo_documento':'questao_oficial_transcricao_pendente_dupla_revisao','fonte_documental':e['fonte'],'pagina_pdf':e['pagina_pdf'],'codes_lexical':a,'codes_similaridade':b,'codes_intersecao':intersection,'codes_uniao':union,'indicios_lexicais':{k:hits[k] for k in a},'sinal':triage,'prioridade':priority,'hash_texto':p['texto_sha256']})
    source_refs.append({'sample_id':p['sample_id'],'item_interno':e['item_id'],'fonte':e['fonte'],'pagina_pdf':e['pagina_pdf'],'hash_texto':e['hash_texto'],'status':'CONFERENCIA_INDEPENDENTE_PENDENTE'})

n=len(rows);counts=Counter(x['status'] for x in rows)
old_concord=sum(1 for x in previous if x['concordam'] in ('1',1,True))
old_concord_defined=sum(1 for x in previous if x['concordam'] in ('1',1,True) and x['regra_lexical_T']!='INDETERMINAVEL')
metrics={
 'experimento':'EXP-010','data_registro':'2026-11-11','desenho':'multirotulo_nao_supervisionado_ate_3_categorias_por_metodo',
 'n':n,'codebook':'EXP009_CODEBOOK_V1','taxonomia':len(codes),'fontes':'Câmara 2012 e MPGO 2024; corpus exploratório reutilizado',
 'regra_A_cobertura':sum(bool(x['lexical_multilabel']) for x in rows),
 'regra_B_cobertura':sum(bool(x['prototipos_multilabel']) for x in rows),
 'alguma_convergencia':sum(x['status']=='INTERSECAO_PARCIAL' for x in rows),
 'sem_convergencia':sum(x['status']=='SEM_CONVERGENCIA' for x in rows),
 'dupla_abstencao':sum(x['status']=='SEM_SINAL' for x in rows),
 'jaccard_media':round(statistics.mean(x['jaccard'] for x in rows),4),
 'jaccard_media_sem_dupla_abstencao':round(statistics.mean(x['jaccard'] for x in rows if x['status']!='SEM_SINAL'),4) if any(x['status']!='SEM_SINAL' for x in rows) else None,
 'n_multiplos_A':sum(x['n_lexical']>1 for x in rows),'n_multiplos_B':sum(x['n_prototipos']>1 for x in rows),
 'exp009_concordancia_qualquer':old_concord,'exp009_concordancia_definida':old_concord_defined,
 'reviewed_gold_standard':0,'modelos_JEV_executados':0,'modelos_Laya_executados':0,'modelos_LLM_executados':0,
 'limites':['Aumento da cobertura NÃO equivale a melhora de precisão','Os dois algoritmos são baselines automáticos, não revisores independentes','Sem gabarito no treinamento nem inferência; nenhum valor mede chance de C/E','Amostra já explorada e transcrições sem dupla revisão'],
 'proxima_decisao':'revisar casos sem convergencia e montar amostra externa inédita antes da avaliação de acurácia',
}
write_csv('classificacao_multirotulo_38.csv',rows)
write_csv('rastreabilidade_interna_38.csv',source_refs)
write_csv('fila_revisao_38.csv',[r for r in rows if r['status']!='INTERSECAO_PARCIAL'])
dump('dados_painel.json',{'metricas':metrics,'taxonomia':codebook,'questoes':outputs})
dump('resultados_exp010.json',metrics)
# Public model payloads: do not send reference labels, origin, question number, gabarito, explanations, output from baseline.
with (OUT/'payload_externo_38_sem_gabarito.jsonl').open('w',encoding='utf-8') as f:
 for p,e in linked:
  f.write(json.dumps({'sample_id':p['sample_id'],'texto':e['texto'],'opcoes':{x['codigo']:x['criterio'] for x in codebook},'maximo_rotulos':3,'permitir_abstencao':True,'responder':'rotulos_e_justificativa_sem_gabarito'},ensure_ascii=False)+'\n')
# SQLite append only on a copy of EXP009; preserve all old tables.
dest=OUT/'cdd_intelligence_exp010.sqlite3'
shutil.copy2(SRC/'cdd_intelligence_exp009.sqlite3',dest)
cn=sqlite3.connect(dest)
cn.execute('''CREATE TABLE IF NOT EXISTS exp010_multirotulo(sample_id TEXT PRIMARY KEY, sha256_texto TEXT, lexical_json TEXT, prototipos_json TEXT, intersecao_json TEXT, uniao_json TEXT, jaccard REAL, status TEXT, versao TEXT)''')
cn.executemany('INSERT OR REPLACE INTO exp010_multirotulo VALUES (?,?,?,?,?,?,?,?,?)',[(r['sample_id'],r['sha256_texto'],json.dumps(r['lexical_multilabel'].split('|') if r['lexical_multilabel'] else []),json.dumps(r['prototipos_multilabel'].split('|') if r['prototipos_multilabel'] else []),json.dumps(r['intersecao'].split('|') if r['intersecao'] else []),json.dumps(r['uniao'].split('|') if r['uniao'] else []),r['jaccard'],r['status'],'EXP010_V1') for r in rows]);cn.commit()
assert cn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert cn.execute('SELECT COUNT(*) FROM exp010_multirotulo').fetchone()[0]==38
cn.close()
# QA structural (not technical truth)
for obj in [json.loads(x) for x in (OUT/'payload_externo_38_sem_gabarito.jsonl').read_text().splitlines()]:
 assert not (set(obj)&{'gabarito','resposta','item_id','numero','orgao','fonte','prova','evidencia_documental','classe_prevista'})
 assert len(obj['opcoes'])==11 and obj['maximo_rotulos']==3
assert len(set(r['sample_id'] for r in rows))==38
assert all(len(x['lexical_multilabel'].split('|'))<=3 for x in rows)
assert all(len(x['prototipos_multilabel'].split('|'))<=3 for x in rows)
print(json.dumps(metrics,ensure_ascii=False,indent=2))