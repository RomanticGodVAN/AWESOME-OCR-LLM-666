#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any


def classify(paper: dict[str, Any]) -> str:
    text = ' '.join([
        paper.get('title', ''),
        paper.get('abstract', ''),
        ' '.join(paper.get('llm_tags', []) or []),
        paper.get('llm_reason', ''),
    ]).lower()

    rules = [
        (['benchmark', 'evaluation', 'metric', 'survey of ocr evaluation', 'historical documents'], 'Benchmarks and Evaluation'),
        (['table', 'tabular'], 'Table Understanding'),
        (['chart', 'plot', 'infographic'], 'Chart Understanding'),
        (['scene text', 'text spotting'], 'Scene Text Spotting'),
        (['formula', 'mathematical expression'], 'Mathematical Expression Recognition'),
        (['geometry', 'diagram'], 'Geometry Problem-solving'),
        (['reading order'], 'Reading Order Prediction'),
        (['layout', 'structure', 'physical structure'], 'Physical Structure Analysis'),
        (['dewarp', 'dewarping', 'rectification'], 'Document Dewarping'),
        (['generation', 'visual text generation'], 'Visual Text Generation'),
        (['understanding', 'reasoning', 'agentic', 'retrieval'], 'Visual Text Understanding'),
        (['parsing', 'ocr', 'document parsing'], 'Visual Text Parsing'),
    ]
    for keys, section in rules:
        if any(k in text for k in keys):
            return section
    return 'Visual Text Parsing'


def latest_papers_json(root: Path) -> Path:
    candidates = sorted(root.glob('document_ocr/*/papers.json'))
    if not candidates:
        raise FileNotFoundError(f'No papers.json found under {root / "document_ocr"}')
    return candidates[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--paper-daily-root', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--latest-only', action='store_true', default=True)
    args = ap.parse_args()

    src = latest_papers_json(Path(args.paper_daily_root))
    payload = json.loads(src.read_text(encoding='utf-8'))
    out = []
    for paper in payload.get('papers', []):
        if not paper.get('included', False):
            continue
        out.append({
            'title': paper.get('title', '').strip(),
            'url': paper.get('abs_url', '').strip(),
            'description': paper.get('title', '').strip(),
            'section': classify(paper),
        })
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {len(out)} entries from {src} to {args.out}')


if __name__ == '__main__':
    main()
