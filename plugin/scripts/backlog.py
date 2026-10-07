#!/usr/bin/env python3
"""The backlog, computed from the design docs.

There is no backlog file to keep in sync. What is in progress, held, or
queued is read off the task headings in docs/design/*.org, and notes that
belong to no doc are the files in docs/loose-ends/. See design doc 017.

    bin/backlog                  in progress, held, queued, and loose ends
    bin/backlog --all            and every unqueued TODO in a doc still live
    bin/backlog --questions      every OPEN question
    bin/backlog --org            the same view as org, with links to each heading
    bin/backlog --next-number    the next design doc number, local and origin/main
    bin/backlog --check          duplicate numbers and task IDs, stale working state

Standard library only, so it runs anywhere python3 does.
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

DESIGN_DIR = "docs/design"
LOOSE_ENDS_DIR = "docs/loose-ends"

# Properties that exist only while work is under way. /backlog:design-complete
# clears them, and --check reports them on a doc that is finished.
WORKING_PROPS = ("QUEUED", "HANDOFF", "REASON", "CLAUDE_TASK", "CLAUDE_TASK_LIST", "TRANSCRIPT")
FINISHED = ("Complete", "Superseded", "Archived")

DOC_NAME = re.compile(r"^(\d{3})-.+\.org$")
HEADING = re.compile(
    r"^(\*+)\s+(?:(TODO|WIP|HOLD|DONE|OPEN|DECIDED)\s+)?(.*?)(?:\s+(:[\w@#%:]+:))?\s*$"
)
TASK_ID = re.compile(r"^\[([A-Z][A-Z0-9]*-(\d{3})-\d{2}[a-z]?)\]\s*(.*)$")
KEYWORD = re.compile(r"^#\+(\w+):\s*(.*?)\s*$")
PROPERTY = re.compile(r"^\s*:([\w-]+):\s*(.*?)\s*$")
PLANNING = re.compile(r"^\s*(CLOSED|SCHEDULED|DEADLINE):")

COUNTS = {2: "two", 3: "three"}


@dataclass
class Task:
    id: str
    state: str
    title: str
    tags: list
    line: int
    level: int
    props: dict = field(default_factory=dict)
    has_working_notes: bool = False

    @property
    def queued(self):
        return "QUEUED" in self.props


@dataclass
class Question:
    state: str
    title: str
    line: int


@dataclass
class Doc:
    path: str
    number: str
    title: str = ""
    status: str = ""
    id: str = ""
    aliases: list = field(default_factory=list)
    tasks: list = field(default_factory=list)
    questions: list = field(default_factory=list)
    stray_working_lines: list = field(default_factory=list)

    def working_state(self):
        found = []
        for task in self.tasks:
            found += [f"{task.id} :{name}:" for name in task.props if name in WORKING_PROPS]
            if task.has_working_notes:
                found.append(f"{task.id} working notes")
        found += [f"working notes at line {line}" for line in self.stray_working_lines]
        return found


@dataclass
class LooseEnd:
    title: str
    path: str


def parse_doc(path, root=None):
    path = Path(path)
    shown = str(path.relative_to(root)) if root else str(path)
    match = DOC_NAME.match(path.name)
    doc = Doc(path=shown, number=match.group(1) if match else "")

    in_block = False
    seen_heading = False
    drawer_owner = None  # the Task or Doc whose :PROPERTIES: may come next
    in_drawer = False
    task = None

    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if in_block:
            if line.strip().lower().startswith("#+end_"):
                in_block = False
            continue
        if line.strip().lower().startswith("#+begin_"):
            in_block = True
            continue

        if in_drawer:
            if line.strip() == ":END:":
                in_drawer = False
                drawer_owner = None
            else:
                prop = PROPERTY.match(line)
                if prop and isinstance(drawer_owner, Task):
                    drawer_owner.props[prop.group(1)] = prop.group(2)
                elif prop and prop.group(1) == "ID":
                    doc.id = prop.group(2)
            continue

        if line.strip() == ":PROPERTIES:":
            owner = drawer_owner if seen_heading else doc
            if owner is not None:
                drawer_owner = owner
                in_drawer = True
            continue

        heading = HEADING.match(line)
        if heading:
            seen_heading = True
            level = len(heading.group(1))
            state, rest = heading.group(2), heading.group(3)
            tags = [t for t in (heading.group(4) or "").split(":") if t]
            if task and level <= task.level:
                task = None
            drawer_owner = None

            if "working" in tags:
                if task:
                    task.has_working_notes = True
                else:
                    doc.stray_working_lines.append(number)

            task_id = TASK_ID.match(rest)
            if state in ("TODO", "WIP", "HOLD", "DONE") and task_id:
                task = Task(
                    id=task_id.group(1),
                    state=state,
                    title=task_id.group(3),
                    tags=tags,
                    line=number,
                    level=level,
                )
                doc.tasks.append(task)
                drawer_owner = task
            elif state in ("OPEN", "DECIDED"):
                doc.questions.append(Question(state=state, title=rest, line=number))
            continue

        if PLANNING.match(line):
            continue
        if line.strip():
            drawer_owner = None

        keyword = KEYWORD.match(line)
        if keyword and not seen_heading:
            name, value = keyword.group(1).upper(), keyword.group(2)
            if name == "TITLE":
                doc.title = value
            elif name == "STATUS":
                doc.status = value
            elif name == "ALIASES":
                doc.aliases.append(value)

    if not doc.title:
        doc.title = path.stem
    return doc


def load_docs(root):
    root = Path(root)
    paths = sorted((root / DESIGN_DIR).glob("*.org"))
    return [
        parse_doc(p, root)
        for p in paths
        if DOC_NAME.match(p.name) and DOC_NAME.match(p.name).group(1) != "000"
    ]


def load_loose_ends(root):
    root = Path(root)
    found = []
    for path in sorted((root / LOOSE_ENDS_DIR).glob("*.org")):
        title = path.stem
        for line in path.read_text().splitlines():
            keyword = KEYWORD.match(line)
            if keyword and keyword.group(1).upper() == "TITLE":
                title = keyword.group(2)
                break
        found.append(LooseEnd(title=title, path=str(path.relative_to(root))))
    return found


def sections(docs, include_all=False):
    """[(heading, [(doc, [task, ...]), ...]), ...], omitting empty ones."""
    wanted = [
        ("In progress", lambda d, t: t.state == "WIP"),
        ("On hold", lambda d, t: t.state == "HOLD"),
        ("Queued", lambda d, t: t.state == "TODO" and t.queued),
    ]
    if include_all:
        wanted.append(
            (
                "Not queued",
                lambda d, t: t.state == "TODO" and not t.queued and d.status not in FINISHED,
            )
        )
    found = []
    for heading, wants in wanted:
        groups = [(d, [t for t in d.tasks if wants(d, t)]) for d in docs]
        groups = [(d, tasks) for d, tasks in groups if tasks]
        if groups:
            found.append((heading, groups))
    return found


def render_text(docs, loose_ends, include_all=False):
    blocks = []
    for heading, groups in sections(docs, include_all):
        lines = [heading]
        for doc, tasks in groups:
            lines.append(f"  {doc.title}")
            for t in tasks:
                who = t.props.get("WORKED_BY", "")
                lines.append(f"    {t.state:<4} [{t.id}] {t.title}" + (f"  ({who})" if who else ""))
                if t.props.get("HANDOFF"):
                    lines.append(f"         handoff: {t.props['HANDOFF']}")
                if t.props.get("REASON"):
                    lines.append(f"         reason: {t.props['REASON']}")
                lines.append(f"         {doc.path}:{t.line}")
        blocks.append("\n".join(lines) + "\n")
    if loose_ends:
        lines = ["Loose ends"]
        for le in loose_ends:
            lines += [f"  {le.title}", f"         {le.path}"]
        blocks.append("\n".join(lines) + "\n")
    if not blocks:
        return "Nothing in progress, held, or queued.\n"
    return "\n".join(blocks)


def render_org(docs, loose_ends, include_all=False):
    lines = [
        "#+TITLE: Backlog",
        "#+TODO: TODO WIP HOLD | DONE",
        "# Generated by bin/backlog --org. Edit the design docs, not this file.",
        "",
    ]
    for heading, groups in sections(docs, include_all):
        lines.append(f"* {heading}")
        for doc, tasks in groups:
            for t in tasks:
                lines.append(f"** {t.state} [[file:{doc.path}::{t.line}][{t.id}]] {t.title}")
                lines.append(f"- doc :: [[file:{doc.path}][{doc.title}]]")
                for label, name in (("worked by", "WORKED_BY"), ("handoff", "HANDOFF"), ("reason", "REASON")):
                    if t.props.get(name):
                        lines.append(f"- {label} :: {t.props[name]}")
        lines.append("")
    if loose_ends:
        lines.append("* Loose ends")
        lines += [f"** [[file:{le.path}][{le.title}]]" for le in loose_ends]
        lines.append("")
    return "\n".join(lines)


def render_questions(docs):
    lines = []
    for doc in docs:
        open_ones = [q for q in doc.questions if q.state == "OPEN"]
        if open_ones:
            lines.append(doc.title)
            for q in open_ones:
                lines += [f"  OPEN {q.title}", f"       {doc.path}:{q.line}"]
    return "\n".join(lines) + "\n" if lines else "No open questions.\n"


def next_number(local_names, remote_names):
    numbers = [0]
    for name in list(local_names) + list(remote_names):
        match = DOC_NAME.match(Path(name).name)
        if match:
            numbers.append(int(match.group(1)))
    return f"{max(numbers) + 1:03d}"


def remote_doc_names(root, ref):
    """Design doc filenames on ref, or None if git cannot say."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "--name-only", ref, DESIGN_DIR + "/"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.split()


