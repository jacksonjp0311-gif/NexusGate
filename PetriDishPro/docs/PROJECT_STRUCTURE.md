# Project Structure

## Public source tree

| Path | Role |
| --- | --- |
| `ORGANISM_GATE.ps1` | Main terminal entry point for the Organism Gate menu. |
| `START_ORGANISM_GATE.bat` | Convenience Windows launcher. |
| `petri_lab/` | Python simulation package and validation logic. |
| `electron/` | Electron application shell and renderer surfaces. |
| `electron/renderer/` | HUD scripts, styles, overlays, and UI behavior layers. |
| `config/` | Organism, preset, field, metric, and drug-card configuration surfaces. |
| `docs/` | Project documentation, entrypoint notes, capability docs, update notes, and assets. |
| `tests/` | Python validation tests and static contract checks. |
| `tools/` | Developer utilities such as failure digest generation. |
| `examples/` | Example simulation input/configuration files. |
| `assets/` | Icons and public visual assets. |

## Local/generated paths

The following paths are local or generated and should not be committed:

- `_backup/`
- `.petri_backups/`
- `backups/`
- `reports/bio/`
- `artifacts/bio/runs/`
- `node_modules/`
- `.venv/`
- `__pycache__/`

## Publication guidance

Keep source, docs, tests, configuration files, icons, and public assets in Git. Keep local backups, generated run outputs, test logs, dependency folders, and private environment files out of Git.
