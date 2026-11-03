"""Offline gender inference from first names, a drop-in for genderize.io.

Uses the World Gender Name Dictionary 2.0 (WGND, Raffo 2021, CC0,
doi:10.7910/DVN/MSEGSJ): for each (name, country) the share of women and men.
A name is looked up in the author's country first and, if absent there, in the
average over every country that lists it. Of the given names, the first one
found decides, as genderize.io does with the first word.

Output per name, like genderize.io: gender (male, female, unknown),
probability (0.5-1, 0 for unknown) and count (countries listing the name).

Usage:
  offline_gender.py fetch                      download WGND into the cache
  offline_gender.py name "Natalia Andrea" [CO]
  offline_gender.py csv in.csv out.csv [--name-col names] [--country-col country_id]
  offline_gender.py inspire inspire_LA.json out.json   rewrite gender fields
"""
import argparse
import csv
import json
import os
import pickle
import re
import sys
import unicodedata
import urllib.request
from collections import defaultdict
from pathlib import Path

CACHE = Path(os.environ.get('OFFLINE_GENDER_CACHE', Path.home() / '.cache/offline-gender'))
WGND = CACHE / 'wgnd_2_0_name-gender-code.csv'
WGND_URL = 'https://dataverse.harvard.edu/api/access/datafile/4750348?format=original'
INDEX = CACHE / 'wgnd_index.pkl'
HERE = Path(__file__).resolve().parent
ISO2 = json.load(open(HERE / 'country_iso2.json'))


def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)
    if not WGND.exists():
        print(f'downloading WGND 2.0 (91 MB) to {WGND}')
        urllib.request.urlretrieve(WGND_URL, WGND)
    build_index()


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def build_index():
    """{name: {country: p_female}} plus the world average under '' (and accent-free keys)."""
    raw = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    with open(WGND, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            g = r['gender']
            if g not in ('F', 'M'):
                continue
            raw[r['name'].strip().lower()][r['code']][g == 'M'] += float(r['wgt'] or 0)
    index = {}
    for name, by in raw.items():
        d = {c: fm[0] / (fm[0] + fm[1]) for c, fm in by.items() if fm[0] + fm[1] > 0}
        if d:
            d[''] = sum(d.values()) / len(d)
            index[name] = d
    for name in list(index):
        index.setdefault(strip_accents(name), index[name])
    pickle.dump(index, open(INDEX, 'wb'))
    print(f'indexed {len(index)} names')
    return index


_index = None


def load():
    global _index
    if _index is None:
        if not INDEX.exists():
            fetch()
        _index = pickle.load(open(INDEX, 'rb'))
    return _index


def tokens(names):
    names = re.sub(r'[|†•()"]', ' ', names or '').replace('-', ' ').replace('.', ' ')
    return [t.lower() for t in names.split() if len(t) > 1]


def guess(names, country=''):
    """(gender, probability, count) for the given names and ISO2 country (or country name)."""
    idx = load()
    code = ISO2.get(country, country) if country else ''
    for t in tokens(names):
        d = idx.get(t) or idx.get(strip_accents(t))
        if not d:
            continue
        pf = d.get(code, d[''])
        n = len(d) - 1
        if pf == 0.5:
            return 'unknown', 0.0, n
        return ('female', round(pf, 2), n) if pf > 0.5 else ('male', round(1 - pf, 2), n)
    return 'unknown', 0.0, 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('fetch')
    p = sub.add_parser('name')
    p.add_argument('names')
    p.add_argument('country', nargs='?', default='')
    p = sub.add_parser('csv')
    p.add_argument('src')
    p.add_argument('dst')
    p.add_argument('--name-col', default='names')
    p.add_argument('--country-col', default='country_id')
    p = sub.add_parser('inspire')
    p.add_argument('src')
    p.add_argument('dst')
    a = ap.parse_args()

    if a.cmd == 'fetch':
        fetch()
    elif a.cmd == 'name':
        print(json.dumps(dict(zip(['gender', 'probability', 'count'], guess(a.names, a.country)))))
    elif a.cmd == 'csv':
        rows = list(csv.DictReader(open(a.src, newline='', encoding='utf-8')))
        cols = list(rows[0]) + ['og_gender', 'og_probability', 'og_count']
        with open(a.dst, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, cols)
            w.writeheader()
            for r in rows:
                r['og_gender'], r['og_probability'], r['og_count'] = guess(r[a.name_col], r.get(a.country_col, ''))
                w.writerow(r)
    elif a.cmd == 'inspire':
        records = json.load(open(a.src))
        # one gender per author, from the country of the author's first record, as in gender-genderize.ipynb
        first = {}
        for r in records:
            first.setdefault(r.get('author_id'), r)
        res = {k: guess(r.get('first_names', ''), r.get('country', '')) for k, r in first.items()}
        for r in records:
            r['gender'], r['gender_probability'], _ = res[r.get('author_id')]
        json.dump(records, open(a.dst, 'w'))
        print(f'wrote {a.dst}: {len(res)} authors')


if __name__ == '__main__':
    sys.exit(main())
