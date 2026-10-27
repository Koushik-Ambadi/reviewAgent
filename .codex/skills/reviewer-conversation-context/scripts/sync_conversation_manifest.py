from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def _sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _message_from_node(node: dict[str, Any]) -> dict[str, Any] | None:
    message = node.get("message")
    if not isinstance(message, dict):
        return None

    author = message.get("author") or {}
    content = message.get("content") or {}
    parts = content.get("parts")
    if not isinstance(parts, list):
        parts = []

    normalized_parts = [
        part for part in parts if isinstance(part, (str, int, float, bool))
    ]
    return {
        "id": message.get("id"),
        "role": author.get("role"),
        "create_time": message.get("create_time"),
        "content_type": content.get("content_type"),
        "parts": normalized_parts,
    }


def _messages(conversation: dict[str, Any]) -> list[dict[str, Any]]:
    supplied = conversation.get("messages")
    if isinstance(supplied, list):
        return [item for item in supplied if isinstance(item, dict)]

    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return []

    messages = []
    for node in mapping.values():
        if isinstance(node, dict):
            normalized = _message_from_node(node)
            if normalized is not None:
                messages.append(normalized)

    return sorted(
        messages,
        key=lambda item: (
            item.get("create_time") is None,
            item.get("create_time") or 0,
            item.get("id") or "",
        ),
    )


def _conversation_id(conversation: dict[str, Any]) -> str | None:
    value = conversation.get("id") or conversation.get("conversation_id")
    return str(value) if value else None


def _normalize(
    conversation: dict[str, Any], project_url: str
) -> dict[str, Any] | None:
    conversation_id = _conversation_id(conversation)
    if conversation_id is None:
        return None

    messages = _messages(conversation)
    content_sha256 = _sha256(messages) if messages else None
    title = str(conversation.get("title") or "Untitled")
    url = conversation.get("url") or (
        f"{project_url.rsplit('/project', 1)[0]}/c/{conversation_id}"
    )
    return {
        "id": conversation_id,
        "title": title,
        "url": str(url),
        "updated_at": conversation.get("update_time")
        or conversation.get("updated_at"),
        "turn_count": len(messages),
        "content_sha256": content_sha256,
        "metadata_sha256": _sha256(
            {"id": conversation_id, "title": title, "url": str(url)}
        ),
    }


def _conversation_items(payload: Any) -> Iterable[dict[str, Any]]:
    if isinstance(payload, list):
        return (item for item in payload if isinstance(item, dict))
    if isinstance(payload, dict) and isinstance(payload.get("conversations"), list):
        return (
            item for item in payload["conversations"] if isinstance(item, dict)
        )
    raise ValueError(
        "Input must be a ChatGPT conversations list or an object with conversations[]"
    )


def build_manifest(payload: Any, project_url: str) -> dict[str, Any]:
    conversations = [
        normalized
        for item in _conversation_items(payload)
        if (normalized := _normalize(item, project_url)) is not None
    ]
    conversations.sort(key=lambda item: (item["title"].casefold(), item["id"]))
    return {
        "schema_version": "1.0",
        "project_url": project_url,
        "capture_method": "local_export_or_normalized_capture",
        "capture_completeness": "complete_input_only",
        "conversations": conversations,
        "manifest_sha256": _sha256(conversations),
    }


def compare(
    previous: dict[str, Any], current: dict[str, Any]
) -> dict[str, list[str]]:
    old = {item["id"]: item for item in previous.get("conversations", [])}
    new = {item["id"]: item for item in current.get("conversations", [])}
    return {
        "added": sorted(new.keys() - old.keys()),
        "changed": sorted(
            key
            for key in new.keys() & old.keys()
            if new[key].get("content_sha256")
            != old[key].get("content_sha256")
            or new[key].get("metadata_sha256")
            != old[key].get("metadata_sha256")
        ),
        "unchanged": sorted(
            key
            for key in new.keys() & old.keys()
            if new[key].get("content_sha256")
            == old[key].get("content_sha256")
            and new[key].get("metadata_sha256")
            == old[key].get("metadata_sha256")
        ),
        "missing_from_input": sorted(old.keys() - new.keys()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize a ChatGPT conversation export and report content changes."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--project-url", required=True)
    parser.add_argument(
        "--check", action="store_true", help="Compare without writing output"
    )
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    manifest = build_manifest(payload, args.project_url)
    previous = (
        json.loads(args.output.read_text(encoding="utf-8"))
        if args.output.exists()
        else {"conversations": []}
    )
    changes = compare(previous, manifest)

    if not args.check:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        temporary.replace(args.output)

    print(json.dumps(changes, indent=2))
    changed = changes["added"] or changes["changed"] or changes["missing_from_input"]
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
