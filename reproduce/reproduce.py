"""Recompute the tables and figures of the JDIS manuscript from data/inspire_LA.json.

The counting rules follow the notebooks in INSPIREHEP_new_nbs/:
- a country's papers are the papers of its author records whose
  `institution_id` is one of the country's institutions, deduplicated by recid;
- authors are the distinct `author_id` of the country's records;
- an author is active with one of those papers from --year minus 5 or later (2017 for the paper);
- genders come from genderize-offline (pip install genderize-offline), or with
  --genderize-io from the genderize.io fields stored in the dataset.

Usage: python reproduce/reproduce.py [data/inspire_LA.json.gz] [results.json] [--genderize-io] [--year 2022]
--year: the year the data end (2022 for the paper's data, 2026 for the 2026 rebuild)
(a plain .json, such as the paper's version, works too)
"""
import csv
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

LA = ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Costa Rica',
      'Cuba', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Guatemala',
      'Honduras', 'Mexico', 'Panama', 'Paraguay', 'Peru', 'Uruguay',
      'Venezuela']
WORLD = ['Spain', 'Portugal', 'Germany', 'Italy', 'France', 'United Kingdom',
         'Russian Federation', 'Belgium', 'Canada', 'United States']
RANKS = ['SENIOR', 'JUNIOR', 'STAFF', 'POSTDOC', 'PHD', 'MASTER',
         'UNDERGRADUATE', 'VISITOR', 'OTHER']
CURRENT_YEAR = 2022

# Table 1 of the manuscript: population, R&D (% of GDP, average) and HDI (average)
CONTEXT = {
    'Argentina': (45606000, 0.49, 0.802), 'Bolivia': (11833000, 0.28, 0.640),
    'Brazil': (213993000, 1.12, 0.698), 'Chile': (19212000, 0.35, 0.790),
    'Colombia': (51266000, 0.22, 0.701), 'Costa Rica': (5139000, 0.40, 0.742),
    'Cuba': (11318000, 0.47, 0.728), 'Dominican Republic': (10954000, None, 0.679),
    'Ecuador': (17888000, 0.20, 0.711), 'El Salvador': (6518000, 0.11, 0.623),
    'Guatemala': (18250000, 0.04, 0.576), 'Honduras': (10063000, 0.04, 0.572),
    'Mexico': (130262000, 0.36, 0.728), 'Panama': (4382000, 0.20, 0.751),
    'Paraguay': (7220000, 0.09, 0.681), 'Peru': (33359000, 0.11, 0.699),
    'Uruguay': (3485000, 0.34, 0.768), 'Venezuela': (28705000, 0.29, 0.719),
}


def h_index(citations):
    return sum(c >= i + 1 for i, c in enumerate(sorted(citations, reverse=True)))


def year_of(paper):
    y = str(paper.get('year') or '')
    return int(y) if y.isdigit() else None


def country_papers(records, country):
    """Papers of `country` as in calculate_papers() of the notebooks."""
    recs = [r for r in records if r.get('country') == country]
    insts = {r.get('institution_id') for r in recs}
    papers = {}
    for r in recs:
        for p in r.get('papers') or []:
            if p.get('institution_id') in insts and p['recid'] not in papers:
                papers[p['recid']] = p
    return recs, insts, papers


def linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    icpt = my - slope * mx
    ss_res = sum((y - (icpt + slope * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return {'slope': slope, 'intercept': icpt, 'r2': 1 - ss_res / ss_tot, 'n': n}


def main(data_path, out_path, gender_source='offline', year=None):
    global CURRENT_YEAR
    CURRENT_YEAR = year or CURRENT_YEAR
    opener = gzip.open if str(data_path).endswith('.gz') else open
    with opener(data_path, 'rt', encoding='utf-8') as f:
        records = json.load(f)
    out = {'source': str(data_path), 'gender_source': gender_source, 'current_year': CURRENT_YEAR, 'n_records': len(records),
           'n_authors': len({r['author_id'] for r in records}),
           'n_papers': len({p['recid'] for r in records for p in r.get('papers') or []})}

    per_country, cpapers = {}, {}
    for c in WORLD + LA:
        recs, insts, papers = country_papers(records, c)
        cpapers[c] = papers
        if c not in LA:
            continue
        pop = CONTEXT[c][0] / 1e6
        by_author = defaultdict(list)
        for r in recs:
            by_author[r['author_id']].extend(
                p for p in r.get('papers') or [] if p.get('institution_id') in insts)
        active = sum(
            1 for ps in by_author.values()
            if any(year_of(p) is not None and CURRENT_YEAR - year_of(p) <= 5 for p in ps))
        # only the first record of each author counts in the notebooks
        first = {}
        for r in recs:
            first.setdefault(r['author_id'], r)
        active_nb = sum(
            1 for r in first.values()
            if (lambda ys: ys and CURRENT_YEAR - max(ys) <= 5)(
                [year_of(p) for p in r.get('papers') or []
                 if p.get('institution_id') in insts and year_of(p) is not None]))
        cits = [p.get('citation_count') or 0 for p in papers.values()]
        n_auth = len(by_author)
        years = Counter(year_of(p) for p in papers.values() if year_of(p))
        per_country[c] = {
            'authors': n_auth, 'active_authors': active_nb,
            'active_authors_any_record': active,
            'authors_pmi': n_auth / pop, 'active_pmi': active_nb / pop,
            'papers': len(papers), 'papers_pmi': len(papers) / pop,
            'papers_per_author': len(papers) / n_auth,
            'citations': sum(cits), 'citations_pmi': sum(cits) / pop,
            'citations_per_author': sum(cits) / n_auth,
            'h_index': h_index(cits), 'h_pmi': h_index(cits) / pop,
            'h_per_author': h_index(cits) / n_auth,
            'papers_per_year': {y: years[y] for y in sorted(years) if y < CURRENT_YEAR},
        }
    out['countries'] = per_country

    # collaboration matrices: % of the papers of row country shared with column country
    def share(a, b):
        return 100 * len(cpapers[a].keys() & cpapers[b].keys()) / len(cpapers[a]) if cpapers[a] else 0
    out['collab_la'] = [[round(share(a, b), 1) for b in LA] for a in LA]
    out['collab_world'] = [[round(share(a, b), 1) for b in WORLD] for a in LA]

    # Latin America as a whole and its share of the global output
    la_all = {}
    for c in LA:
        la_all.update(cpapers[c])
    la_year_p, la_year_c = Counter(), Counter()
    for p in la_all.values():
        y = year_of(p)
        if y:
            la_year_p[y] += 1
            la_year_c[y] += p.get('citation_count') or 0
    world = {int(r['year']): r for r in csv.DictReader(open(ROOT / 'INSPIREHEP_new_nbs/world_papers.csv'))
             if r['year'].isdigit()}
    out['world'] = [{'year': y, 'la_papers': la_year_p[y], 'la_citations': la_year_c[y],
                     'world_papers': int(world[y]['Citable papers']),
                     'world_citations': int(world[y]['Citations']),
                     'pct_papers': 100 * la_year_p[y] / int(world[y]['Citable papers']),
                     'pct_citations': 100 * la_year_c[y] / int(world[y]['Citations'])}
                    for y in sorted(world) if 1946 <= y <= 2021]
    out['la_total_papers'] = len(la_all)

    # correlations with R&D (average % of GDP) and HDI
    corr = {}
    for metric in ['authors_pmi', 'papers_pmi', 'citations_pmi']:
        for xname, xi in [('rd', 1), ('hdi', 2)]:
            pts = [(CONTEXT[c][xi], per_country[c][metric]) for c in LA if CONTEXT[c][xi] is not None]
            corr[f'{metric}_vs_{xname}'] = linfit(*zip(*pts))
    out['correlations'] = corr

    # ranks: distinct declared positions per author (Table 5), and distinct
    # (paper, author, position) triples of papers published under a rank (Table 6)
    rank_auth = {c: {k: set() for k in RANKS} for c in LA}
    rank_pap = {c: {k: set() for k in RANKS} for c in LA}
    for r in records:
        for pos in r.get('positions') or []:
            if pos.get('country') in rank_auth and pos.get('rank') in RANKS:
                key = json.dumps({k: v for k, v in pos.items() if k != 'author_id'}, sort_keys=True)
                rank_auth[pos['country']][pos['rank']].add((r['author_id'], key))
        for p in r.get('papers') or []:
            if p.get('country') in rank_pap and p.get('rank') in RANKS:
                rank_pap[p['country']][p['rank']].add(
                    (p['recid'], r['author_id'], p.get('institution'), p.get('start_date')))
    out['ranks_authors'] = {c: {k: len(v) for k, v in d.items()} for c, d in rank_auth.items()}
    out['ranks_papers'] = {c: {k: len(v) for k, v in d.items()} for c, d in rank_pap.items()}
    out['authors_with_rank'] = len({r['author_id'] for r in records
                                    if any(p.get('rank') for p in r.get('positions') or [])})

    # gender: unique authors per year with probability >= 0.9, inferred offline with
    # genderize-offline (WGND 2.0) from the first record of each author, or the
    # genderize.io fields stored in the dataset
    gender = {}
    if gender_source == 'offline':
        from genderize_offline import guess
        first = {}
        for r in records:
            first.setdefault(r['author_id'], r)
        for k, r in first.items():
            g, p, _ = guess(r.get('first_names', ''), r.get('country', ''))
            if g != 'unknown' and p >= 0.9:
                gender[k] = g
    else:
        for r in records:
            if r.get('gender') in ('male', 'female') and (r.get('gender_probability') or 0) >= 0.9:
                gender[r['author_id']] = r['gender']
    out['gender_known'] = len(gender)
    by_year = defaultdict(dict)
    rank_group = defaultdict(dict)
    groups = {'Undergraduate, Master, PhD': {'UNDERGRADUATE', 'MASTER', 'PHD'},
              'Postdoc': {'POSTDOC'}, 'Junior or Staff': {'JUNIOR', 'STAFF'},
              'Senior': {'SENIOR'}}
    for r in records:
        g = gender.get(r['author_id'])
        if not g:
            continue
        years = {year_of(p) for p in r.get('papers') or []} - {None}
        for y in years:
            by_year[y][r['author_id']] = g
        # Table 7: a declared rank held in a year in which the author published
        for pos in r.get('positions') or []:
            try:
                start = int(str(pos['start_date'])[:4])
                end = int(str(pos['end_date'])[:4]) if pos.get('end_date') else (
                    CURRENT_YEAR if pos.get('current') else start)
            except (KeyError, ValueError):
                continue
            if not pos.get('rank') or not any(start <= y <= end for y in years):
                continue
            rank_group['All ranks'][r['author_id']] = g
            for name, ks in groups.items():
                if pos['rank'] in ks:
                    rank_group[name][r['author_id']] = g

    def frac(d):
        n = len(d)
        f = sum(1 for g in d.values() if g == 'female') / n if n else 0
        return {'n': n, 'female_pct': 100 * f, 'ci95': 100 * 1.96 * math.sqrt(f * (1 - f) / n) if n else 0}
    out['gender_by_year'] = {y: frac(by_year[y]) for y in sorted(by_year) if 1970 <= y <= CURRENT_YEAR}
    out['gender_by_rank'] = {k: frac(rank_group[k]) for k in ['All ranks', *groups]}

    json.dump(out, open(out_path, 'w'), indent=1)
    print(f'wrote {out_path}')


if __name__ == '__main__':
    argv = sys.argv[1:]
    year = None
    if '--year' in argv:  # the year the data end: active authors, last full year of the per-year counts
        i = argv.index('--year')
        year = int(argv[i + 1])
        del argv[i:i + 2]
    args = [a for a in argv if a != '--genderize-io']
    data = args[0] if args else ROOT / 'data/inspire_LA.json.gz'
    res = args[1] if len(args) > 1 else HERE / 'results.json'
    main(data, res, 'genderize.io' if '--genderize-io' in argv else 'offline', year)
