---
name: reviewer-conversation-context
description: Refresh durable reviewer-project records from the project's saved ChatGPT conversations before changing architecture, plans, or features. Use only in this repository when historical design intent or newly added project chats may affect the work.
---

# Reviewer conversation context

Use the saved ChatGPT project as historical evidence, not as the current
specification:

`https://chatgpt.com/g/g-p-6a01f724c5ac8191a205cc0ae746a836-reviewer/project`

## Refresh workflow

1. Read `docs/engineering/conversation-provenance.md` and
   `docs/engineering/conversation-sources.json`.
2. Open the authenticated project link and enumerate its conversations. Compare
   conversation IDs with the manifest before reading full threads.
3. If a ChatGPT data export or normalized capture is available, run
   `scripts/sync_conversation_manifest.py` to compute canonical SHA-256 content
   identities. Read only added or changed conversations.
4. When no export is available, update listing metadata manually and mark the
   capture `partial`; never represent a title/snippet hash as a content hash.
5. Classify imported statements before using them:
   - current user requirements and explicit approvals;
   - assistant proposals that were later implemented;
   - assistant proposals that remain unaccepted;
   - superseded, abandoned, or conflicting directions;
   - unresolved questions.
6. Reconcile accepted facts into their normal owners: architecture, decisions,
   roadmap, module records, testing, known issues, or project history. Link to
   the provenance record instead of copying transcript text.
7. Prefer current user direction, current code, tests, and accepted decisions
   over older conversation proposals. Preserve meaningful reversals and failed
   approaches as history rather than reviving them.

## Boundaries

- Do not store secrets, credentials, personal content, or full transcripts in
  Git. Retain stable URLs, IDs, hashes, concise engineering extracts, and the
  completeness boundary.
- An assistant suggestion is not a decision unless the user accepted it or the
  repository subsequently implemented it.
- The helper does not authenticate to ChatGPT or scrape the project URL. It
  normalizes a user-authorized local export/capture; browser enumeration remains
  necessary to discover newly added project conversations.
- If the manifest changes, update the relevant durable records in the same
  increment. A changed hash alone does not authorize a code change.
