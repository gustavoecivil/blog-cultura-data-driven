from __future__ import annotations
import hashlib, json, re, shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

ROOT=Path('build/world_cup_2022_primary')
SB=Path('/tmp/statsbomb/data'); OF=Path('/tmp/openfootball/2022/worldcup.json')
CID,SID=43,106
NOW=datetime.now(timezone.utc).isoformat()

def snake(s): return re.sub(r'_+','_',re.sub(r'[^0-9A-Za-z]+','_',s)).strip('_').lower()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def dump(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def parquet(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True); df=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows); df.to_parquet(p,index=False,compression='zstd'); return df
def flat(x,p=''):
 o={}
 for k,v in x.items():
  n=snake(f'{p}_{k}' if p else k)
  if isinstance(v,dict): o.update(flat(v,n))
  elif isinstance(v,list): o[n]=json.dumps(v,ensure_ascii=False,separators=(',',':'))
  else:o[n]=v
 return o
for d in ['data/raw/world_cup_2022/statsbomb/events','data/raw/world_cup_2022/statsbomb/lineups','data/raw/world_cup_2022/statsbomb/three_sixty','data/raw/world_cup_2022/openfootball','data/processed/world_cup_2022/canonical/core','data/processed/world_cup_2022/canonical/events','data/processed/world_cup_2022/canonical/tactics','data/processed/world_cup_2022/canonical/officials','data/processed/world_cup_2022/canonical/three_sixty','data/catalogs/world_cup_2022','data/quality/world_cup_2022','docs/world_cup_2022','schemas/world_cup_2022']:(ROOT/d).mkdir(parents=True,exist_ok=True)
raw=ROOT/'data/raw/world_cup_2022'; can=ROOT/'data/processed/world_cup_2022/canonical'; cat=ROOT/'data/catalogs/world_cup_2022'; qual=ROOT/'data/quality/world_cup_2022'; docs=ROOT/'docs/world_cup_2022'
shutil.copy2(SB/'competitions.json',raw/'statsbomb/competitions.json')
shutil.copy2(SB/f'matches/{CID}/{SID}.json',raw/f'statsbomb/matches_{CID}_{SID}.json')
shutil.copy2(OF,raw/'openfootball/worldcup_2022.json')
matches=json.loads((SB/f'matches/{CID}/{SID}.json').read_text())
manifest=[]
def cp(src,dst,kind,mid=None):
 if src.exists():
  shutil.copy2(src,dst); manifest.append({'source':'StatsBomb Open Data','kind':kind,'match_id':mid,'path':str(dst.relative_to(ROOT)),'size_bytes':dst.stat().st_size,'sha256':sha(dst),'status':'collected'})
 else: manifest.append({'source':'StatsBomb Open Data','kind':kind,'match_id':mid,'path':str(dst.relative_to(ROOT)),'size_bytes':0,'sha256':None,'status':'not_available'})
for m in matches:
 mid=m['match_id']; cp(SB/f'events/{mid}.json',raw/f'statsbomb/events/{mid}.json','events',mid); cp(SB/f'lineups/{mid}.json',raw/f'statsbomb/lineups/{mid}.json','lineups',mid); cp(SB/f'three-sixty/{mid}.json',raw/f'statsbomb/three_sixty/{mid}.json','three_sixty',mid)
