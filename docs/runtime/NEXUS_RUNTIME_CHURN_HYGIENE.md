# NEXUS Runtime Churn Hygiene

Runtime Churn Hygiene separates generated evidence exhaust from source mutations after heavy NEXUS runs.

```text
git status -> classify generated tracked surfaces -> classify generated untracked exhaust -> preserve source dirty -> optional clean
```

Use:

```powershell
.\scripts\nexus.ps1 runtime-hygiene
.\scripts\nexus.ps1 clean-runtime
.\scripts\nexus.ps1 install-hooks
```

`runtime-hygiene` is dry-run classification. `clean-runtime` applies only allowlisted cleanup:

- restore known tracked generated runtime surfaces
- remove known untracked timestamped pack exhaust
- leave source files, docs, tests, policy files, and unclassified changes visible

Blocked:

- no `git reset --hard`
- no unbounded `git clean`
- no source deletion
- no cleaning unclassified paths
- no self-authorized commit

Runtime hygiene is a local operator convenience and evidence surface. It does not prove correctness, safety, security, production readiness, or authority.

`install-hooks` installs a local post-commit hook that runs bounded runtime cleanup after future commits. The hook is local machine state; the installer is tracked so the behavior can be recreated.
