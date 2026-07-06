from __future__ import annotations
import re
from typing import Dict, Mapping

CAPABILITY_KEYS = ["fs_read","fs_write","network","secrets","registry","process_spawn","service_install","git_write","host_mount","clipboard","gpu"]
DEFAULT_WEIGHTS: Dict[str, float] = {"fs_read":0.05,"fs_write":0.25,"network":0.30,"secrets":0.90,"registry":0.70,"process_spawn":0.25,"service_install":0.95,"git_write":0.80,"host_mount":0.60,"clipboard":0.20,"gpu":0.10}
DEFAULT_THRESHOLDS = {"auto":0.30,"review":0.65}

def empty_capability_vector() -> Dict[str,int]:
    return {k:0 for k in CAPABILITY_KEYS}

def capability_vector_from_action(action: str="", runner: str="", payload: str="") -> Dict[str,int]:
    text=f"{action} {runner} {payload}".lower()
    c=empty_capability_vector()
    if payload: c["fs_read"]=1
    if re.search(r"\b(write|modify|patch|save|delete|remove|mkdir|copy|move|set-content)\b", text): c["fs_write"]=1
    if re.search(r"\b(http|https|curl|wget|invoke-webrequest|network|egress|download|upload)\b", text): c["network"]=1
    if re.search(r"\b(secret|token|api[_-]?key|password|credential|private key)\b", text): c["secrets"]=1
    if re.search(r"\b(registry|reg add|hklm|hkcu)\b", text): c["registry"]=1
    if re.search(r"\b(start-process|subprocess|spawn|exec|powershell|cmd.exe|bash)\b", text): c["process_spawn"]=1
    if re.search(r"\b(service install|sc.exe|install-service|systemctl|daemon)\b", text): c["service_install"]=1
    if re.search(r"\b(git push|git commit|git add|git write|push)\b", text): c["git_write"]=1
    elif re.search(r"\b(git status|git log|git diff)\b", text): c["fs_read"]=1
    if re.search(r"\b(host mount|mount|mappedfolder|bind mount|volume)\b", text): c["host_mount"]=1
    if re.search(r"\b(clipboard|clip.exe|pbcopy)\b", text): c["clipboard"]=1
    if re.search(r"\b(gpu|cuda|rocm)\b", text): c["gpu"]=1
    if runner=="mock":
        for k in ["process_spawn","network","secrets","registry","service_install","git_write","host_mount"]:
            c[k]=0
    return c

def risk_terms(capability_vector: Mapping[str,int]) -> Dict[str,float]:
    c={k:int(bool(capability_vector.get(k,0))) for k in CAPABILITY_KEYS}
    return {
        "weighted_capability": round(sum(DEFAULT_WEIGHTS[k]*c[k] for k in CAPABILITY_KEYS), 6),
        "blast_radius": 0.15 if c["host_mount"] or c["service_install"] else 0.0,
        "git_mutation_penalty": 0.25 if c["git_write"] else 0.0,
        "network_openness_penalty": 0.20 if c["network"] else 0.0,
        "secret_exposure_penalty": 0.35 if c["secrets"] else 0.0,
    }

def score_risk(capability_vector: Mapping[str,int]) -> float:
    return round(sum(risk_terms(capability_vector).values()),6)

def risk_band(score: float, thresholds: Mapping[str,float]|None=None) -> str:
    t=thresholds or DEFAULT_THRESHOLDS
    if score <= float(t.get("auto",0.30)): return "engage"
    if score <= float(t.get("review",0.65)): return "review"
    return "deny"