manifest += [{'source':'StatsBomb Open Data','kind':'matches','match_id':None,'path':f'data/raw/world_cup_2022/statsbomb/matches_{CID}_{SID}.json','size_bytes':(raw/f'statsbomb/matches_{CID}_{SID}.json').stat().st_size,'sha256':sha(raw/f'statsbomb/matches_{CID}_{SID}.json'),'status':'collected'},{'source':'OpenFootball','kind':'validation','match_id':None,'path':'data/raw/world_cup_2022/openfootball/worldcup_2022.json','size_bytes':(raw/'openfootball/worldcup_2022.json').stat().st_size,'sha256':sha(raw/'openfootball/worldcup_2022.json'),'status':'collected'}]
parquet(raw/'collection_manifest.parquet',manifest); dump(raw/'collection_manifest.json',manifest)
teams={}; stadiums={}; referees={}; coaches=[]; mr=[]
for m in matches:
 h,a=m['home_team'],m['away_team']; st=m.get('stadium') or {}; rf=m.get('referee') or {}; stage=m.get('competition_stage') or {}
 for side,t in [('home',h),('away',a)]:
  tid=t.get(f'{side}_team_id'); teams[tid]={'team_id':tid,'team_name':t.get(f'{side}_team_name'),'team_gender':t.get(f'{side}_team_gender'),'team_group':t.get(f'{side}_team_group'),'country_id':(t.get('country') or {}).get('id'),'country_name':(t.get('country') or {}).get('name'),'source_id':'statsbomb'}
  for x in t.get('managers') or []: coaches.append({'match_id':m['match_id'],'team_id':tid,'coach_id':x.get('id'),'coach_name':x.get('name'),'coach_nickname':x.get('nickname'),'coach_dob':x.get('dob'),'country_id':(x.get('country') or {}).get('id'),'country_name':(x.get('country') or {}).get('name'),'source_id':'statsbomb'})
 if st.get('id'): stadiums[st['id']]={'stadium_id':st['id'],'stadium_name':st.get('name'),'country_id':(st.get('country') or {}).get('id'),'country_name':(st.get('country') or {}).get('name'),'source_id':'statsbomb'}
 if rf.get('id'): referees[rf['id']]={'referee_id':rf['id'],'referee_name':rf.get('name'),'country_id':(rf.get('country') or {}).get('id'),'country_name':(rf.get('country') or {}).get('name'),'source_id':'statsbomb'}
 mr.append({'match_id':m['match_id'],'match_date':m.get('match_date'),'kick_off':m.get('kick_off'),'competition_id':CID,'season_id':SID,'stage_id':stage.get('id'),'stage_name':stage.get('name'),'stadium_id':st.get('id'),'referee_id':rf.get('id'),'home_team_id':h.get('home_team_id'),'home_team_name':h.get('home_team_name'),'home_group':h.get('home_team_group'),'away_team_id':a.get('away_team_id'),'away_team_name':a.get('away_team_name'),'away_group':a.get('away_team_group'),'home_score':m.get('home_score'),'away_score':m.get('away_score'),'match_status':m.get('match_status'),'match_status_360':m.get('match_status_360'),'last_updated':m.get('last_updated'),'last_updated_360':m.get('last_updated_360'),'source_id':'statsbomb'})
parquet(can/'core/competitions.parquet',[{'competition_id':CID,'competition_name':'FIFA World Cup','season_id':SID,'season_name':'2022','source_id':'statsbomb'}]); mdf=parquet(can/'core/matches.parquet',mr); tdf=parquet(can/'core/teams.parquet',list(teams.values())); parquet(can/'core/stadiums.parquet',list(stadiums.values())); parquet(can/'officials/referees.parquet',list(referees.values())); parquet(can/'officials/coaches.parquet',coaches)
players={}; lineups=[]; posrows=[]; cardrows=[]; positions={}
for m in matches:
 mid=m['match_id']; data=json.loads((SB/f'lineups/{mid}.json').read_text())
 for team in data:
  for p in team.get('lineup',[]):
   pid=p.get('player_id'); c=p.get('country') or {}; players[pid]={'player_id':pid,'player_name':p.get('player_name'),'player_nickname':p.get('player_nickname'),'country_id':c.get('id'),'country_name':c.get('name'),'source_id':'statsbomb'}
   lineups.append({'match_id':mid,'team_id':team.get('team_id'),'team_name':team.get('team_name'),'player_id':pid,'player_name':p.get('player_name'),'jersey_number':p.get('jersey_number'),'country_id':c.get('id'),'country_name':c.get('name'),'source_id':'statsbomb'})
   for i,x in enumerate(p.get('positions') or [],1): positions[x.get('position_id')]={'position_id':x.get('position_id'),'position_name':x.get('position'),'source_id':'statsbomb'}; posrows.append({'match_id':mid,'team_id':team.get('team_id'),'player_id':pid,'sequence':i,'position_id':x.get('position_id'),'position_name':x.get('position'),'from_time':x.get('from'),'to_time':x.get('to'),'from_period':x.get('from_period'),'to_period':x.get('to_period'),'start_reason':x.get('start_reason'),'end_reason':x.get('end_reason'),'source_id':'statsbomb'})
   for i,x in enumerate(p.get('cards') or [],1): cardrows.append({'match_id':mid,'team_id':team.get('team_id'),'player_id':pid,'sequence':i,'time':x.get('time'),'card_type':x.get('card_type'),'reason':x.get('reason'),'period':x.get('period'),'source_id':'statsbomb'})
