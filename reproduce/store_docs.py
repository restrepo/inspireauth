"""Write the store documents of the reproduction dashboard.

Each dataset gets a `datasets/<name>` document pointing at its uploaded blob,
and the page gets `files/index.html`. The documents are written to outdir as
<name>.json, ready for one ArtifactData batch.

Usage: python reproduce/store_docs.py reproduce/dashboard/blobs.json outdir/
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

DATASETS = {
    'table_cells': ('Table cells, paper vs recomputed',
                    'Each cell of Tables 5, 6, 7, 10, 11 and 12 of the manuscript with its printed value, '
                    'the value recomputed from inspire_LA.json and whether they agree.'),
    'scalars': ('Dataset totals and R²',
                'Totals quoted in the paper and the R² printed in Figs. 15–20, each beside the recomputed value.'),
    'country_metrics': ('Country metrics and context',
                        'Per country: population, R&D and HDI from Table 1, and the recomputed authors, papers, '
                        'citations and h-index.'),
    'papers_per_year': ('Articles per year by country',
                        'Recomputed number of articles of each country, and of Latin America as a whole, by publication year.'),
    'world_share': ('Latin America vs global output',
                    'Latin American papers and citations per year, recomputed, beside the global output of '
                    'Tables 3–4 (INSPIRE-HEP, February 2024).'),
    'collab': ('Collaboration matrices',
               "Share of a country's articles co-authored with another country, recomputed for Figs. 22 and 23."),
    'gender_year': ('Female fraction per year',
                    'Recomputed female fraction of the authors who published each year, with its 95% margin; '
                    'genders inferred offline with the World Gender Name Dictionary 2.0.'),
    'mobility': ('Ranks and where they published',
                 'Figs. 4 and 37-39: authors with a declared rank in a country, by the rank and region under '
                 'which they published (recomputed).'),
    'phd_destination': ('Where Latin American PhDs go',
                        'Not in the paper: current or latest later position of the authors who held a PhD '
                        'position in a Latin American country.'),
    'gender_rank': ('Female fraction by rank',
                    'Table 8 of the paper (genderize.io) beside the recomputed counts and female fractions '
                    '(offline genders, World Gender Name Dictionary 2.0).'),
}


def main(blobs_path, outdir, by='reproduce.py on data/inspire_LA.json, genders from genderize-offline 0.1.0'):
    blobs = json.load(open(blobs_path))
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for name, (title, desc) in DATASETS.items():
        doc = {'title': title, 'description': desc,
               'source': {'kind': 'file', 'url': blobs[name], 'name': f'{name}.json'},
               'updated': {'at': now, 'by': by}, 'fixed': True, 'edit': {'via': 'claude', 'at': now}}
        json.dump(doc, open(out / f'{name}.json', 'w'), ensure_ascii=False)
    page = (HERE / 'dashboard/index.html').read_text()
    json.dump({'text': page, 'edit': {'via': 'claude', 'at': now}}, open(out / 'index.json', 'w'))
    print(f'wrote {len(DATASETS) + 1} documents to {out}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
