---
name: setup
description: |
  Initialize the design doc backlog system in a project. Use when the user wants to:
  - Set up design docs for a project
  - Initialize the backlog system
  - Configure design doc workflow
  - Add design doc task management
---

# Setup Design Doc Backlog System

This skill helps users set up the design doc driven task management system in their project.

## When to Use

Activate when the user says things like:
- "set up design docs"
- "initialize the backlog"
- "configure design doc workflow"
- "add task management with design docs"

## Setup Process

### 1. Gather Information

Ask the user for:
- **Project prefix**: A short uppercase identifier (e.g., `ACME`, `GF`, `DAB`) used in task IDs like `[ACME-001-01]`

Check if they already have:
- A `README.org` with `#+PROJECT_PREFIX:` set (use that)
- Existing `docs/design/` directory (don't overwrite)
- A tracked `backlog.org` — the project predates design doc 017; finish setup, then suggest `/backlog:migrate-backlog`

### 2. Create Directory Structure

Create these directories if they don't exist:
```
docs/design/
docs/loose-ends/      (with an empty .gitkeep)
bin/
```

### 3. Create Files from Templates

The templates are in the plugin's `templates/` directory. Copy them with PROJECT substitution:

| Template | Destination | Substitution |
|----------|-------------|--------------|
| `readme-project.org` | `README.org` | Replace `PROJECT` with prefix |
| `readme-design.org` | `docs/design/README.org` | None |
| `org-setup.org` | `org-setup.org` | Replace `PROJECT` with prefix |
| `design-doc-template.org` | `docs/design/000-template.org` | Replace `PROJECT` with prefix |
| `changelog-template.md` | `CHANGELOG.md` | None |
| `scripts/backlog.py` (beside `templates/`) | `bin/backlog` | None; `chmod +x` |

**Important**: Check if files exist before writing. Ask the user before overwriting — except `bin/backlog`, which is the plugin's and is replaced on every setup run, so re-running setup is how a project picks up a newer one. Say so when it changes.

`bin/backlog` is committed to the project, so a developer without the plugin, or without Emacs, can still read the backlog from a shell.

Add `backlog.org` to `.gitignore` (create it if needed). There is no backlog file; anyone who wants one in Emacs generates it with `bin/backlog --org > backlog.org`.

### 4. Update CLAUDE.md

Append or merge the following into the project's CLAUDE.md (create if needed):

```markdown
## Design Doc Workflow

This project uses design docs for task management. Design docs live in `docs/design/`.

### Key Files
- `docs/design/*.org` - Design documents: each decision, its tasks, and every task's state
- `bin/backlog` - The backlog, computed from the docs (`--all`, `--questions`, `--org`, `--check`)
- `docs/loose-ends/*.org` - Notes that belong to no doc, one file each
- `README.org` - Project config (prefix, categories, statuses)

There is no backlog file. Task state lives on the task's heading in its doc (`WIP`/`HOLD`, `:QUEUED:`, `:HANDOFF:`, progress under a child heading tagged `:working:`). `backlog.org`, if present, is generated and ignored by git.

### Reading the Docs
Start from the newest checkpoint (a doc with a "What it supersedes" section) and the docs numbered after it. Open a `Superseded` doc only to follow a citation.

### Workflow
1. Create design docs with `/backlog:new-design-doc` — it reserves the number by pushing a two-file stub to main
2. Queue tasks with `/backlog:task-queue <id>`
3. Start work with `/backlog:task-start <id>`
4. Complete with `/backlog:task-complete <id>`; the last task in a doc runs `/backlog:design-complete`
5. Now and then, `/backlog:checkpoint` to write down what we now believe

If two docs end up with one number, `/backlog:renumber-design-doc` repairs it.

### Task ID Format
`[PREFIX-NNN-XX]` where:
- PREFIX = project prefix (e.g., ACME)
- NNN = design doc number
- XX = task sequence
```

### 5. Explain What Was Created

After setup, explain:
- What files were created and their purpose
- How to create a first design doc
- Available commands (`/backlog:new-design-doc`, etc.)

## Example Interaction

```
User: Set up design docs for this project

Claude: I'll help you set up the design doc backlog system.

What project prefix would you like to use? This is a short uppercase identifier
(like ACME, GF, or DAB) that will appear in task IDs like [ACME-001-01].

User: ACME

Claude: Great! Let me set up the backlog system with prefix ACME.

[Creates files...]

Done! I've created:
- README.org - Project config with categories and statuses
- org-setup.org - Shared org-mode configuration
- bin/backlog - The backlog, computed from the design docs
- docs/loose-ends/ - Notes that belong to no design doc
- docs/design/README.org - Index of design documents
- docs/design/000-template.org - Template for new design docs
- CHANGELOG.md - For tracking releases

To create your first design doc, use:
  /backlog:new-design-doc "Your Feature Title"

This reserves the next number on origin/main and creates the doc. Its tasks show up in bin/backlog once queued.
```

## Template Content

When writing files, read the template content from the plugin's templates directory and perform the PROJECT → prefix substitution.
