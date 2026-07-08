from __future__ import annotations
import argparse, datetime as dt, json, subprocess
from pathlib import Path
VERSION="0.9.2"; MODE="nexus_wound_indexed_resume"
def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def run(root,argv): return subprocess.run(argv,cwd=str(root),text=True,capture_output=True,timeout=45)
def build_resume_packet(root, intent=""):
 root=Path(root).resolve(); st=run(root,["git","status","--short"]).stdout.splitlines(); head=run(root,["git","rev-parse","--short","HEAD"]).stdout.strip(); comp=root/"reports"/"nexus_compile_report_latest.json"; failed=[]; cstatus="missing"
 if comp.exists():
  try:
   data=json.loads(comp.read_text(encoding="utf-8-sig")); cstatus=data.get("status"); failed=[g.get("gate") for g in data.get("gates",[]) if g.get("status")=="fail"]
  except Exception as e: cstatus="parse_error"; failed=["compile_report_parse_error"]
 if failed: wound="compiler:"+",".join([x for x in failed if x]); rec="compiler-wound-focus"
 elif st: wound="dirty_worktree_requires_bounded_validation"; rec="bounded-validation"
 else: wound="none"; rec="release-seal"
 return {"version":VERSION,"generated_utc":utc(),"mode":MODE,"repo":str(root),"head":head,"intent":intent,"status":"resume_ready","active_wound":wound,"resume_from":rec,"recommended_loop":rec,"do_not_rerun":"passed gates whose input paths have not changed","git":{"dirty":bool(st),"changed_count":len(st),"status_short":st},"compiler":{"status":cstatus,"failed_gates":failed},"boundary":{"patch_enabled":False,"test_execution_enabled":False,"git_stage_enabled":False,"git_commit_enabled":False,"git_push_enabled":False,"autonomous_authority":False},"claim_boundary":"Read-only local resume evidence."}
def write_outputs(root,pkt):
 root=Path(root).resolve(); (root/"reports").mkdir(exist_ok=True); (root/"state"/"loops").mkdir(parents=True,exist_ok=True); enc=json.dumps(pkt,indent=2,sort_keys=True)+"\n"
 (root/"reports"/"nexus_resume_packet_latest.json").write_text(enc,encoding="utf-8"); (root/"state"/"loops"/"wound_indexed_resume_latest.json").write_text(enc,encoding="utf-8"); (root/"reports"/"nexus_resume_packet_latest.md").write_text(f"# NEXUS Wound-Indexed Resume Packet\n\n- Active wound: `{pkt['active_wound']}`\n- Recommended loop: `{pkt['recommended_loop']}`\n",encoding="utf-8")
def main(argv=None):
 ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--intent",default=""); ap.add_argument("--no-write",action="store_true"); ap.add_argument("--json",action="store_true"); a=ap.parse_args(argv); pkt=build_resume_packet(a.root,a.intent)
 if not a.no_write: write_outputs(a.root,pkt)
 print(json.dumps(pkt if a.json else {"mode":pkt["mode"],"status":pkt["status"],"active_wound":pkt["active_wound"],"recommended_loop":pkt["recommended_loop"]},indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
