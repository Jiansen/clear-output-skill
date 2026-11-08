import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load_tool("check_responses")
builder = load_tool("make_prompt")


class ContractTests(unittest.TestCase):
    def test_literal_change_is_detected(self):
        text = "Run `tool --dry-run --path './draft files'`. If `E_LOCKED: resource busy` appears, check `/var/run/widget.lock`."
        self.assertEqual(checker.check_response("c13", text), [])
        self.assertTrue(checker.check_response("c13", text.replace("--dry-run", "--run")))

    def test_formatting_around_literal_is_allowed(self):
        self.assertEqual(checker.check_response("c22", "请求 `/v1/items?limit=1`。阈值尚未确定。"), [])

    def test_raw_json_contract(self):
        text = '{"observation":"ERROR E_CONN_TIMEOUT","next_step":"Check reachability."}'
        self.assertEqual(checker.check_response("c07", text), [])
        for invalid in ["```json\n" + text + "\n```", text + "\nDone.", text.replace("next_step", "next"), text.replace('"Check reachability."', "false")]:
            with self.subTest(invalid=invalid):
                self.assertTrue(checker.check_response("c07", invalid))

    def test_duplicate_json_keys_are_rejected(self):
        text = '{"observation":"wrong","observation":"ERROR E_CONN_TIMEOUT","next_step":"Check."}'
        self.assertTrue(checker.check_response("c07", text))

    def test_error_must_be_in_observation(self):
        self.assertTrue(checker.check_response("c07", '{"observation":"Timeout.","next_step":"ERROR E_CONN_TIMEOUT"}'))

    def test_coverage_rejects_missing_duplicate_and_unknown(self):
        cases = [{"id": "x1"}, {"id": "x2"}]
        data = {"responses": [{"id": "x1", "response": "A"}, {"id": "x1", "response": "B"}, {"id": "x3", "response": "C"}]}
        errors = checker.check_bundle(data, cases)
        self.assertEqual({e["error"] for e in errors}, {"Duplicate response.", "Unknown case.", "Missing response."})

    def test_malformed_response_is_reported(self):
        for item in [None, {"id": [], "response": "A"}, {"id": "x1", "response": None}]:
            with self.subTest(item=item):
                self.assertTrue(checker.check_bundle({"responses": [item]}, [{"id": "x1"}]))

    def test_noop_contract_rejects_extra_commentary(self):
        text = "如果文件不存在，系统会返回错误。"
        self.assertEqual(checker.check_response("c14", text), [])
        self.assertTrue(checker.check_response("c14", "原文已经清楚：" + text))

    def test_checker_does_not_claim_semantic_coverage(self):
        # A wrong meaning can pass exact checks. This limitation is intentional.
        self.assertEqual(checker.check_response("c22", "/v1/items?limit=1 已测试通过，阈值为 90%。"), [])


class EvaluationInputTests(unittest.TestCase):
    def test_case_rubric_alignment(self):
        cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        rubrics = json.loads((ROOT / "evals/rubric.json").read_text())["cases"]
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [case["id"] for case in rubrics])
        for case in cases:
            self.assertEqual(case["messages"][-1]["role"], "user")
            self.assertTrue(all(message["content"] for message in case["messages"]))

    def test_prompt_does_not_include_private_rubric(self):
        cases_path = ROOT / "evals/cases.json"
        for condition in ["baseline", "short-prompt", "full-skill"]:
            with self.subTest(condition=condition):
                prompt = builder.make_prompt(condition, cases_path)
                self.assertNotIn('"invariants"', prompt)
                self.assertIn('"c24"', prompt)
        self.assertNotIn("# Clear Output", builder.make_prompt("baseline", cases_path))
        self.assertIn("# Clear Output", builder.make_prompt("full-skill", cases_path))


if __name__ == "__main__":
    unittest.main()
