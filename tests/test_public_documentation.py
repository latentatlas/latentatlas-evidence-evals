import unittest
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
LATENTATLAS_DOC = ROOT / "docs" / "latentatlas-evidence-and-action-architecture.md"
CATEGORYVANTAGE_DOC = ROOT / "docs" / "categoryvantage-governed-kernel-architecture.md"
FROZEN_REVIEW_DOC = ROOT / "docs" / "frozen-masked-review.md"
AUTHORITY_ACTION_REPORT = ROOT / "docs" / "authority-action-v0-7-usable-pilot-results.md"
AUTHORITY_ACTION_REVIEW = ROOT / "docs" / "authority-action-internal-blind-review-v0-8.md"
CITATION = ROOT / "CITATION.cff"
PYPROJECT = ROOT / "pyproject.toml"


class PublicDocumentationTests(unittest.TestCase):
    def test_architecture_documents_exist_and_are_linked(self):
        readme = README.read_text(encoding="utf-8")

        for document in (LATENTATLAS_DOC, CATEGORYVANTAGE_DOC, FROZEN_REVIEW_DOC):
            self.assertTrue(document.is_file())
            self.assertIn(f"docs/{document.name}", readme)

    def test_latentatlas_document_preserves_research_contract(self):
        text = LATENTATLAS_DOC.read_text(encoding="utf-8")

        required_terms = (
            "Evidence qualification loop",
            "Action-time authority loop",
            "Masked review and calibration loop",
            "authority lease",
            "packet-sufficiency gate",
            "151",
            "146",
            "99",
            "22",
            "25",
            "10.5281/zenodo.20161629",
            "10.5281/zenodo.21243387",
            "10.5281/zenodo.21432540",
        )
        for term in required_terms:
            self.assertIn(term, text)

    def test_categoryvantage_document_preserves_kernel_architecture(self):
        text = CATEGORYVANTAGE_DOC.read_text(encoding="utf-8")

        for kernel in (
            "Identity Kernel",
            "Evidence Kernel",
            "Truth Kernel",
            "Publication Kernel",
            "Action Kernel",
            "Learning Kernel",
        ):
            self.assertIn(kernel, text)

    def test_frozen_review_artifact_is_documented_and_linked(self):
        readme = README.read_text(encoding="utf-8")
        document = FROZEN_REVIEW_DOC.read_text(encoding="utf-8")

        for path in (
            "data/frozen_masked_review_v1/manifest.json",
            "data/frozen_masked_review_v1/summary.json",
            "data/frozen_masked_review_v1/outcomes.csv",
            "latentatlas/frozen_review.py",
        ):
            self.assertTrue((ROOT / path).is_file(), path)
        self.assertIn("docs/frozen-masked-review.md", readme)
        self.assertIn("verify-frozen-review", readme)
        self.assertIn("verify-frozen-review", document)

    def test_authority_action_pilot_artifact_is_documented_and_linked(self):
        readme = README.read_text(encoding="utf-8")
        report = AUTHORITY_ACTION_REPORT.read_text(encoding="utf-8")

        for path in (
            "data/authority_action_v0_7_pilot/manifest.json",
            "data/authority_action_v0_7_pilot/summary.json",
            "latentatlas/authority_action_pilot.py",
        ):
            self.assertTrue((ROOT / path).is_file(), path)
            self.assertIn(path, readme)
        self.assertIn("verify-authority-action-pilot", readme)
        self.assertIn("verify-authority-action-pilot", report)

    def test_authority_action_review_artifact_is_documented_and_linked(self):
        readme = README.read_text(encoding="utf-8")
        review = AUTHORITY_ACTION_REVIEW.read_text(encoding="utf-8")

        for path in (
            "data/authority_action_v0_8_internal_review/manifest.json",
            "data/authority_action_v0_8_internal_review/summary.json",
            "latentatlas/authority_action_review.py",
        ):
            self.assertTrue((ROOT / path).is_file(), path)
            self.assertIn(path, readme)
        self.assertIn("verify-authority-action-review", readme)
        self.assertIn("verify-authority-action-review", review)

    def test_public_documents_do_not_expose_private_workspace_markers(self):
        forbidden = (
            "/Us" + "ers/",
            "sirket" + "ortagim",
            "approved" + " by:",
            "saban" + "ci",
            "docs/" + "planned",
        )

        for document in (
            LATENTATLAS_DOC,
            CATEGORYVANTAGE_DOC,
            FROZEN_REVIEW_DOC,
            AUTHORITY_ACTION_REPORT,
            AUTHORITY_ACTION_REVIEW,
        ):
            text = document.read_text(encoding="utf-8").lower()
            for marker in forbidden:
                self.assertNotIn(marker.lower(), text)

    def test_documented_public_modules_exist(self):
        expected_paths = (
            "latentatlas/evidence_guard.py",
            "latentatlas/evidence_index.py",
            "latentatlas/evidence_vector_layer.py",
            "latentatlas/schema_validator.py",
            "latentatlas/verify_outputs.py",
            "latentatlas/action_time_revalidation.py",
            "latentatlas/cli.py",
            "examples",
            "tests",
        )

        for relative_path in expected_paths:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_citation_and_community_files_are_present(self):
        readme = README.read_text(encoding="utf-8")
        citation = CITATION.read_text(encoding="utf-8")
        project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
        project_version = project["project"]["version"]

        expected_paths = (
            "CITATION.cff",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/research_question.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/pull_request_template.md",
        )
        for relative_path in expected_paths:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

        self.assertIn("CITATION.cff", readme)
        self.assertEqual("0.2.0", project_version)
        self.assertIn(f"version: {project_version}", citation)
        for doi in (
            "10.5281/zenodo.20161629",
            "10.5281/zenodo.21243387",
            "10.5281/zenodo.21432540",
        ):
            self.assertIn(doi, citation)


if __name__ == "__main__":
    unittest.main()
