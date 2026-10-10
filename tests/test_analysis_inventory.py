from repo_review.analysis.runner import summarize_symbol_inventory
from repo_review.contracts import StageResult, StageStatus, StageSummary
from repo_review.reporting.formatter import REPORT_VERSION
from repo_review.reporting.serializer import serialize


def test_symbol_inventory_builds_grouped_audit_register():
    symbols = [
        {
            "file": "src/control.c",
            "functions_defined": [{"name": "run", "line": 8}],
            "functions_declared": [{"name": "init", "line": 4}],
            "globals": [{"name": "g_state"}],
            "locals": [{"name": "value"}, {"name": "index"}],
            "parameters": [{"name": "input"}],
            "structs": [
                {
                    "name": "State",
                    "line": 20,
                    "fields": [{"name": "charge", "type": "uint8_t", "line": 21}],
                }
            ],
            "enums": [{"name": "Mode", "constants": [{"name": "OFF"}, {"name": "ON"}]}],
            "typedefs": [{"name": "StateType"}],
            "macros": [
                {"name": "LIMIT", "line": 2, "type": "value", "replacement": "100"},
                {"name": "CLAMP", "line": 3, "type": "function", "replacement": "(x)"},
            ],
        },
        {
            "functions_defined": [{"name": "stop"}],
            "functions_declared": [],
            "globals": [],
            "locals": [{"name": "result"}],
            "parameters": [],
            "structs": [],
            "enums": [],
            "typedefs": [],
            "macros": [{"name": "VERSION"}],
        },
    ]

    inventory = summarize_symbol_inventory(
        symbols,
        skipped_files=[{"file": "ignored.c", "reason": "outside_target_folder"}],
    )
    counts = {item.inventory_id: item.identified for item in inventory.items}

    assert inventory.parsed_files == 2
    assert inventory.skipped_files == 1
    assert counts["function_definitions"] == 2
    assert counts["local_variables"] == 3
    assert counts["structure_fields"] == 1
    assert counts["enum_constants"] == 2
    assert counts["macros"] == 3
    assert inventory.audit.status == "inventory_initialized"
    assert inventory.audit.audited == 0
    assert inventory.audit.pending_approval == 0
    assert inventory.audit.not_audited == sum(counts.values())

    groups = {group.group_id: group for group in inventory.groups}
    macro = groups["macros"].artifacts[0]
    field = groups["structure_fields"].artifacts[0]
    assert macro.audit_status == "not_audited"
    assert macro.audit_reason is None
    assert macro.location == "src/control.c:2"
    assert "Macro type: value" in macro.evidence
    assert "Replacement: 100" in macro.evidence
    assert field.name == "State.charge"
    assert field.location == "src/control.c:21"
    assert "Type: uint8_t" in field.evidence

    repeated = summarize_symbol_inventory(symbols)
    assert repeated.groups[0].artifacts[0].artifact_id == inventory.groups[0].artifacts[0].artifact_id

    payload = serialize(
        StageResult(
            title="Analysis",
            stage_id="analysis",
            status=StageStatus.COMPLETED,
            summary=StageSummary(),
            inventory=inventory,
        )
    )
    assert payload["inventory"]["items"][0]["identified"] == 2
    assert payload["inventory"]["groups"][6]["artifacts"][0]["audit_status"] == "not_audited"
    assert payload["inventory"]["audit"]["not_audited"] == sum(counts.values())
    assert REPORT_VERSION == "2.2"
