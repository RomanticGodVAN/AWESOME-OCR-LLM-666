#!/usr/bin/env python3
import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

CANONICAL_SECTIONS = [
    "📄 Visual Text Parsing",
    "📄 Visual Text Understanding",
    "📄 Benchmarks and Evaluation",
    "📄 Specialized Model",
    "📄 Document Dewarping",
    "📄 Physical Structure Analysis",
    "📄 Reading Order Prediction",
    "📄 Mathematical Expression Recognition",
    "📄 Geometry Problem-solving",
    "📄 Table Understanding",
    "📄 Chart Understanding",
    "📄 Scene Text Spotting",
    "📄 Visual Text Generation",
]

ALIASES = {
    "visual text parsing": "📄 Visual Text Parsing",
    "parsing": "📄 Visual Text Parsing",
    "document parsing": "📄 Visual Text Parsing",
    "doc parsing": "📄 Visual Text Parsing",
    "visual text understanding": "📄 Visual Text Understanding",
    "understanding": "📄 Visual Text Understanding",
    "document understanding": "📄 Visual Text Understanding",
    "benchmarks and evaluation": "📄 Benchmarks and Evaluation",
    "benchmark": "📄 Benchmarks and Evaluation",
    "evaluation": "📄 Benchmarks and Evaluation",
    "specialized model": "📄 Specialized Model",
    "document dewarping": "📄 Document Dewarping",
    "dewarping": "📄 Document Dewarping",
    "physical structure analysis": "📄 Physical Structure Analysis",
    "layout": "📄 Physical Structure Analysis",
    "structure": "📄 Physical Structure Analysis",
    "reading order prediction": "📄 Reading Order Prediction",
    "reading order": "📄 Reading Order Prediction",
    "mathematical expression recognition": "📄 Mathematical Expression Recognition",
    "formula": "📄 Mathematical Expression Recognition",
    "geometry problem-solving": "📄 Geometry Problem-solving",
    "geometry": "📄 Geometry Problem-solving",
    "table understanding": "📄 Table Understanding",
    "table": "📄 Table Understanding",
    "chart understanding": "📄 Chart Understanding",
    "chart": "📄 Chart Understanding",
    "scene text spotting": "📄 Scene Text Spotting",
    "scene text": "📄 Scene Text Spotting",
    "visual text generation": "📄 Visual Text Generation",
    "text generation": "📄 Visual Text Generation",
}

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*$')
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
TABLE_ROW_RE = re.compile(r'^\|')

@dataclass
class Entry:
    title: str
    url: str
    description: str = ""
    section: str = ""


def norm(s: str) -> str:
    s = s.replace('📄', '').strip().lower()
    return re.sub(r'\s+', ' ', s)


def resolve_section(raw: str) -> str:
    raw_n = norm(raw)
    for sec in CANONICAL_SECTIONS:
        if raw_n == norm(sec):
            return sec
    if raw_n in ALIASES:
        return ALIASES[raw_n]
    for key, val in ALIASES.items():
        if key in raw_n:
            return val
    raise ValueError(f"Unknown section/category: {raw}")


def load_entries(json_path: str) -> List[Entry]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    out = []
    for item in data:
        out.append(Entry(
            title=item['title'],
            url=item['url'],
            description=item.get('description', ''),
            section=resolve_section(item['section']),
        ))
    return out


def split_sections(text: str) -> Tuple[List[str], Dict[str, List[str]]]:
    lines = text.splitlines()
    preamble, sections = [], {}
    current = None
    seen_first = False
    for line in lines:
        m = HEADING_RE.match(line)
        if m and norm(m.group(2)) in {norm(s) for s in CANONICAL_SECTIONS}:
            current = next(s for s in CANONICAL_SECTIONS if norm(s) == norm(m.group(2)))
            sections.setdefault(current, [])
            seen_first = True
            continue
        if not seen_first:
            preamble.append(line)
        elif current is not None:
            sections.setdefault(current, []).append(line)
        else:
            preamble.append(line)
    return preamble, sections


def extract_existing_keys(lines: List[str]):
    keys = set()
    for line in lines:
        m = LINK_RE.search(line)
        if m:
            keys.add((norm(m.group(1)), norm(m.group(2))))
            keys.add((norm(m.group(1)), ''))
            keys.add(('', norm(m.group(2))))
    return keys


def build_row(entry: Entry) -> str:
    venue = "-"
    name = f"`{entry.title}`"
    affiliation = "-"
    title = f"[{entry.description or entry.title}]({entry.url})"
    github = "-"
    date = "-"
    return f"| {venue} | {name} | {affiliation} | {title} | {github} | {date} |"


def inject_into_section(lines: List[str], entries: List[Entry]) -> List[str]:
    existing_keys = extract_existing_keys(lines)
    out = list(lines)
    insert_at = None
    header_seen = False
    for i, line in enumerate(out):
        if TABLE_ROW_RE.match(line):
            header_seen = True
            continue
        if header_seen and not TABLE_ROW_RE.match(line):
            insert_at = i
            break
    if insert_at is None:
        if not out or not TABLE_ROW_RE.match(out[0]):
            out = [
                "| Venue | Name | Primary affiliation | Title | GitHub | Date |",
                "|:-:|:-:|:-:|:-:|:-:|:-:|",
                ""
            ] + out
            insert_at = 2
        else:
            insert_at = len(out)
    rows_to_add = []
    for e in entries:
        if (norm(e.title), '') in existing_keys or ('', norm(e.url)) in existing_keys:
            continue
        rows_to_add.append(build_row(e))
    if rows_to_add:
        if insert_at < len(out) and out[insert_at] != '':
            rows_to_add.append('')
        out[insert_at:insert_at] = rows_to_add
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', required=True)
    ap.add_argument('--json', required=True)
    args = ap.parse_args()

    entries = load_entries(args.json)
    with open(args.md, 'r', encoding='utf-8') as f:
        text = f.read()

    preamble, sections = split_sections(text)
    grouped: Dict[str, List[Entry]] = {}
    for e in entries:
        grouped.setdefault(e.section, []).append(e)

    for sec, items in grouped.items():
        sections[sec] = inject_into_section(sections.get(sec, []), items)

    rebuilt = []
    rebuilt.extend(preamble)
    if rebuilt and rebuilt[-1] != '':
        rebuilt.append('')
    for sec in CANONICAL_SECTIONS:
        rebuilt.append(f"## {sec}")
        rebuilt.extend(sections.get(sec, ['']))
        if rebuilt and rebuilt[-1] != '':
            rebuilt.append('')
    with open(args.md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rebuilt).rstrip() + '\n')
    print(f"Updated {args.md} with {len(entries)} entries")

if __name__ == '__main__':
    main()
