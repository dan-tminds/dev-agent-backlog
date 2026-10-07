"""Tests for backlog.py. Run with: python3 -m unittest discover plugin/scripts/tests"""

import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import backlog  # noqa: E402


def write(root, relpath, text):
    path = Path(root) / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip())
    return path


SEARCH_DOC = """
    #+TITLE: 021 - Find a Provider
    #+STATUS: Active
    :PROPERTIES:
    :ID: 6f1c0d2e-0000-4000-8000-000000000021
    :END:

    * Design

    #+begin_src org
    ** WIP [HL-021-99] An example inside a block, which is not a task
    #+end_src

    * Tasks

    ** DONE [HL-021-01] The model                                  :p1:
    CLOSED: [2026-10-01]
    :PROPERTIES:
    :EFFORT: S
    :END:

    ** WIP [HL-021-02] The search form                             :p1:
    :PROPERTIES:
    :QUEUED: [2026-10-06]
    :WORKED_BY: claude-code, dan
    :HANDOFF: The date picker is the open question.
    :END:

    The form itself.

    *** Working notes                                              :working:
    [2026-10-07] Two inputs wrap at 900px.

    ** HOLD [HL-021-03] The map                                    :p2:
    :PROPERTIES:
    :REASON: Waiting on a geocoder decision
    :END:

    ** TODO [HL-021-04] Results, sorted                            :p1:
    :PROPERTIES:
    :QUEUED: [2026-10-06]
    :END:

    ** TODO [HL-021-05] Results, filtered                          :p2:

    * Questions

    ** OPEN Does the card want a date?

    ** DECIDED One search per household?
    """

DONE_DOC = """
    #+TITLE: 019 - What to Say
    #+STATUS: Complete

    * Tasks

    ** DONE [HL-019-01] Draft, append-only                         :p1:
    CLOSED: [2026-09-22]

    ** DONE [HL-006-06a] A suffixed ID from another doc            :p1:
    CLOSED: [2026-09-22]
    """


class ParseDocTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.path = write(self.root, "docs/design/021-find-a-provider.org", SEARCH_DOC)
        self.doc = backlog.parse_doc(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_header(self):
        self.assertEqual(self.doc.number, "021")
        self.assertEqual(self.doc.title, "021 - Find a Provider")
        self.assertEqual(self.doc.status, "Active")
        self.assertEqual(self.doc.id, "6f1c0d2e-0000-4000-8000-000000000021")

    def test_tasks_skip_example_blocks(self):
        self.assertEqual(
            [t.id for t in self.doc.tasks],
            ["HL-021-01", "HL-021-02", "HL-021-03", "HL-021-04", "HL-021-05"],
        )

    def test_task_fields(self):
        wip = self.doc.tasks[1]
        self.assertEqual(wip.state, "WIP")
        self.assertEqual(wip.title, "The search form")
        self.assertEqual(wip.tags, ["p1"])
        self.assertEqual(wip.props["HANDOFF"], "The date picker is the open question.")
        self.assertTrue(wip.queued)
        self.assertTrue(wip.has_working_notes)
        self.assertEqual(wip.line, 21)

    def test_properties_after_closed_line(self):
        self.assertEqual(self.doc.tasks[0].props["EFFORT"], "S")

    def test_questions(self):
        self.assertEqual(
            [(q.state, q.title) for q in self.doc.questions],
            [("OPEN", "Does the card want a date?"), ("DECIDED", "One search per household?")],
        )

    def test_working_state(self):
        self.assertEqual(
            self.doc.working_state(),
            [
                "HL-021-02 :QUEUED:",
                "HL-021-02 :HANDOFF:",
                "HL-021-02 working notes",
                "HL-021-03 :REASON:",
                "HL-021-04 :QUEUED:",
            ],
        )

    def test_suffixed_task_ids(self):
        path = write(self.root, "docs/design/019-what-to-say.org", DONE_DOC)
        doc = backlog.parse_doc(path)
        self.assertEqual([t.id for t in doc.tasks], ["HL-019-01", "HL-006-06a"])

    def test_aliases(self):
        path = write(
            self.root,
            "docs/design/022-renamed.org",
            """
            #+TITLE: 022 - Renamed
            #+ALIASES: HL-021 abc123..def456
            """,
        )
        self.assertEqual(backlog.parse_doc(path).aliases, ["HL-021 abc123..def456"])


class LoadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, "docs/design/000-template.org", "#+TITLE: NNN - Title\n")
        write(self.root, "docs/design/README.org", "#+TITLE: Design Documents\n")
        write(self.root, "docs/design/021-find-a-provider.org", SEARCH_DOC)
        write(self.root, "docs/design/019-what-to-say.org", DONE_DOC)
        write(
            self.root,
            "docs/loose-ends/lint-is-red.org",
            "#+TITLE: Lint is red\n\nruff finds five errors.\n",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_numbered_docs_only_in_order(self):
        docs = backlog.load_docs(self.root)
        self.assertEqual([d.number for d in docs], ["019", "021"])

    def test_loose_ends(self):
        self.assertEqual(
            [(le.title, le.path) for le in backlog.load_loose_ends(self.root)],
            [("Lint is red", "docs/loose-ends/lint-is-red.org")],
        )


class ViewTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, "docs/design/021-find-a-provider.org", SEARCH_DOC)
        write(self.root, "docs/design/019-what-to-say.org", DONE_DOC)
        write(self.root, "docs/loose-ends/lint-is-red.org", "#+TITLE: Lint is red\n")
        self.docs = backlog.load_docs(self.root)
        self.loose = backlog.load_loose_ends(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_text_view(self):
        out = backlog.render_text(self.docs, self.loose)
        self.assertEqual(
            out,
            textwrap.dedent(
                """\
                In progress
                  021 - Find a Provider
                    WIP  [HL-021-02] The search form  (claude-code, dan)
                         handoff: The date picker is the open question.
                         docs/design/021-find-a-provider.org:21

                On hold
                  021 - Find a Provider
                    HOLD [HL-021-03] The map
                         reason: Waiting on a geocoder decision
                         docs/design/021-find-a-provider.org:33

                Queued
                  021 - Find a Provider
                    TODO [HL-021-04] Results, sorted
                         docs/design/021-find-a-provider.org:38

                Loose ends
                  Lint is red
                         docs/loose-ends/lint-is-red.org
                """
            ),
        )

    def test_all_adds_unqueued_todos_from_live_docs(self):
        out = backlog.render_text(self.docs, self.loose, include_all=True)
        self.assertIn("Not queued\n  021 - Find a Provider\n    TODO [HL-021-05] Results, filtered", out)

    def test_empty(self):
        self.assertEqual(backlog.render_text([], []), "Nothing in progress, held, or queued.\n")

    def test_org_view_links_to_lines(self):
        out = backlog.render_org(self.docs, self.loose)
        self.assertIn("* In progress\n", out)
        self.assertIn(
            "** WIP [[file:docs/design/021-find-a-provider.org::21][HL-021-02]] The search form",
            out,
        )
        self.assertIn("- handoff :: The date picker is the open question.", out)
        self.assertIn("** [[file:docs/loose-ends/lint-is-red.org][Lint is red]]", out)
        self.assertTrue(out.startswith("#+TITLE: Backlog\n"))

    def test_questions(self):
        out = backlog.render_questions(self.docs)
        self.assertEqual(
            out,
            "021 - Find a Provider\n"
            "  OPEN Does the card want a date?\n"
            "       docs/design/021-find-a-provider.org:47\n",
        )


class NextNumberTest(unittest.TestCase):
    def test_local_only(self):
        self.assertEqual(backlog.next_number(["001-a.org", "017-b.org", "README.org"], []), "018")

    def test_remote_ahead(self):
        self.assertEqual(
            backlog.next_number(["017-b.org"], ["docs/design/017-b.org", "docs/design/018-c.org"]),
            "019",
        )

    def test_empty(self):
        self.assertEqual(backlog.next_number(["000-template.org"], []), "001")


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def problems(self):
        return backlog.check(backlog.load_docs(self.root))

    def test_clean(self):
        write(self.root, "docs/design/021-find-a-provider.org", SEARCH_DOC)
        self.assertEqual(self.problems(), [])

    def test_duplicate_number(self):
        write(self.root, "docs/design/021-find-a-provider.org", SEARCH_DOC)
        write(self.root, "docs/design/021-something-else.org", "#+TITLE: 021 - Else\n")
        self.assertEqual(
            self.problems(),
            [
                "021 is used by two docs: docs/design/021-find-a-provider.org, "
                "docs/design/021-something-else.org"
            ],
        )

    def test_duplicate_task_id(self):
        write(self.root, "docs/design/021-find-a-provider.org", SEARCH_DOC)
        write(
            self.root,
            "docs/design/022-other.org",
            "#+TITLE: 022 - Other\n\n* Tasks\n\n** TODO [HL-021-04] Copied\n",
        )
        self.assertIn(
            "HL-021-04 appears twice: docs/design/021-find-a-provider.org:38, "
            "docs/design/022-other.org:5",
            self.problems(),
        )

    def test_task_number_does_not_match_doc(self):
        write(
            self.root,
            "docs/design/022-other.org",
            "#+TITLE: 022 - Other\n\n* Tasks\n\n** TODO [HL-021-07] Left behind by a rename\n",
        )
        self.assertEqual(
            self.problems(),
            ["HL-021-07 is in docs/design/022-other.org:5, whose number is 022"],
        )

    def test_suffixed_task_from_split_doc_is_allowed_if_aliased(self):
        write(
            self.root,
            "docs/design/022-other.org",
            "#+TITLE: 022 - Other\n#+ALIASES: HL-021 a..b\n\n* Tasks\n\n** DONE [HL-021-07] Old\n",
        )
        self.assertEqual(self.problems(), [])

    def test_working_state_in_complete_doc(self):
        write(
            self.root,
            "docs/design/019-what-to-say.org",
            DONE_DOC.replace("CLOSED: [2026-09-22]\n\n    ** DONE [HL-006", "CLOSED: [2026-09-22]\n    :PROPERTIES:\n    :HANDOFF: stale\n    :END:\n\n    ** DONE [HL-006"),
        )
        problems = self.problems()
        self.assertIn(
            "docs/design/019-what-to-say.org is Complete but still has working state: HL-019-01 :HANDOFF:",
            problems,
        )


class MainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, "docs/design/021-find-a-provider.org", SEARCH_DOC)

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *args):
        from io import StringIO

        out = StringIO()
        code = backlog.main(["--root", str(self.root), *args], stdout=out, stderr=StringIO())
        return code, out.getvalue()

    def test_default_view(self):
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("In progress\n"))

    def test_check_exit_code(self):
        write(self.root, "docs/design/021-dup.org", "#+TITLE: 021 - Dup\n")
        code, out = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("021 is used by two docs", out)

    def test_check_clean(self):
        code, out = self.run_main("--check")
        self.assertEqual((code, out), (0, "No problems.\n"))

    def test_next_number_without_git(self):
        code, out = self.run_main("--next-number")
        self.assertEqual(code, 0)
        self.assertEqual(out, "022\n")


if __name__ == "__main__":
    unittest.main()