def check(docs):
    problems = []

    by_number = {}
    for doc in docs:
        by_number.setdefault(doc.number, []).append(doc.path)
    for number, paths in by_number.items():
        if len(paths) > 1:
            count = COUNTS.get(len(paths), str(len(paths)))
            problems.append(f"{number} is used by {count} docs: {', '.join(paths)}")

    by_task = {}
    for doc in docs:
        for t in doc.tasks:
            by_task.setdefault(t.id, []).append(f"{doc.path}:{t.line}")
    for task_id, places in by_task.items():
        if len(places) > 1:
            times = "twice" if len(places) == 2 else f"{len(places)} times"
            problems.append(f"{task_id} appears {times}: {', '.join(places)}")

    for doc in docs:
        aliased = [a.split()[0] + "-" for a in doc.aliases if a.split()]
        for t in doc.tasks:
            prefix = t.id.rsplit("-", 1)[0] + "-"
            if TASK_ID.match(f"[{t.id}]").group(2) != doc.number and prefix not in aliased:
                problems.append(
                    f"{t.id} is in {doc.path}:{t.line}, whose number is {doc.number}"
                )

    for doc in docs:
        if doc.status in FINISHED and doc.working_state():
            problems.append(
                f"{doc.path} is {doc.status} but still has working state: "
                + ", ".join(doc.working_state())
            )

    return problems


