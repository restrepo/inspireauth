"""Write the datasets of the reproduction dashboard from compare.py's output.

Usage: python reproduce/export_dashboard.py page_data.json outdir/
"""
import json
import sys
from pathlib import Path

ISO3 = {'Argentina': 'ARG', 'Bolivia': 'BOL', 'Brazil': 'BRA', 'Chile': 'CHL', 'Colombia': 'COL',
        'Costa Rica': 'CRI', 'Cuba': 'CUB', 'Dominican Republic': 'DOM', 'Ecuador': 'ECU',
        'El Salvador': 'SLV', 'Guatemala': 'GTM', 'Honduras': 'HND', 'Mexico': 'MEX', 'Panama': 'PAN',
        'Paraguay': 'PRY', 'Peru': 'PER', 'Uruguay': 'URY', 'Venezuela': 'VEN'}
TABLE_NO = {'authors': 'Table 5', 'ranks_authors': 'Table 6', 'ranks_papers': 'Table 7',
            'publications': 'Table 10', 'citations': 'Table 11', 'hindex': 'Table 12'}


def main(page_data, outdir):
    d = json.load(open(page_data))
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    def dump(name, rows):
        json.dump(rows, open(out / f'{name}.json', 'w'), separators=(',', ':'))
        print(name, len(rows))

    cells = []
    for t in d['tables']:
        for r in t['rows']:
            for j, col in enumerate(t['cols']):
                cells.append({'id': f"{t['key']}|{r['country']}|{col}", 'table': f"{TABLE_NO[t['key']]}: {t['title']}",
                              'country': r['country'], 'column': col, 'paper': r['paper'][j],
                              'ours': round(r['ours'][j], 3), 'status': r['status'][j]})
    dump('table_cells', cells)

    c = d['correlations']
    names = {'authors_pmi': 'Authors PMI', 'papers_pmi': 'Publications PMI', 'citations_pmi': 'Citations PMI'}
    scalars = [{'id': f'r2_{k}', 'group': 'R²', 'label': f"{names[k.split('_vs_')[0]]} vs {'R&D' if k.endswith('rd') else 'HDI'}",
                'paper': v, 'ours': round(c[k]['r2'], 3)} for k, v in d['r2_paper'].items()]
    scalars += [
        {'id': 'authors', 'group': 'Dataset', 'label': 'Distinct authors', 'paper': 29969, 'ours': d['n_authors']},
        {'id': 'rank_authors', 'group': 'Dataset', 'label': 'Authors with a declared rank', 'paper': 7023,
         'ours': d['authors_with_rank']},
        {'id': 'gender_known', 'group': 'Dataset', 'label': 'Authors with gender (p ≥ 0.9, offline)', 'paper': 18000,
         'ours': d['gender_known']},
        {'id': 'papers', 'group': 'Dataset', 'label': 'Distinct papers', 'paper': None, 'ours': d['n_papers']},
        {'id': 'records', 'group': 'Dataset', 'label': 'Author–institution records', 'paper': None,
         'ours': d['n_records']},
    ]
    dump('scalars', scalars)

    metrics = []
    by = {t['key']: {r['country']: r['ours'] for r in t['rows']} for t in d['tables']}
    for k in d['LA']:
        ctx = d['context'][k]
        metrics.append({'country': k, 'code': ISO3[k], 'population': ctx['pop'], 'rd_avg': ctx['rd'],
                        'hdi_avg': ctx['hdi'], 'authors': by['authors'][k][0],
                        'papers': by['publications'][k][0], 'citations': by['citations'][k][0],
                        'h_index': by['hindex'][k][0],
                        **{m: round(v, 3) for m, v in d['points'][k].items()}})
    dump('country_metrics', metrics)

    dump('papers_per_year', [{'country': 'All Latin America', 'year': int(y), 'papers': n}
                             for y, n in d['la_papers_per_year'].items()]
         + [{'country': k, 'year': int(y), 'papers': n} for k in d['LA'] for y, n in d['per_year'][k].items()])
    dump('world_share', [{k: r[k] for k in ['year', 'la_papers', 'world_papers', 'la_citations', 'world_citations']}
                         for r in d['world']])
    collab = [{'scope': 'Latin America', 'row': a, 'col': b, 'pct': d['collab_la'][i][j]}
              for i, a in enumerate(d['LA']) for j, b in enumerate(d['LA'])]
    collab += [{'scope': 'World', 'row': a, 'col': b, 'pct': d['collab_world'][i][j]}
               for i, a in enumerate(d['LA']) for j, b in enumerate(d['WORLD'])]
    dump('collab', collab)
    dump('mobility', d['mobility'])
    dump('phd_destination', d['phd_destination'])
    dump('advisor_generations', d['advisor_generations'])
    dump('advisor_families', d['advisor_families'])
    dump('gender_year', [{'year': int(y), 'authors': v['n'], 'female_pct': round(v['female_pct'], 2),
                          'ci95': round(v['ci95'], 2)} for y, v in d['gender_by_year'].items()])
    dump('gender_rank', [{'group': g['group'], 'paper_n': g['paper_n'], 'ours_n': g['n'],
                          'paper_pct': g['paper_pct'], 'ours_pct': round(g['pct'], 1),
                          'paper_ci': g['paper_ci'], 'ours_ci': round(g['ci'], 1)} for g in d['gender_rank']])


if __name__ == '__main__':
    main(*sys.argv[1:3])
