from pathlib import Path
from xml.sax.saxutils import escape
SECURE_DEFAULTS={"vGPU":"Disable","Networking":"Disable","AudioInput":"Disable","VideoInput":"Disable","ProtectedClient":"Enable","PrinterRedirection":"Disable","ClipboardRedirection":"Disable"}
def generate_wsb(root: Path, payload: Path)->Path:
    runtime=root/"NexusCell"/"runtime"/"wsb"; input_dir=runtime/"input"; output_dir=runtime/"output"
    input_dir.mkdir(parents=True,exist_ok=True); output_dir.mkdir(parents=True,exist_ok=True)
    wsb_path=runtime/"nexus_cell_payload.wsb"
    lines=["<Configuration>"]
    for tag,value in SECURE_DEFAULTS.items(): lines.append(f"  <{tag}>{value}</{tag}>")
    lines += ["  <MappedFolders>","    <MappedFolder>",f"      <HostFolder>{escape(str(input_dir))}</HostFolder>","      <SandboxFolder>C:\\NexusCell\\input</SandboxFolder>","      <ReadOnly>true</ReadOnly>","    </MappedFolder>","    <MappedFolder>",f"      <HostFolder>{escape(str(output_dir))}</HostFolder>","      <SandboxFolder>C:\\NexusCell\\output</SandboxFolder>","      <ReadOnly>false</ReadOnly>","    </MappedFolder>","  </MappedFolders>","  <LogonCommand>","    <Command>powershell.exe -ExecutionPolicy Bypass -File C:\\NexusCell\\input\\payload.ps1</Command>","  </LogonCommand>","</Configuration>"]
    wsb_path.write_text("\n".join(lines)+"\n",encoding="utf-8"); return wsb_path