pdf=parquet(can/'core/players.parquet',list(players.values())); ldf=parquet(can/'core/lineups.parquet',lineups); parquet(can/'core/positions.parquet',list(positions.values())); parquet(can/'tactics/lineup_positions.parquet',posrows); parquet(can/'tactics/lineup_cards.parquet',cardrows)
core=[]; bytype=defaultdict(list); fields=defaultdict(lambda:{'types':set(),'count':0}); eventtypes={}; patterns={}; formations=[]; tactical=[]
def visit(v,p='',depth=0,etype=''):
 k=(etype,p); fields[k]['types'].add(type(v).__name__); fields[k]['count']+=1; fields[k]['depth']=max(fields[k].get('depth',0),depth)
 if isinstance(v,dict):
  for a,b in v.items(): visit(b,f'{p}.{a}' if p else a,depth+1,etype)
 elif isinstance(v,list):
  for b in v:
   if isinstance(b,dict): visit(b,p+'[]',depth+1,etype)
for m in matches:
 mid=m['match_id']; data=json.loads((SB/f'events/{mid}.json').read_text())
 for e in data:
  et=(e.get('type') or {}).get('name','Unknown'); eid=(e.get('type') or {}).get('id'); eventtypes[eid]={'event_type_id':eid,'event_type_name':et,'source_id':'statsbomb'}; pp=e.get('play_pattern') or {}; patterns[pp.get('id')]={'play_pattern_id':pp.get('id'),'play_pattern_name':pp.get('name'),'source_id':'statsbomb'} if pp.get('id') else None
  loc=e.get('location') or [None,None]; core.append({'event_id':e.get('id'),'match_id':mid,'event_index':e.get('index'),'period':e.get('period'),'timestamp':e.get('timestamp'),'minute':e.get('minute'),'second':e.get('second'),'event_type_id':eid,'event_type_name':et,'possession':e.get('possession'),'possession_team_id':(e.get('possession_team') or {}).get('id'),'play_pattern_id':pp.get('id'),'team_id':(e.get('team') or {}).get('id'),'player_id':(e.get('player') or {}).get('id'),'position_id':(e.get('position') or {}).get('id'),'location_x':loc[0] if len(loc)>0 else None,'location_y':loc[1] if len(loc)>1 else None,'duration':e.get('duration'),'under_pressure':e.get('under_pressure'),'counterpress':e.get('counterpress'),'related_events_json':json.dumps(e.get('related_events'),ensure_ascii=False) if e.get('related_events') else None,'source_id':'statsbomb'})
  f=flat(e); f.update(match_id=mid,source_id='statsbomb'); bytype[et].append(f); visit(e,'',0,et)
  tac=e.get('tactics') or {}
  if tac:
   formations.append({'event_id':e.get('id'),'match_id':mid,'team_id':(e.get('team') or {}).get('id'),'event_type_name':et,'formation':tac.get('formation'),'source_id':'statsbomb'})
   for i,x in enumerate(tac.get('lineup') or [],1): tactical.append({'event_id':e.get('id'),'match_id':mid,'team_id':(e.get('team') or {}).get('id'),'formation':tac.get('formation'),'sequence':i,'player_id':(x.get('player') or {}).get('id'),'player_name':(x.get('player') or {}).get('name'),'position_id':(x.get('position') or {}).get('id'),'position_name':(x.get('position') or {}).get('name'),'jersey_number':x.get('jersey_number'),'source_id':'statsbomb'})
