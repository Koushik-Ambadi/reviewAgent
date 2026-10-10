from repo_review.analysis.runner import summarize_symbol_inventory
from repo_review.contracts import StageResult, StageStatus, StageSummary
from repo_review.reporting.formatter import REPORT_VERSION
from repo_review.reporting.serializer import serialize


def test_symbol_inventory_summary_counts_extracted_records_without_claiming_audit():
    symbols = [
        {
            "functions_defined": [{"name": "run"}],
            "functions_declared": [{"name": "init"}],
            "globals": [{"name": "g_state"}],
            "locals": [{"name": "value"}, {"name": "index"}],
            "parameters": [{"name": "input"}],
            "structs": [{"name": "State"}],
            "enums": [{"name": "Mode", "constants": [{"name": "OFF"}, {"name": "ON"}]}],
            "typedefs": [{"name": "StateType"}],
            "macros": [{"name": "LIMIT"}, {"name": "CLAMP"}],
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
    assert counts["enum_constants"] == 2
    assert counts["macros"] == 3
    assert inventory.audit.status == "not_tracked"
    assert inventory.audit.audited is None
    assert inventory.audit.pending_approval is None
    assert inventory.audit.not_audited is None

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
    assert payload["inventory"]["audit"]["audited"] is None
    assert REPORT_VERSION == "2.1"
