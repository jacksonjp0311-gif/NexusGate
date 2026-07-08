from __future__ import annotations
import argparse,datetime as dt,json,platform,shutil,subprocess,sys
from pathlib import Path
VERSION='0.9.4'; MODE='nexus_ai_loop_toolkit'
TOOLS='repo-radar scope-hygiene claim-boundary-audit surface-map stale-surface-scan next-action-router handoff-pack dependency-preflight alignment-score boundary-scan release-brief evolution-radar idea-forge architecture-sketch patch-plan test-strategy debug-lens refactor-map ui-polish performance-scout docs-weaver memory-anchor command-palette session-brief commit-story risk-register paradise-index code-garden-map friction-detector local-oracle pair-programming-brief continuity-seal'.split()
BOUNDARY={'repo_mutation_enabled':False,'git_stage_enabled':False,'git_commit_enabled':False,'git_push_enabled':False,'network_enabled':False,'secrets_enabled':False,'autonomous_authority':False,'arbitrary_command_execution':False}
def _run(root,argv,timeout=30):
 try:
  p=subprocess.run(argv,cwd=str(root),capture_output=True,text=True,timeout=timeout,check=False); return {'ok':p.returncode==0,'returncode':p.returncode,'stdout':p.stdout[-3000:],'stderr':p.stderr[-2000:]}
 except Exception as e: return {'ok':False,'stderr':str(e)}
def _git(root,*a): return _run(root,['git',*a])
def _rj(p,d):
 try: return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else d
 except Exception: return d
def _status(root): return [x for x in _git(root,'status','--short').get('stdout','').splitlines() if x.strip()]
def _loops(root): return _rj(root/'loops/nexus_loop_registry.v0.1.json',{}).get('loops',{})
def _compiler(root): return _rj(root/'reports/nexus_compile_report_latest.json',{})
def _data(root,tool,intent):
 loops=_loops(root); status=_status(root); comp=_compiler(root); failed=[g.get('gate') for g in comp.get('gates',[]) if isinstance(g,dict) and g.get('status')=='fail']
 common={'head':_git(root,'rev-parse','--short','HEAD').get('stdout','').strip(),'dirty':bool(status),'changed_count':len(status),'loop_count':len(loops),'compiler_status':comp.get('status','unknown'),'failed_gates':failed,'intent':intent}
 if tool=='command-palette': common['commands']=[{'loop':k,'execute':f'python -m nexus_gate.loops.runner --root . --loop {k} --intent "<intent>" --execute --human-authorized --json'} for k in sorted(loops)]
 if tool=='local-oracle': common['recommended_loops']=['debug-recovery-chain','scope-hygiene','risk-register'] if failed or status else ['idea-forge','creative-build-chain','paradise-index']
 if tool=='paradise-index':
  groups={}
  for k,v in loops.items(): groups.setdefault(v.get('display_group','Meta Loops'),[]).append(k)
  common['groups']={k:sorted(v) for k,v in groups.items()}; common['personal_coding_paradise']=True
 if tool=='idea-forge': common['ideas']=[{'id':'loop-hud-cards','start_loop':'ui-polish'},{'id':'wound-timeline','start_loop':'debug-recovery-chain'},{'id':'agent-command-palette','start_loop':'command-palette'}]
 if tool=='patch-plan': common['steps']=['rehydrate','patch intended files only','emit JSON packet','targeted tests','bounded tests','compiler','stage intended only']
 if tool=='test-strategy': common['tests']=sorted(p.name for p in (root/'tests').glob('test_*.py'))[:80] if (root/'tests').exists() else []
 if tool=='continuity-seal': common['visible']={p:(root/p).exists() for p in ['README.md','chatgpt/scripts.md','loops/nexus_loop_registry.v0.1.json','state/loops/nexus_loop_cards_latest.json','docs/runtime/NEXUS_PERSONAL_CODING_PARADISE.md','reports/nexus_compile_report_latest.json']}
 return common
def build_toolkit_packet(root,tool,intent=''):
 root=Path(root).resolve()
 if tool not in TOOLS: return {'version':VERSION,'mode':MODE,'tool':tool,'status':'fail','known_tools':TOOLS,'boundary':BOUNDARY}
 return {'version':VERSION,'mode':MODE,'tool':tool,'intent':intent,'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'pass','boundary':BOUNDARY,'data':_data(root,tool,intent),'claim_boundary':'Read-only local loop toolkit packet. Not authority, not proof, not mutation.','outputs':{'report':f"reports/nexus_loop_toolkit_{tool.replace('-','_')}_latest.json",'state':f"state/loops/nexus_loop_toolkit_{tool.replace('-','_')}_latest.json"}}
def write_toolkit_packet(root,packet):
 root=Path(root).resolve(); key=str(packet.get('tool','unknown')).replace('-','_')
 for p in [root/'reports'/f'nexus_loop_toolkit_{key}_latest.json',root/'state/loops'/f'nexus_loop_toolkit_{key}_latest.json']:
  p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(packet,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def main(argv=None):
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--tool',default='repo-radar'); ap.add_argument('--intent',default=''); ap.add_argument('--json',action='store_true'); ap.add_argument('--list',action='store_true'); ap.add_argument('--no-write',action='store_true'); a=ap.parse_args(argv)
 if a.list: print(json.dumps({'version':VERSION,'mode':MODE,'tools':TOOLS,'boundary':BOUNDARY},indent=2,sort_keys=True)); return 0
 pkt=build_toolkit_packet(a.root,a.tool,a.intent)
 if not a.no_write: write_toolkit_packet(a.root,pkt)
 print(json.dumps(pkt if a.json else {'mode':pkt.get('mode'),'tool':pkt.get('tool'),'status':pkt.get('status')},indent=2,sort_keys=True)); return 0 if pkt.get('status')=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
