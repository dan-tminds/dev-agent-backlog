---
description: Repair a design doc numbering collision - move one doc to a free number and rewrite what refers to it
argument-hint: [doc-file] [new-number]
---

# Renumber Design Doc

Two design docs have the same number — two developers each created `021` on their own branch, and reserving by push (`/new-design-doc`) didn't happen or didn't catch it. Move one of them: **$ARGUMENTS**

The filename, the links and the task IDs in code can all be rewritten. Commit messages cannot, so the doc that moves keeps an alias that says which commits still use its old ID. See design doc 017.

## 1. Find the Collision

```bash
git fetch origin
bin/backlog --check
```

`--check` reports `021 is used by two docs: …`. If `$ARGUMENTS` names a doc, use that one; otherwise use the pair `--check` found. If there is no collision locally, compare with the remote: `git ls-tree --name-only origin/main docs/design/ | grep '/021-'` — the collision may be between this branch and `main`.

## 2. Decide Which Doc Yields

- **The doc already on `origin/main` keeps the number.** The other one yields.
- **If both are on `origin/main`** (the collision was merged), the one merged second yields: `git log --diff-filter=A --format='%h %ad %s' origin/main -- <path>` for each.
- **If neither is** (two unmerged branches), ask the user. Whoever renumbers, do it on the branch that merges second.

Tell the user which doc keeps the number and which moves, and why, before changing anything.

## 3. Find the Yielding Range

The rewrite is only safe on lines the yielding side added, so pin down where those are:

- **Not merged yet** (the usual case — run this before merging): `base=$(git merge-base HEAD origin/main)`, no tip. Committed and uncommitted changes since `base` on this branch, and untracked files, all count as added.
- **Already merged with a merge commit `M`**: `base=$(git merge-base M^1 M^2)`, `tip=M^2`.
- **Already merged with no merge commit** (rebased or fast-forwarded): there is no clean range. Show `git log --format='%h %an %s' -- <yielding doc>` and ask the user which commits were the yielding doc's work; use the parent of the first as `base` and the last as `tip`. If that can't be decided, skip step 5c and list every reference for the user instead.

## 4. Pick the New Number

`bin/backlog --next-number` (counts `origin/main`), unless `$ARGUMENTS` gave one. Check it is free on the remote too.

Renumber as the last step before merging, and push the merge promptly: the new number is not reserved, and the shorter the window the less likely it collides again. If it does, run this again — everything here is mechanical.

## 5. Rewrite

**a. The file.** `git mv docs/design/021-mine.org docs/design/023-mine.org`. Anything else named for the number that belongs to the yielding doc moves too — e.g. `docs/design/mockups/021-mine/` — if the yielding side added it.

**b. The doc itself.**
- `#+TITLE: 021 - …` → `#+TITLE: 023 - …`
- Every `[PREFIX-021-` in its task headings and body → `[PREFIX-023-` (in this file all of them mean this doc)
- Add, under the other `#+` keywords: `#+ALIASES: PREFIX-021 <base>..<tip>`, short SHAs. For an unmerged branch the tip is `git rev-parse --short HEAD` *before* the renumber commit: exactly the commits in that range used the old ID. (If the branch will be rebased before it merges, rebase first and renumber after, or the SHAs in the alias won't survive.)
- If the doc has a Changelog section, add a line: `[YYYY-MM-DD] Renumbered from 021, which 021-<other> kept.`

**c. Task-ID references elsewhere.** This is the step that has to be exact, so the script does it:

```bash
bin/backlog --renumber-refs PREFIX-021 PREFIX-023 --since $base [--until $tip]          # dry run
bin/backlog --renumber-refs PREFIX-021 PREFIX-023 --since $base [--until $tip] --write
```

It rewrites `PREFIX-021-NN` only on lines added in the yielding range, and lists every other occurrence. Show the user the *Left* list: those mean the doc that kept the number, or are ambiguous, and stay as they are unless the user says otherwise.

**d. Links.** `grep -rn '021-mine' --exclude-dir=.git .` — the slug makes these unambiguous. Rewrite every `021-mine.org` (and moved directory paths) to the new name.

**e. Bare numbers in prose.** `git diff $base -U0 | grep -nE '^\+.*\b021\b'` finds lines the yielding side added that say "021" without a task ID ("see 021", "as 021 decided"). Show them to the user; don't rewrite them blind.

**f. The index.** Move the doc's row in `docs/design/README.org` to its new number and position.

## 6. Verify and Commit

```bash
bin/backlog --check                      # no duplicate numbers, no mismatched task IDs
grep -rn 'PREFIX-021-' --exclude-dir=.git . | grep -v '<doc that kept 021>'   # what's left, and why
```

Commit the rename on its own so it can be reviewed by itself:

```
docs: renumber 021-mine to 023 (021-theirs kept 021)

Rewrote N task-ID references added on this branch and M links.
Left K references that may mean 021-theirs; listed in the doc's
alias range for /reconcile-design-docs.
```

## 7. Report

- Which doc kept the number and which moved, and to what
- Counts: references rewritten, links rewritten, references left (with the list)
- The alias recorded, and that commit messages in that range still say the old ID — `/reconcile-design-docs` reads the alias when it searches the log
- That the new number is not reserved until this merges and is pushed

## Files

- Design docs: `docs/design/*.org`
- Index: `docs/design/README.org`
- Script: `bin/backlog --check`, `--next-number`, `--renumber-refs`
