# Automated Update Workflow

This repository should not rely on direct manual LLM rewriting of the curated markdown list.

## Rule

Use `scripts/update_awesome_md.py` to update `README.md` from machine-readable payloads in `data/awesome_updates.json`.

## Local update

```bash
bash scripts/run_auto_update.sh data/awesome_updates.json README.md
```

## Payload format

```json
[
  {
    "title": "Paper or Project Name",
    "url": "https://...",
    "description": "Short description or title text",
    "section": "Visual Text Parsing"
  }
]
```

## Auto push

- Local script commits and pushes changes automatically when README changes.
- GitHub Actions also runs on schedule and on payload updates.

## Managed sections

- Visual Text Parsing
- Visual Text Understanding
- Benchmarks and Evaluation
- Specialized Model
- Document Dewarping
- Physical Structure Analysis
- Reading Order Prediction
- Mathematical Expression Recognition
- Geometry Problem-solving
- Table Understanding
- Chart Understanding
- Scene Text Spotting
- Visual Text Generation
