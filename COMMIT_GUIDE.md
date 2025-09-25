# Commit Types Cheat Sheet

| Type  | Purpose                                   | Example summary                          |
|-------|-------------------------------------------|-------------------------------------------|
| feat  | Introduce a new feature                   | feat: add MIDI CC panel mapping           |
| fix   | Patch a bug                               | fix: correct eigenmode scaling            |
| docs  | Documentation-only changes               | docs: update README run instructions      |
| chore | Maintenance / tooling / misc updates      | chore: add .gitignore and LICENSE         |
| test  | Add or improve tests                      | test: add pytest coverage for midi_listener |

## Usage
- Use present tense ("add" not "added").
- Keep the summary under 50 characters when possible.
- Optionally include details in the body explaining context or decisions.
- Reference issues/tickets in the footer if needed.

Example commit message:

```
feat: add MIDI CC panel mapping

- load mapping file dynamically
- normalize CC values in mapper

Refs: UI-1023
```
