# payArc — Discovery Materials

This folder holds **raw source material** about payment gateways:
articles, specs, blog posts, screenshots, transcripts, notes, internal
references — anything that informs the project.

## How to add material

- Drop the file directly into this folder.
- Filename should describe the source: `2026-05-stripe-architecture-blog.md`,
  `pci-dss-v4-summary.pdf`, `acquirer-flow-diagram.png`.
- Keep originals as-is. **Do not edit raw materials.** Notes & summaries go
  in [`SOURCES.md`](SOURCES.md).
- For text that's just pasted into chat without a filename, use:
  `YYYY-MM-DD-topic.md` and put the user's full text inside, plus a header
  with the date and a short note about where it came from.

## How the agent processes material

When a new file lands here, the agent should:

1. Read it carefully (Russian / English / mixed — all fine).
2. Append a one-paragraph summary + citation to [`SOURCES.md`](SOURCES.md).
3. Update [`../vision.md`](../vision.md) if the framing shifts.
4. Update [`../glossary.md`](../glossary.md) with any new domain terms.
5. Append unresolved items to [`../questions.md`](../questions.md).
6. **Never rewrite or delete the original source file.**

## Inventory

The current index of source materials lives in
[`SOURCES.md`](SOURCES.md).
