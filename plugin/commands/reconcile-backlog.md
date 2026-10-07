---
description: Reconcile working state across the design docs - stale WIP, leftover properties, loose ends, collisions
argument-hint: [--dry-run]
---

# Reconcile Backlog

The backlog is the working state on the task headings in `docs/design/*.org` plus `docs/loose-ends/`. Find where that state no longer matches reality, and fix it.

(Whether a task is *done* — evidence from git, the changelog, the code — is `/reconcile-design-docs`. This command is about the in-progress state around tasks.)

## Arguments

- **--dry-run** (optional): Show what would change without making modifications

## Process

### 1. Collisions and Leftovers

```bash
git fetch origin
bin/backlog --check
```

- **Two docs with one number**: suggest `/backlog:renumber-design-doc`. Don't go on reconciling task IDs in those docs until it's repaired.
- **One task ID in two places** or **a task ID that doesn't match its doc**: show both places; usually a copy-paste or a renumber that missed a heading.
- **Working state in a `Complete` or `Superseded` doc**: suggest `/backlog:design-complete` on it.

### 2. Task Headings

Read every `TODO`, `WIP` and `HOLD` heading (`bin/backlog --all` lists them with `file:line`). For each:

| Finding | Check | Action |
|---------|-------|--------|
| **Stale WIP** | `git log -1 --format='%ar %an' -- <doc>` is more than a week old | Ask: still in progress, back to `TODO`, or `HOLD` with a reason? |
| **WIP by someone else** | `:WORKED_BY:` names another developer | Report only; it's theirs |
| **HOLD without a reason** | no `:REASON:` | Ask for one |
| **Reason on a task not held** | `:REASON:` on `TODO`/`WIP` | Remove it |
| **Handoff on a DONE task** | `:HANDOFF:` or `:QUEUED:` on `DONE` | Remove (it was in-progress state) |
| **Queued in a finished doc** | `:QUEUED:` `TODO` in a `Complete`/`Superseded` doc | Ask: reopen the doc, move the task, or drop it |

### 3. Loose Ends

For each file in `docs/loose-ends/`:
- If it names a doc that is now `Complete`, ask whether it was resolved by that doc
- If it is more than a month old, show its date and ask whether it's still true
- Use `/backlog:loose-end --resolve` or `--move` for what the user decides

### 4. A Leftover `backlog.org`

If `backlog.org` is still tracked by git (`git ls-files backlog.org`), the project predates design doc 017: suggest `/backlog:migrate-backlog`.

### 5. Apply and Report

Apply what was confirmed (unless `--dry-run`), commit the docs together (`chore: reconcile backlog`), and report:

```
## Backlog Reconciliation

### Collisions: none
### Stale WIP: 1
- [HL-021-03] WIP, last touched 12 days ago by Matt → left as is (his)
### Cleaned: 3
- [HL-019-02] :HANDOFF: on a DONE task, removed
### Loose ends: 4, 1 resolved
- css-restructure → resolved by 022

Now: `bin/backlog`
```

## Strictness Rules

- **Never change another developer's WIP** without asking
- **Never delete a loose end without the user saying it's resolved**
- **Every change has a reason** in the report

## Files

- Design docs: `docs/design/*.org`
- Loose ends: `docs/loose-ends/*.org`
- View and check: `bin/backlog`, `bin/backlog --check`

## Related Commands

- `/reconcile-design-docs` - Is the task actually done? (git, changelog, code)
- `/backlog:design-complete` - Clear working state from a finished doc
- `/backlog:renumber-design-doc` - Repair a numbering collision