def find_root(start):
    for candidate in [start, *start.parents]:
        if (candidate / DESIGN_DIR).is_dir():
            return candidate
    return start


def main(argv, stdout=sys.stdout, stderr=sys.stderr):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", help="project root (default: nearest dir with docs/design)")
    parser.add_argument("--all", action="store_true", help="include unqueued TODOs")
    parser.add_argument("--org", action="store_true", help="print as org")
    parser.add_argument("--questions", action="store_true", help="list OPEN questions")
    parser.add_argument("--next-number", action="store_true", help="next design doc number")
    parser.add_argument("--ref", default="origin/main", help="ref --next-number also counts")
    parser.add_argument("--check", action="store_true", help="report collisions and stale state")
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else find_root(Path.cwd())

    if args.next_number:
        local = [p.name for p in (root / DESIGN_DIR).glob("*.org")]
        remote = remote_doc_names(root, args.ref)
        if remote is None:
            print(f"({args.ref} not readable; counted local docs only)", file=stderr)
        stdout.write(next_number(local, remote or []) + "\n")
        return 0

    docs = load_docs(root)

    if args.check:
        problems = check(docs)
        stdout.write("".join(p + "\n" for p in problems) or "No problems.\n")
        return 1 if problems else 0

    if args.questions:
        stdout.write(render_questions(docs))
        return 0

    loose_ends = load_loose_ends(root)
    render = render_org if args.org else render_text
    stdout.write(render(docs, loose_ends, include_all=args.all))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
