---
description: Create a new design document (from template or by converting markdown)
argument-hint: <title> [source.md]
---

# New Design Doc

Create a new design document titled: **$ARGUMENTS**

## Argument Parsing

Parse `$ARGUMENTS` to extract:
- **title**: The design doc title (required)
- **source_path**: Optional path to existing markdown file to convert

Examples:
- `/new-design-doc Error Recovery` → title="Error Recovery", no source
- `/new-design-doc Error Recovery docs/legacy/error-handling.md` → title="Error Recovery", source="docs/legacy/error-handling.md"

## Process

The number is the one thing two developers can both take at once, so it is claimed on the remote before anything else happens: a two-file commit — the stub and its index row — pushed straight to the remote's default branch. After that the doc is written wherever the developer is working, branch or not. See design doc 017.

### 1. Determine Category

Read valid categories from `README.org` (the `* Document Categories` table). Ask the user which applies, or infer it from context.

### 2. Reserve the Number

```bash
git fetch origin
bin/backlog --next-number        # the larger of the local docs and origin/main's, plus one
```

(Use the remote's default branch if it isn't `main`: `git symbolic-ref --short refs/remotes/origin/HEAD`, and pass it as `--ref`.)

Tell the user what is about to happen and ask once: *"Reserve NNN for '<title>' by pushing a two-file commit (the stub and its README row) to origin/main?"* If they say no, skip to step 2c.

**2a. Make the reservation commit against `origin/main`, not against the current checkout.** That keeps it to two files whatever branch the developer is on and whatever is uncommitted:

```bash
tmp=$(mktemp -d)
git worktree add --detach "$tmp" origin/main
# write $tmp/docs/design/NNN-slug.org  (the stub, below)
# add the row to $tmp/docs/design/README.org
git -C "$tmp" add docs/design/NNN-slug.org docs/design/README.org
git -C "$tmp" commit -m "docs: reserve NNN, <title>"
git -C "$tmp" push origin HEAD:main
sha=$(git -C "$tmp" rev-parse HEAD)
git worktree remove "$tmp"
```

**If the push is rejected**, someone else pushed in between. In the temporary worktree: `git fetch origin && git reset --hard origin/main`, take `bin/backlog --root "$tmp" --next-number` again, rewrite the stub's filename, `#+TITLE:` and README row for the new number, commit, push. Nothing cites the number yet, so renaming is free. Give up after three tries and say why.

**2b. Bring the reservation into the current checkout:**
- If `HEAD` is an ancestor of `origin/main` (on main, nothing unpushed): `git merge --ff-only origin/main`
- Otherwise: `git cherry-pick $sha`. If it conflicts on `README.org` (the developer had edited it), resolve by keeping both rows.

**2c. If there is no remote, the network is down, or the user declined**, create the stub in the working tree and commit it locally, and say plainly: *"NNN is not reserved. If someone else takes it before this merges, `/backlog:renumber-design-doc` will move this one."*

### 3. The Stub

From `docs/design/000-template.org`, with:

- A fresh org-id in the file-level drawer at the top: `uuidgen | tr A-Z a-z` (or `python3 -c 'import uuid; print(uuid.uuid4())'`). This is the doc's identity if its number or place ever changes; it is never reused.
- `#+TITLE:` - NNN - <title>
- `#+AUTHOR:` - the person creating it (`git config user.name`)
- `#+STATUS:` - Draft
- `#+CATEGORY:` - from step 1
- `#+CREATED:` and `#+LAST_MODIFIED:` - today [YYYY-MM-DD]
- `#+SETUPFILE: ../../org-setup.org`
- The template's headings, empty

And a row in `docs/design/README.org`: `| NNN | [[file:NNN-slug.org][Title]] | Draft |`

The stub is deliberately empty: it is a claim, not a draft. The content goes in next, as an ordinary commit on whatever branch the developer is on.

### 4. Write the Content

**If no source_path**: fill in the sections with the user (see the `new-design-doc` skill for what makes each section good).

**If source_path provided** (convert from markdown):
- Read the markdown file
- Convert to org-mode format (see Conversion Rules below)
- Preserve existing content structure

### 5. Assign Task IDs

For **new documents**: `[PREFIX-NNN-01]`, `[PREFIX-NNN-02]`, … using the project prefix from `README.org`'s `#+PROJECT_PREFIX:` and the reserved number.

For **converted documents**:
- Find all `- [ ]` and `- [x]` checkboxes
- Convert to `** TODO [PREFIX-NNN-XX]` / `** DONE [PREFIX-NNN-XX]`
- Assign sequential IDs starting at 01
- Preserve the task description text

### 6. Offer to Queue Tasks

After conversion, list the tasks with their IDs and ask whether to queue any of them (`/task-queue`, which marks the heading `:QUEUED:`).

### 7. Report

- Path to the new file, and whether the number is reserved on the remote
- If converted: summary of what was transformed
- List of tasks with their IDs
- Remind to review and refine

## Conversion Rules (Markdown → Org-Mode)

### Structure
| Markdown | Org-Mode |
|----------|----------|
| `# Heading` | `* Heading` |
| `## Heading` | `** Heading` (under appropriate parent) |
| `### Heading` | `*** Heading` |

### Tasks
| Markdown | Org-Mode |
|----------|----------|
| `- [ ] Task text` | `** TODO [PROJECT-NNN-XX] Task text` |
| `- [x] Task text` | `** DONE [PROJECT-NNN-XX] Task text` |

### Code
| Markdown | Org-Mode |
|----------|----------|
| ` ```rust` | `#+begin_src rust` |
| ` ``` ` | `#+end_src` |

### Frontmatter
| Markdown YAML | Org-Mode |
|---------------|----------|
| `title: X` | `#+TITLE: X` |
| `status: X` | `#+STATUS: X` |
| `author: X` | `#+AUTHOR: X` |

### Questions/Decisions
| Markdown Pattern | Org-Mode |
|------------------|----------|
| `**Open Question:**` or `- [ ] Question?` in Questions section | `** OPEN Question?` |
| `**Decision:**` or `- [x] Decided thing` in Questions section | `** DECIDED Decided thing` |

### Links
| Markdown | Org-Mode |
|----------|----------|
| `[text](url)` | `[[url][text]]` |
| `[text](./file.md)` | `[[file:file.org][text]]` (update .md → .org) |

## Org-Mode Reminders

The document MUST use org-mode conventions:
- `** TODO [PROJECT-NNN-XX] Task title` for tasks (not markdown checkboxes)
- `** OPEN` / `** DECIDED` for questions
- `:PROPERTIES:` drawers for metadata (EFFORT, VERSION, etc.)
- `#+SETUPFILE: ../../org-setup.org` for shared config

## Examples

New from template:
```
/new-design-doc Error Recovery Improvements
```
Reserves 019 on origin/main, then creates `docs/design/019-error-recovery-improvements.org`

Convert existing markdown:
```
/new-design-doc Cache Architecture docs/legacy/caching-proposal.md
```
Converts markdown to `docs/design/020-cache-architecture.org`, assigns task IDs

## Files

- Template: `docs/design/000-template.org`
- Index: `docs/design/README.org`
- Setup: `org-setup.org`
- Next number: `bin/backlog --next-number`
