"""Message precision does not change which schema instances are rejected."""
import unittest

from dna_design_core.kernel import schemas


class SchemaMessageTests(unittest.TestCase):
    def test_nested_required_paths_escape_json_pointer(self):
        shape = {"type": "object", "properties": {"a/b": {"type": "object", "required": ["~name"]}}}
        self.assertEqual(schemas.issues(shape, {"a/b": {}}), [{
            "location": "/a~1b/~0name", "rule": "required", "reason": "Required field is missing."}])

    def test_diagnostics_preserve_validation_for_constructed_cases(self):
        shape = {"type": "object", "properties": {"count": {"type": "integer", "minimum": 1}},
                 "required": ["count"], "additionalProperties": False}
        for value, valid in (({"count": 1}, True), ({}, False), ({"count": 0}, False),
                             ({"count": "1"}, False), ({"count": 1, "extra": 1}, False)):
            with self.subTest(value=value):
                self.assertEqual(not schemas.issues(shape, value), valid)
                self.assertEqual(schemas.validator(shape).is_valid(value), valid)

    def test_messages_do_not_echo_submitted_sequence_or_value(self):
        submitted = "ACGT" * 80
        rows = schemas.issues({"type": "integer"}, submitted)
        self.assertNotIn(submitted, str(rows))
        self.assertEqual(rows[0]["rule"], "type")


if __name__ == "__main__":
    unittest.main()
