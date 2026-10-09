from copy import deepcopy
import json
import unittest
from bind_arms import CASE_ID, EXPECTED, build, validate_original
from contract import LAB

class BindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cards=json.loads((LAB/"stop_scope_suite/design/core_case_bindings_2026_10_08/CARDS.json").read_text())
        cls.card=next(c for c in cards["cards"] if c["case_id"]==CASE_ID)
    def test_original_eight_preserved(self):
        self.assertEqual(len(validate_original(self.card)),8)
        b=build()
        self.assertEqual({x["arm_id"]:x["original_component_ids"] for x in b["arms"]},EXPECTED)
    def test_added_admission_not_silently_equivalent(self):
        c=deepcopy(self.card)
        c["original_contract"]["interventions"][3]["component_ids"].append("ADMISSION")
        with self.assertRaises(ValueError):validate_original(c)
    def test_missing_or_duplicate_arm_rejected(self):
        c=deepcopy(self.card)
        c["original_contract"]["interventions"][-1]=c["original_contract"]["interventions"][0]
        with self.assertRaises(ValueError):validate_original(c)
    def test_refresh_not_bound_as_original_cancel(self):
        self.assertFalse(build()["cancellation_preflight"]["refresh_probe_is_original_cancel_arm"])
    def test_no_case_completion_or_pooling(self):
        b=build()
        self.assertFalse(b["original_case_complete"])
        self.assertEqual(b["catalogue_cases_certified"],0)
        self.assertTrue(all(not a["original_arm_fully_verified"] for a in b["arms"]))
        self.assertEqual(next(g for g in b["obligations"] if g["id"]=="G04")["status"],"open")
    def test_reversed_effect_order_not_claimed(self):
        b=build()
        self.assertEqual(next(g for g in b["obligations"] if g["id"]=="G09")["status"],"open")
        self.assertEqual(b["mechanism_alignment"]["status"],"explicit_topology_binding_required")

if __name__=="__main__":unittest.main()

