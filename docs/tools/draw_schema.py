"""Draw img/authors.svg, the structure of an inspire_LA record (see docs/data-schema.md).

Usage: python docs/tools/draw_schema.py [img/authors.svg]
"""
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# fill, stroke by source (docs/data-schema.md)
SRC = {'lit': ('#e6e6e6', '#7f7f7f'), 'prof': ('#d9ead3', '#6a9a5b'), 'inst': ('#f4cccc', '#b85c5c'),
       'calc': ('#cfe2f3', '#5b8bb8')}
GROUPS = [
    ('fields', 'of each record', 'lit', [
        ('author_id', 'lit'), ('profile_id', 'lit'), ('full_name', 'lit'), ('institution', 'lit'),
        ('institution_id', 'lit'), ('country', 'inst'), ('email_addresses *', 'prof'),
        ('first_names', 'calc'), ('gender', 'calc'), ('gender_probability', 'calc')]),
    ('name', 'object', 'prof', [
        ('value', 'prof'), ('preferred_name', 'prof'), ('name_variants[]', 'prof'), ('native_names[]', 'prof'),
        ('previous_names[]', 'prof'), ('numeration', 'prof')]),
    ('ids[]', 'INSPIRE BAI, ORCID, SPIRES, …', 'prof', [
        ('schema', 'prof'), ('value', 'prof')]),
    ('positions[]', 'list, or null', 'prof', [
        ('institution', 'prof'), ('record.$ref', 'prof'), ('rank', 'prof'), ('start_date', 'prof'),
        ('end_date', 'prof'), ('current', 'prof'), ('curated_relation', 'prof'), ('hidden', 'prof'),
        ('institution_id', 'calc'), ('country', 'calc'), ('author_id', 'calc')]),
    ('advisors[]', 'list', 'prof', [
        ('name', 'prof'), ('degree_type', 'prof'), ('ids[]', 'prof'), ('record.$ref', 'prof'),
        ('curated_relation', 'prof'), ('hidden', 'prof')]),
    ('papers[]', 'same list in every record of the author', 'lit', [
        ('recid', 'lit'), ('year', 'lit'), ('citation_count', 'lit'), ('journal_id', 'lit'),
        ('primary_arxiv_category[]', 'lit'), ('author_id', 'lit'), ('institution_id', 'lit'),
        ('— at publication —', None), ('rank', 'calc'), ('institution', 'calc'), ('country', 'calc'),
        ('start_date', 'calc'), ('end_date', 'calc'), ('current', 'calc')]),
]
LEGEND = [('lit', 'INSPIRE literature (papers and their authors)'), ('prof', 'INSPIRE author profile'),
          ('inst', 'INSPIRE institution record'), ('calc', 'computed when the file is built')]

W, COLW, GAP, X0 = 1480, 222, 22, 24
TOP, HEAD_H, ROW_H = 150, 46, 30


def main(out):
    parts = []
    add = parts.append
    rows = max(len(g[3]) for g in GROUPS)
    H = TOP + HEAD_H + 16 + rows * ROW_H + 86
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'font-family="Helvetica, Arial, sans-serif">')
    add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    add('<text x="24" y="40" font-size="24" fill="#222">data/inspire_LA.json.gz: a list of records</text>')
    add('<text x="24" y="66" font-size="14" fill="#555">One record per author and institution; '
        'all records of an author share profile, gender and papers. Count authors by author_id, papers by '
        'papers[].recid.</text>')
    # root
    rx, ry, rw, rh = W / 2 - 120, 88, 240, 40
    add(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="6" fill="#cccccc" stroke="#595959"/>')
    add(f'<text x="{W / 2}" y="{ry + 26}" font-size="18" text-anchor="middle" fill="#111">record</text>')
    for i, (title, sub, src, fields) in enumerate(GROUPS):
        x = X0 + i * (COLW + GAP)
        fill, stroke = SRC[src]
        cx = x + COLW / 2
        add(f'<path d="M{W / 2} {ry + rh} C {W / 2} {ry + rh + 20}, {cx} {TOP - 24}, {cx} {TOP}" fill="none" '
            'stroke="#8c8c8c" stroke-width="1.3"/>')
        add(f'<rect x="{x}" y="{TOP}" width="{COLW}" height="{HEAD_H}" rx="4" fill="{fill}" stroke="{stroke}" '
            'stroke-width="1.5"/>')
        add(f'<text x="{cx}" y="{TOP + 21}" font-size="17" text-anchor="middle" fill="#111" '
            f'font-family="Menlo, Consolas, monospace">{escape(title)}</text>')
        add(f'<text x="{cx}" y="{TOP + 38}" font-size="11" text-anchor="middle" fill="#444">{escape(sub)}</text>')
        y = TOP + HEAD_H + 14
        add(f'<line x1="{cx}" y1="{TOP + HEAD_H}" x2="{cx}" y2="{y + (len(fields) - 1) * ROW_H + 4}" '
            'stroke="#b3b3b3" stroke-width="1"/>')
        for name, fsrc in fields:
            if fsrc is None:
                add(f'<text x="{cx}" y="{y + 15}" font-size="11.5" text-anchor="middle" fill="#3d6d99" '
                    f'font-style="italic">{escape(name)}</text>')
            else:
                f, s = SRC[fsrc]
                add(f'<rect x="{x + 10}" y="{y}" width="{COLW - 20}" height="{ROW_H - 7}" rx="11" fill="{f}" '
                    f'stroke="{s}"/>')
                add(f'<text x="{cx}" y="{y + 16}" font-size="12.5" text-anchor="middle" fill="#111" '
                    f'font-family="Menlo, Consolas, monospace">{escape(name)}</text>')
            y += ROW_H
    ly = H - 52
    lx = 24
    add(f'<text x="{lx}" y="{ly + 15}" font-size="13" fill="#333">Source:</text>')
    lx += 66
    for key, label in LEGEND:
        f, s = SRC[key]
        add(f'<rect x="{lx}" y="{ly}" width="26" height="20" rx="8" fill="{f}" stroke="{s}"/>')
        add(f'<text x="{lx + 34}" y="{ly + 15}" font-size="13" fill="#333">{escape(label)}</text>')
        lx += 34 + 6.6 * len(label) + 34
    add(f'<text x="24" y="{H - 14}" font-size="12" fill="#666">* null since the 2026 rebuild (the INSPIRE API no '
        'longer gives e-mails). Fields and counts: docs/data-schema.md; JSON Schema: docs/inspire_LA.schema.json.</text>')
    add('</svg>')
    Path(out).write_text('\n'.join(parts) + '\n', encoding='utf-8')
    print(f'wrote {out} ({W}x{H})')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'img/authors.svg')
