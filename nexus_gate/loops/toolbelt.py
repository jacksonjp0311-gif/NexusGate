
from __future__ import annotations
import argparse, datetime as _dt, json, subprocess
from pathlib import Path
from typing import Any
VERSION="0.9.6"; MODE="nexus_ai_toolbelt"
BOUNDARY={"repo_mutation_enabled":False,"git_stage_enabled":False,"git_commit_enabled":False,"git_push_enabled":False,"network_enabled":False,"secrets_enabled":False,"autonomous_authority":False,"arbitrary_command_execution":False}
GROUPS=[
 {"group_id":"orient","title":"Orient","purpose":"Rehydrate, see status, and route next action.","loops":["repo-radar","toolbelt-index","toolbelt-console","toolbelt-dashboard","toolbelt-next","next-action-router","local-oracle"],"chain":"repo-radar -> toolbelt-console -> toolbelt-next"},
 {"group_id":"plan","title":"Plan","purpose":"Turn intent into architecture, patch plan, and tests.","loops":["idea-forge","architecture-sketch","patch-plan","test-strategy","creative-build-chain","pair-programming-brief"],"chain":"idea-forge -> architecture-sketch -> patch-plan -> test-strategy"},
 {"group_id":"debug","title":"Debug","purpose":"Narrow failures into wounds.","loops":["debug-lens","wound-indexed-resume","compiler-wound-focus","debug-recovery-chain","failure-intelligence","friction-detector"],"chain":"debug-lens -> wound-indexed-resume -> compiler-wound-focus"},
 {"group_id":"hygiene","title":"Hygiene","purpose":"Keep scope, claims, stale surfaces, and authority clean.","loops":["scope-hygiene","claim-boundary-audit","boundary-scan","stale-surface-scan","risk-register","dependency-preflight"],"chain":"scope-hygiene -> boundary-scan -> claim-boundary-audit"},
 {"group_id":"ship","title":"Ship","purpose":"Validate, summarize, seal, and prepare human-authorized mutation.","loops":["bounded-validation","release-brief","toolbelt-ship","toolbelt-ship-console","release-seal","commit-story","continuity-seal"],"chain":"bounded-validation -> release-brief -> release-seal -> commit-story"},
 {"group_id":"memory","title":"Memory","purpose":"Preserve continuity.","loops":["handoff-pack","session-brief","memory-anchor","docs-weaver","continuity-seal","paradise-index"],"chain":"handoff-pack -> session-brief -> memory-anchor -> continuity-seal"},
 {"group_id":"ui","title":"UI / HUD","purpose":"Support cards, command palette, UI polish, and code garden maps.","loops":["hud-loop-sync","command-palette","ui-polish","code-garden-map","surface-map"],"chain":"hud-loop-sync -> command-palette -> ui-polish"}]
VIEWS={"index":"toolbelt-index","start":"repo-radar","dashboard":"toolbelt-next","next":"next-action-router","ship":"release-brief"}
def _utc(): return _dt.datetime.now(_dt.timezone.utc).isoformat()
def _read_json(p:Path,d:Any):
 try:
  return json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else d
 except Exception: return d
def _write_json(p:Path,o:Any): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def _run(root:Path,args:list[str]):
 try:
  p=subprocess.run(args,cwd=str(root),capture_output=True,text=True,timeout=20,check=False); return {"ok":p.returncode==0,"returncode":p.returncode,"stdout":(p.stdout or "")[-2000:],"stderr":(p.stderr or "")[-1000:]}
 except Exception as e: return {"ok":False,"stderr":str(e)}
def _status(root:Path):
 out=_run(root,["git","status","--short"]).get("stdout",""); lines=[x for x in out.splitlines() if x.strip()]
 comp=_read_json(root/"reports"/"nexus_compile_report_latest.json",{})
 failed=[g.get("gate") for g in comp.get("gates",[]) if isinstance(g,dict) and g.get("status")=="fail"]
 return {"head":_run(root,["git","rev-parse","--short","HEAD"]).get("stdout","").strip(),"dirty":bool(lines),"changed_count":len(lines),"status_preview":lines[:40],"compiler_status":comp.get("status","unknown"),"failed_gates":failed}
def _cards(cards): return {c.get("loop_id"):c for c in cards.get("cards",[]) if isinstance(c,dict) and c.get("loop_id")}
def _gstatus(g,loops,cards):
 ids=list(g["loops"]); avail=[i for i in ids if i in loops]; miss=[i for i in ids if i not in loops]; cmiss=[i for i in ids if i not in cards]
 return {**g,"available_loops":avail,"missing_loops":miss,"missing_cards":cmiss,"ready":not miss and not cmiss,"commands":[f'python -m nexus_gate.loops.runner --root . --loop {i} --intent "<intent>" --json' for i in avail],"execute_commands":[f'python -m nexus_gate.loops.runner --root . --loop {i} --intent "<intent>" --execute --human-authorized --json' for i in avail]}
