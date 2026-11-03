"""Compare reproduce.py results with the tables of the manuscript.

Usage: python reproduce/compare.py jdis-version.tex results.json page_data.json
       python reproduce/compare.py reproduce/paper/tables.json results.json page_data.json
       python reproduce/compare.py --dump jdis-version.tex reproduce/paper/tables.json

The printed tables can come from the manuscript (.tex) or from tables.json, the
same rows extracted with --dump, so the comparison runs without the manuscript.
"""
import json
import re
import sys

from reproduce import LA, RANKS, WORLD, CONTEXT

ABBR = {'Dom Rep': 'Dominican Republic'}


def tex_table(tex, label):
    """Rows {country: [cells]} of the tabular just before \\label{label}."""
    end = tex.index('\\label{' + label + '}')
    start = tex.rindex('\\begin{tabular}', 0, end)
    body = tex[start:end].split('\\midrule', 1)[1].split('\\botrule', 1)[0]
    rows = {}
    for line in body.split('\n'):
        line = line.strip()
        if not line or line.startswith('%') or '&' not in line:
            continue
        cells = [re.sub(r'\\DR\{([^}]*)\}', r'\1', c).replace('\\hline', '').replace('\\\\', '').strip()
                 for c in line.split('&')]
        rows[ABBR.get(cells[0], cells[0])] = cells[1:]
    return rows


LABELS = ['table:authors', 'table:publications', 'table:citations', 'table:h-index',
          'table:rank-authors', 'table:authors-2', 'tab:my_label']


def paper_tables(path):
    """{label: {row: [cells]}} from the .tex or from a tables.json written by --dump."""
    if str(path).endswith('.json'):
        return json.load(open(path, encoding='utf-8'))
    tex = open(path, encoding='utf-8').read()
    return {label: tex_table(tex, label) for label in LABELS}


def num(s):
    s = s.replace('$', '').replace(',', '').strip()
    if s in ('-', '---', ''):
        return 0
    m = re.match(r'([\d.]+)\s*\\pm\s*([\d.]+)', s)
    return (float(m.group(1)), float(m.group(2))) if m else float(s)


def main(tex_path, res_path, out_path):
    printed = paper_tables(tex_path)
    res = json.load(open(res_path))
    cc = res['countries']
    tables = []

    def add(key, title, label, cols, ours, digits):
        paper = printed[label]
        rows = []
        for c in LA:
            p = [num(x) for x in paper[c]]
            o = ours(c)
            rows.append({'country': c, 'paper': p, 'ours': o})
        tables.append({'key': key, 'title': title, 'label': label, 'cols': cols,
                       'digits': digits, 'rows': rows})

    add('authors', 'Authors', 'table:authors',
        ['Total authors', 'Active authors', 'Total PMI', 'Active PMI'],
        lambda c: [cc[c]['authors'], cc[c]['active_authors'], cc[c]['authors_pmi'], cc[c]['active_pmi']],
        [0, 0, 0, 0])
    add('publications', 'Publications', 'table:publications',
        ['Total', 'PMI', 'Per author'],
        lambda c: [cc[c]['papers'], cc[c]['papers_pmi'], cc[c]['papers_per_author']], [0, 0, 0])
    add('citations', 'Citations', 'table:citations',
        ['Total', 'PMI', 'Per author'],
        lambda c: [cc[c]['citations'], cc[c]['citations_pmi'], cc[c]['citations_per_author']], [0, 0, 0])
    add('hindex', 'h-index', 'table:h-index',
        ['h-index', 'PMI', 'Per author'],
        lambda c: [cc[c]['h_index'], cc[c]['h_pmi'], cc[c]['h_per_author']], [0, 0, 2])
    rank_cols = ['Senior', 'Junior', 'Staff', 'Postdoc', 'PhD', 'Master', 'Undergrad', 'Visitor', 'Other']
    add('ranks_authors', 'Declared ranks by country', 'table:rank-authors', rank_cols,
        lambda c: [res['ranks_authors'][c][k] for k in RANKS], [0] * 9)
    add('ranks_papers', 'Papers by rank at publication', 'table:authors-2', rank_cols,
        lambda c: [res['ranks_papers'][c][k] for k in RANKS], [0] * 9)

    # gender by rank (Table 7)
    gpaper = printed['tab:my_label']
    grows = []
    for name, ours in res['gender_by_rank'].items():
        p = [num(x) for x in gpaper[name]]
        grows.append({'group': name, 'paper_n': p[0], 'paper_pct': p[1][0], 'paper_ci': p[1][1],
                      'n': ours['n'], 'pct': ours['female_pct'], 'ci': ours['ci95']})

    # R^2 values printed in Figs. 14-19
    r2_paper = {'authors_pmi_vs_rd': 0.20, 'papers_pmi_vs_rd': 0.19, 'citations_pmi_vs_rd': 0.10,
                'authors_pmi_vs_hdi': 0.34, 'papers_pmi_vs_hdi': 0.37, 'citations_pmi_vs_hdi': 0.35}

    out = {k: res[k] for k in ['n_records', 'n_authors', 'n_papers', 'la_total_papers',
                                'gender_known', 'authors_with_rank', 'collab_la', 'collab_world',
                                'world', 'gender_by_year', 'correlations']}
    out.update({'LA': LA, 'WORLD': WORLD, 'tables': tables, 'gender_rank': grows,
                'r2_paper': r2_paper,
                'context': {c: {'pop': v[0], 'rd': v[1], 'hdi': v[2]} for c, v in CONTEXT.items()},
                'points': {c: {k: cc[c][k] for k in ['authors_pmi', 'papers_pmi', 'citations_pmi']}
                           for c in LA},
                'per_year': {c: cc[c]['papers_per_year'] for c in LA}})

    # cell-level agreement: the paper rounds most values and truncates some small ones
    summary = []
    for t in tables:
        n = ok = 0
        for r in t['rows']:
            r['status'] = []
            for p, o in zip(r['paper'], r['ours']):
                tol = 0.5 if p >= 1 else 0.05 if p >= 0.1 else 0.005
                s = ('exact' if abs(p - o) < 1e-9 else 'rounded' if abs(p - o) <= tol + 1e-9
                     else 'truncated' if p <= o < p + 2 * tol else 'differs')
                r['status'].append(s)
                n += 1
                ok += s != 'differs'
        summary.append({'key': t['key'], 'cells': n, 'match': ok})
    out['summary'] = summary
    json.dump(out, open(out_path, 'w'))
    for s in summary:
        print(f"{s['key']:15s} {s['match']}/{s['cells']}")


if __name__ == '__main__':
    if sys.argv[1] == '--dump':
        with open(sys.argv[3], 'w', encoding='utf-8') as f:
            json.dump(paper_tables(sys.argv[2]), f, ensure_ascii=False, indent=1)
    else:
        main(*sys.argv[1:4])
