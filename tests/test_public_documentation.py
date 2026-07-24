import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
LATENTATLAS_DOC = ROOT / "docs" / "latentatlas-evidence-and-action-architecture.md"
CATEGORYVANTAGE_DOC = ROOT / "docs" / "categoryvantage-governed-kernel-architecture.md"


class PublicDocumentationTests(unittest.TestCase):
    def test_architecture_documents_exist_and_are_linked(self):
        readme = README.read_text(encoding="utf-8")

        for document in (LATENTATLAS_DOC, CATEGORYVANTAGE_DOC):
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

    def test_public_documents_do_not_expose_private_workspace_markers(self):
        forbidden = (
            "/Us" + "ers/",
            "sirket" + "ortagim",
            "approved" + " by:",
            "saban" + "ci",
            "docs/" + "planned",
        )

        for document in (LATENTATLAS_DOC, CATEGORYVANTAGE_DOC):
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


if __name__ == "__main__":
    unittest.main()
