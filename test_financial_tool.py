
import json

from app.discovery import discover
from app.tools import financial
import sys

sys.stdout.reconfigure(encoding="utf-8")

class NoLLMFallback:
    def with_structured_output(self, *args, **kwargs):
        raise AssertionError(
            "Unexpected LLM fallback: metrics are missing."
        )


documents = discover(3)

result = financial(
    documents,
    NoLLMFallback()
)

print(json.dumps(
    result,
    indent=2,
    ensure_ascii=False
))

expected = {
    "2026-03": (70698, 13718, 25.3),
    "2026-06": (72275, 13849, 24.0),
    "2026-09": (73188, 13884, 24.0)
}

names = (
    "revenue_from_operations",
    "net_profit",
    "operating_margin"
)

assert len(result["metrics"]) == 3

for row in result["metrics"]:
    actual = tuple(row[name] for name in names)

    assert actual == expected[row["quarter"]], (
        f"Incorrect metrics: {row}"
    )

assert len(result["evidence"]) == 9

june_profit = next(
    e for e in result["evidence"]
    if e["id"] == "F-2026-06-net_profit"
)

assert june_profit["source_quarter"] == "2026-09"

assert june_profit["extraction_method"] == (
    "comparative_table"
)

print("\n===== FINANCIAL TOOL TEST =====")
print("Financial metrics: PASS")
print("Reference value accuracy: PASS")
print("Evidence coverage: PASS")
print("Cross-report provenance: PASS")
print("LLM calls required: 0")
print("Overall result: PASS")