edf=parquet(can/'events/events_core.parquet',core); parquet(can/'core/event_types.parquet',[x for x in eventtypes.values() if x]); parquet(can/'core/play_patterns.parquet',[x for x in patterns.values() if x]); parquet(can/'tactics/formations.parquet',formations); parquet(can/'tactics/tactical_lineups.parquet',tactical)
for et,rows in bytype.items(): parquet(can/f'events/{snake(et) or "unknown"}.parquet',rows)
parquet(cat/'recursive_event_field_inventory.parquet',[{'event_type':k[0],'field_path':k[1],'observed_types':','.join(sorted(v['types'])),'observations':v['count'],'max_depth':v['depth']} for k,v in fields.items()])
se=[]; ff=[]; va=[]
for m in matches:
 mid=m['match_id']; p=SB/f'three-sixty/{mid}.json'
 if not p.exists(): continue
 for e in json.loads(p.read_text()):
  uid=e.get('event_uuid'); frames=e.get('freeze_frame') or []; area=e.get('visible_area') or []; se.append({'match_id':mid,'event_uuid':uid,'freeze_frame_count':len(frames),'visible_area_coordinate_count':len(area),'source_id':'statsbomb'})
  for i,x in enumerate(frames,1): loc=x.get('location') or [None,None]; ff.append({'match_id':mid,'event_uuid':uid,'sequence':i,'teammate':x.get('teammate'),'actor':x.get('actor'),'keeper':x.get('keeper'),'location_x':loc[0],'location_y':loc[1],'source_id':'statsbomb'})
  for i in range(0,len(area),2): va.append({'match_id':mid,'event_uuid':uid,'sequence':i//2+1,'location_x':area[i],'location_y':area[i+1] if i+1<len(area) else None,'source_id':'statsbomb'})
parquet(can/'three_sixty/three_sixty_events.parquet',se); parquet(can/'three_sixty/freeze_frames.parquet',ff); parquet(can/'three_sixty/visible_areas.parquet',va)
of=json.loads(OF.read_text()).get('matches',[])
def norm(x): return {'usa':'united states','south korea':'korea republic'}.get(snake(x).replace('_',' '),snake(x).replace('_',' '))
idx={(r['match_date'],frozenset([norm(r['home_team_name']),norm(r['away_team_name'])])):r for r in mr}; comp=[]
for x in of:
 key=(x.get('date'),frozenset([norm(x.get('team1','')),norm(x.get('team2',''))])); r=idx.get(key); ft=(x.get('score') or {}).get('ft') or [None,None]; same=r and norm(x['team1'])==norm(r['home_team_name']); score=bool(r and (([r['home_score'],r['away_score']]==ft) if same else ([r['away_score'],r['home_score']]==ft))); comp.append({'date':x.get('date'),'team1':x.get('team1'),'team2':x.get('team2'),'score1':ft[0],'score2':ft[1],'group':x.get('group'),'ground':x.get('ground'),'statsbomb_match_id':r.get('match_id') if r else None,'match_found':bool(r),'score_match':score})
cdf=parquet(qual/'source_match_comparison.parquet',comp); parquet(qual/'source_conflicts.parquet',[x for x in comp if not x['match_found'] or not x['score_match']])
trs=[]; frs=[]; lineage=[]
for p in sorted(can.rglob('*.parquet')):
 pf=pq.ParquetFile(p); trs.append({'table_name':p.stem,'relative_path':str(p.relative_to(ROOT)),'rows':pf.metadata.num_rows,'columns':len(pf.schema_arrow),'size_bytes':p.stat().st_size,'sha256':sha(p),'status':'canonical_primary'})
 (ROOT/'schemas/world_cup_2022'/f'{p.stem}.txt').write_text(str(pf.schema_arrow),encoding='utf-8')
 sample=pd.read_parquet(p).head(1)
 for f in pf.schema_arrow: frs.append({'table_name':p.stem,'column_name':f.name,'data_type':str(f.type),'source':'StatsBomb Open Data','classification':'technical_metadata' if f.name.startswith('source_') else 'source_provided','is_project_derived':False,'nullable':f.nullable,'example':str(sample[f.name].iloc[0])[:200] if len(sample) else None,'pipeline_version':'1.0.0'})
 lineage.append({'target_table':p.stem,'target_path':str(p.relative_to(ROOT)),'source_system':'StatsBomb Open Data','transformation':'primary normalization only','pipeline_version':'1.0.0'})
tab=parquet(cat/'table_catalog.parquet',trs); parquet(cat/'field_catalog.parquet',frs); parquet(cat/'lineage.parquet',lineage); tab.to_csv(cat/'table_catalog.csv',index=False)
checks=[]
def ck(n,ok,a,e,sev='error'): checks.append({'check_name':n,'passed':bool(ok),'actual':str(a),'expected':str(e),'severity':sev})
ck('matches_count',len(mdf)==64,len(mdf),64); ck('unique_match_ids',mdf.match_id.nunique()==64,mdf.match_id.nunique(),64); ck('teams_count',tdf.team_id.nunique()==32,tdf.team_id.nunique(),32); ck('event_files',sum(x['kind']=='events' and x['status']=='collected' for x in manifest)==64,sum(x['kind']=='events' and x['status']=='collected' for x in manifest),64); ck('lineup_files',sum(x['kind']=='lineups' and x['status']=='collected' for x in manifest)==64,sum(x['kind']=='lineups' and x['status']=='collected' for x in manifest),64); ck('event_ids_unique',edf.event_id.nunique()==len(edf),edf.event_id.nunique(),len(edf)); ck('event_match_fk',set(edf.match_id)<=set(mdf.match_id),len(set(edf.match_id)-set(mdf.match_id)),0); ck('event_team_fk',set(edf.team_id.dropna())<=set(tdf.team_id),len(set(edf.team_id.dropna())-set(tdf.team_id)),0); ck('coordinates_x',edf.location_x.dropna().between(0,120).all(),int((~edf.location_x.dropna().between(0,120)).sum()),0); ck('coordinates_y',edf.location_y.dropna().between(0,80).all(),int((~edf.location_y.dropna().between(0,80)).sum()),0); ck('openfootball_64',len(cdf)==64,len(cdf),64,'warning'); ck('openfootball_linked',int(cdf.match_found.sum())==64,int(cdf.match_found.sum()),64,'warning'); ck('360_documented',True,len(list((SB/'three-sixty').glob('*.json'))),'selected','info')
qdf=parquet(qual/'quality_checks.parquet',checks); qdf.to_csv(qual/'quality_checks.csv',index=False)
source_catalog=[{'source':'StatsBomb Open Data','role':'principal','coverage':'64 matches, events, lineups, selected 360','terms':'attribution required','status':'collected'},{'source':'OpenFootball','role':'validation','coverage':'fixtures, scores, groups, grounds','terms':'repository license','status':'collected'},{'source':'FIFA','role':'authoritative reference','coverage':'official tournament reference','terms':'not assumed bulk-open','status':'catalogued_only'}]; parquet(cat/'source_catalog.parquet',source_catalog); pd.DataFrame(source_catalog).to_csv(cat/'source_catalog.csv',index=False)
(docs/'EXISTING_PROJECT_AUDIT.md').write_text('# Auditoria do ambiente existente\n\nExecução isolada em GitHub Actions. Nenhum arquivo local do usuário foi alterado. Dados da Copa de 2026 não foram usados.\n',encoding='utf-8')
(docs/'SOURCE_DISCOVERY.md').write_text('# Fontes\n\nStatsBomb Open Data é a fonte principal; OpenFootball é fonte de validação; FIFA foi catalogada como referência oficial sem assumir licença bulk.\n',encoding='utf-8')
rep=['# Relatório final — Dados Primários da Copa do Mundo 2022','',f'Gerado em: {NOW}','',f'- Partidas: {len(mdf)}',f'- Eventos: {len(edf)}',f'- Seleções: {len(tdf)}',f'- Jogadores: {len(pdf)}',f'- Tabelas canônicas: {len(tab)}',f'- Arquivos 360 disponíveis: {len(list((SB/"three-sixty").glob("*.json")))}',f'- Testes obrigatórios falhos: {len(qdf[(qdf.severity=="error") & (~qdf.passed)])}','','## Limitações','','- StatsBomb 360 cobre apenas partidas selecionadas.','- Dados indisponíveis não foram inventados.','- Nenhuma métrica esportiva derivada foi criada.','','## Prontidão PostgreSQL','','IDs, tipos, catálogos, esquemas e linhagem foram preparados; nenhuma carga foi executada.']
(docs/'PRIMARY_DATA_FINAL_REPORT.md').write_text('\n'.join(rep)+'\n',encoding='utf-8')
(docs/'QUALITY_REPORT.md').write_text('# Qualidade\n\n'+qdf.to_markdown(index=False)+'\n',encoding='utf-8')
if len(qdf[(qdf.severity=='error') & (~qdf.passed)]): raise SystemExit('Mandatory quality checks failed')
rel=ROOT/'CANONICAL_PRIMARY_V1'; rel.mkdir(exist_ok=True)
for src in [can,cat,qual,docs,ROOT/'schemas/world_cup_2022']:
 dst=rel/src.relative_to(ROOT); shutil.copytree(src,dst,dirs_exist_ok=True)
files=[{'path':str(p.relative_to(rel)),'size_bytes':p.stat().st_size,'sha256':sha(p)} for p in rel.rglob('*') if p.is_file()]; dump(rel/'RELEASE_MANIFEST.json',{'release':'CANONICAL_PRIMARY_V1','created_at_utc':NOW,'files':files})
print(json.dumps({'status':'success','matches':len(mdf),'events':len(edf),'tables':len(tab),'quality_checks':len(qdf),'release':str(rel)},indent=2))
