from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
VERSION="0.9.2"; MODE="nexus_bounded_per_file_tests"
def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def discover_test_files(root, pattern="test_*.py"):
 root=Path(root).resolve(); tests=root/"tests"; found=set()
 try:
  p=subprocess.run(["git","ls-files","tests/test_*.py"],cwd=str(root),text=True,capture_output=True,timeout=30)
  if p.returncode==0:
   for line in p.stdout.splitlines():
    q=root/line.strip()
    if q.exists() and q.name.startswith("test_") and q.suffix==".py": found.add(q.resolve())
 except Exception: pass
 if tests.exists():
  for q in tests.glob(pattern):
   if q.is_file() and q.name.startswith("test_") and q.suffix==".py" and ".bak" not in q.name: found.add(q.resolve())
 return [str(q.relative_to(root)).replace("\\","/") for q in sorted(found)]
def run_bounded_tests(root,pattern="test_*.py",timeout_seconds=90):
 root=Path(root).resolve(); files=discover_test_files(root,pattern); results=[]; failures=[]
 for rel in files:
  name=Path(rel).name; cmd=[sys.executable,"-m","unittest","discover","-s","tests","-p",name,"-v"]
  try: p=subprocess.run(cmd,cwd=str(root),text=True,capture_output=True,timeout=timeout_seconds); item={"file":rel,"returncode":p.returncode,"stdout_tail":p.stdout[-1200:],"stderr_tail":p.stderr[-1200:]}
  except subprocess.TimeoutExpired as e: item={"file":rel,"returncode":124,"stdout_tail":"","stderr_tail":str(e)[-1200:],"timeout_seconds":timeout_seconds}
  results.append(item)
  if item["returncode"]!=0: failures.append(item); break
 return {"version":VERSION,"generated_utc":utc(),"mode":MODE,"status":"pass" if not failures else "fail","test_count":len(files),"executed_count":len(results),"failed_count":len(failures),"discovery":"git_tracked_plus_local_filesystem","files":files,"results_tail":results[-25:],"failures":failures,"claim_boundary":"Local test evidence only."}
def write_outputs(root,pkt):
 root=Path(root).resolve(); (root/"reports").mkdir(exist_ok=True); (root/"state"/"loops").mkdir(parents=True,exist_ok=True)
 (root/"reports"/"nexus_bounded_runtime_report_latest.json").write_text(json.dumps(pkt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 (root/"state"/"loops"/"bounded_tests_latest.json").write_text(json.dumps({k:pkt[k] for k in ["version","generated_utc","mode","status","test_count","executed_count","failed_count"]},indent=2,sort_keys=True)+"\n",encoding="utf-8")
def main(argv=None):
 ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--pattern",default="test_*.py"); ap.add_argument("--timeout-seconds",type=int,default=90); ap.add_argument("--no-write",action="store_true"); ap.add_argument("--json",action="store_true"); a=ap.parse_args(argv)
 pkt=run_bounded_tests(a.root,a.pattern,a.timeout_seconds)
 if not a.no_write: write_outputs(a.root,pkt)
 print(json.dumps(pkt if a.json else {"mode":pkt["mode"],"status":pkt["status"],"test_count":pkt["test_count"],"failed_count":pkt["failed_count"]},indent=2,sort_keys=True))
 return 0 if pkt["status"]=="pass" else 1
if __name__=="__main__": raise SystemExit(main())
