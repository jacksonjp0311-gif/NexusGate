from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
VERSION = "0.9.5"; SCHEMA = "NEXUS_LOOP_CARD.v0.9.5"
def _stage_summary(stages):
 out=[]
 for s in stages:
  item={'name':s.get('name','unnamed'),'type':s.get('type','unknown')}
  for k in ['command','path','loop']:
   if k in s: item[k]=s[k]
  out.append(item)
 return out
def build_loop_cards(root):
 root=Path(root).resolve(); reg=json.loads((root/'loops/nexus_loop_registry.v0.1.json').read_text(encoding='utf-8-sig')); cards=[]
 for i,lid in enumerate(sorted(reg.get('loops',{})),1):
  loop=reg['loops'][lid]
  cards.append({'schema':SCHEMA,'order':i,'loop_id':lid,'title':loop.get('title') or lid.replace('-',' ').title(),'description':loop.get('description',''),'function':loop.get('function') or loop.get('description',''),'operator_use':loop.get('operator_use','Use when this loop matches the active gate, wound, or validation need.'),'command_surface':f'python -m nexus_gate.loops.runner --root . --loop {lid} --intent "<intent>" --json','execute_surface':f'python -m nexus_gate.loops.runner --root . --loop {lid} --intent "<intent>" --execute --human-authorized --json','powershell_surface':f'.\\scripts\\nexus.ps1 meta-loop -Loop {lid} -Tag "<intent>"','ai_callable':bool(loop.get('ai_callable',True)),'local_only':bool(loop.get('local_only',True)),'mutates':bool(loop.get('mutates',False)),'requires_human_authorization':bool(loop.get('requires_human_authorization',False)),'stop_on_failure':bool(loop.get('stop_on_failure',False)),'authority_boundary':reg.get('authority_boundary',{}),'claim_boundary':reg.get('claim_boundary',''),'stages':_stage_summary(loop.get('stages',[])),'stages_summary':[f"{s.get('name')}:{s.get('type')}" for s in loop.get('stages',[])],'hud':{'card_kind':'nexus_loop','display_group':loop.get('display_group','Meta Loops'),'primary_action':'inspect_or_run_through_governed_loop_runner','human_card_ready':True,'ai_toolkit_ready':bool(loop.get('ai_callable',True)),'coding_paradise_ready':loop.get('display_group') in {'Coding Paradise','Creative','Design','Debug','Continuity','Operator Tools'}}})
 return {'schema':'NEXUS_LOOP_CARD_SET.v0.9.5','version':VERSION,'system':'NEXUS_LOOP_CARDS','generated_for':'NEXUS_GATE_v0.9.5','source_registry':'loops/nexus_loop_registry.v0.1.json','generated_at':datetime.now(timezone.utc).isoformat(),'card_count':len(cards),'cards':cards,'authority_boundary':reg.get('authority_boundary',{}),'claim_boundary':'Loop cards are HUD-readable surfaces. They grant no authority.'}
def write_loop_cards(root):
 root=Path(root).resolve(); pkt=build_loop_cards(root); (root/'state/loops').mkdir(parents=True,exist_ok=True); (root/'docs/runtime').mkdir(parents=True,exist_ok=True); enc=json.dumps(pkt,indent=2,sort_keys=True)+'\n'
 (root/'state/loops/nexus_loop_cards.v0.9.5.json').write_text(enc,encoding='utf-8'); (root/'state/loops/nexus_loop_cards_latest.json').write_text(enc,encoding='utf-8')
 lines=['# NEXUS Loop Cards','','NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.','v0.9.4 expands cards into a personal coding paradise: creative planning, debug recovery, command palette, local oracle, docs weaving, continuity seal, and safe shipping loops.','','Boundary: loop cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.','','## Card Surfaces','','- `state/loops/nexus_loop_cards.v0.9.5.json`','- `state/loops/nexus_loop_cards_latest.json`','- `python -m nexus_gate.loops.cards --root . --json`','- Spiral Core Portal option `[14] Nexus Loops / Cards`','','## Cards','']
 for c in pkt['cards']: lines += [f"### {c['title']}",'',f"- Loop: `{c['loop_id']}`",f"- Group: `{c['hud']['display_group']}`",f"- Function: {c['function']}",f"- Command: `{c['command_surface']}`",f"- Execute: `{c['execute_surface']}`",'']
 (root/'docs/runtime/NEXUS_LOOP_CARDS.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8'); return pkt
def main(argv=None):
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--json',action='store_true'); a=ap.parse_args(argv); pkt=write_loop_cards(Path(a.root)); print(json.dumps(pkt,indent=2,sort_keys=True) if a.json else f"wrote {pkt['card_count']} NEXUS loop cards"); return 0
if __name__=='__main__': raise SystemExit(main())