def build_toolbelt_packet(root:str|Path,intent:str="",view:str="dashboard"):
 root=Path(root).resolve(); view=view if view in VIEWS else "dashboard"
 reg=_read_json(root/"loops"/"nexus_loop_registry.v0.1.json",{}); cards=_cards(_read_json(root/"state"/"loops"/"nexus_loop_cards_latest.json",{})); loops=reg.get("loops",{})
 groups=[_gstatus(g,loops,cards) for g in GROUPS]; missing=sorted({m for g in groups for m in g["missing_loops"]}); st=_status(root)
 if st["failed_gates"]: rec,why="debug-recovery-chain","compiler report contains failed gates"
 elif st["dirty"]: rec,why="scope-hygiene","working tree has local changes"
 elif view=="ship": rec,why="release-brief","ship view requested"
 elif view=="start": rec,why="repo-radar","start view requested"
 else: rec,why="evolution-radar","tree appears ready for next evolution planning"
 return {"schema":"NEXUS_AI_TOOLBELT.v0.9.6","version":VERSION,"mode":MODE,"view":view,"generated_utc":_utc(),"intent":intent,"root":str(root),"status":"pass" if not missing else "review","repo_status":st,"recommended_next_loop":rec,"recommendation_reason":why,"toolbelt_group_count":len(groups),"ready_group_count":sum(1 for g in groups if g["ready"]),"loop_count":len(loops),"card_count":len(cards),"groups":groups,"missing_loop_count":len(missing),"missing_loops":missing,"powershell_surface":".\\scripts\\nexus.ps1 toolbelt -Tag \"<intent>\"","bash_surface":"bash scripts/nexus.sh toolbelt \"<intent>\"","process_chains":{"start":"toolbelt-start -> toolbelt-dashboard -> next-action-router","build":"idea-forge -> architecture-sketch -> patch-plan -> test-strategy","debug":"debug-lens -> wound-indexed-resume -> compiler-wound-focus","ship":"scope-hygiene -> boundary-scan -> release-brief -> release-seal","continuity":"handoff-pack -> session-brief -> memory-anchor -> continuity-seal"},"boundary":BOUNDARY,"claim_boundary":"The AI Toolbelt Console is a local read-only operator cockpit. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof."}
def write_toolbelt(root:str|Path,intent:str="",view:str="dashboard"):
 root=Path(root).resolve(); p=build_toolbelt_packet(root,intent,view)
 _write_json(root/"state"/"loops"/"nexus_toolbelt.v0.9.6.json",p); _write_json(root/"state"/"loops"/"nexus_toolbelt_latest.json",p); _write_json(root/"reports"/"nexus_toolbelt_latest.json",p)
 lines=["# NEXUS AI Toolbelt","","The NEXUS AI Toolbelt is the operator-visible map of local, AI-callable loops.","It lets ChatGPT/Codex recommend useful local loops without granting direct repo authority.","","Boundary: the toolbelt is an index and packet emitter only. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.","","## Fast Start","","```powershell",".\\scripts\\nexus.ps1 toolbelt",".\\scripts\\nexus.ps1 toolbelt-start -Tag \"<intent>\"",".\\scripts\\nexus.ps1 toolbelt-next -Tag \"<intent>\"",".\\scripts\\nexus.ps1 toolbelt-ship -Tag \"<intent>\"","```","","```bash","bash scripts/nexus.sh toolbelt \"<intent>\"","bash scripts/nexus.sh toolbelt-next \"<intent>\"","```","","## Default Process","","```text","Start      -> toolbelt-start -> toolbelt-dashboard -> next-action-router","Build      -> idea-forge -> architecture-sketch -> patch-plan -> test-strategy","Debug      -> debug-lens -> wound-indexed-resume -> compiler-wound-focus","Ship       -> scope-hygiene -> boundary-scan -> release-brief -> release-seal","Continuity -> handoff-pack -> session-brief -> memory-anchor -> continuity-seal","```","","## Toolbelt Groups",""]
 for g in p["groups"]: lines += [f"### {g['title']}","",f"- Purpose: {g['purpose']}",f"- Chain: `{g['chain']}`",f"- Ready: `{str(g['ready']).lower()}`",f"- Loops: `{', '.join(g['loops'])}`",""]
 (root/"docs"/"runtime").mkdir(parents=True,exist_ok=True); (root/"docs"/"runtime"/"NEXUS_AI_TOOLBELT.md").write_text("\n".join(lines).rstrip()+"\n",encoding="utf-8"); return p
def main(argv=None):
 ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--intent",default=""); ap.add_argument("--view",default="dashboard",choices=sorted(VIEWS)); ap.add_argument("--json",action="store_true"); a=ap.parse_args(argv)
 p=write_toolbelt(a.root,a.intent,a.view); print(json.dumps(p,indent=2,sort_keys=True) if a.json else f"wrote NEXUS AI Toolbelt {p['view']} {p['status']} next={p['recommended_next_loop']}"); return 0 if p["status"] in {"pass","review"} else 1
if __name__=="__main__": raise SystemExit(main())
