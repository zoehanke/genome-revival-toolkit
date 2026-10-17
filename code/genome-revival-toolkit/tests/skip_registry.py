"""D18 registered optional-test skips, distinct from a successful verification."""
from datetime import date
from functools import wraps
import json
from pathlib import Path


def skip_with(reason_id, *, condition):
    def decorate(function):
        @wraps(function)
        def run(case, *arguments, **parameters):
            records = json.loads((Path(__file__).parent / "SKIPS.json").read_text(encoding="utf-8"))
            record = next((row for row in records if row.get("id") == reason_id), None)
            if record is None or not all(record.get(key) for key in ("test", "reason", "condition", "owner", "expires")):
                raise AssertionError("Missing or incomplete registered skip: " + reason_id)
            if record["expires"] < date.today().isoformat():
                raise AssertionError("Expired registered skip: " + reason_id)
            if condition():
                case.skipTest(reason_id + ": " + record["reason"] + " NOT_PERFORMED; not PASS.")
            return function(case, *arguments, **parameters)
        return run
    return decorate
