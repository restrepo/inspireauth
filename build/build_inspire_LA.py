"""Rebuild data/inspire_LA.json from the INSPIRE-HEP API.

Follows the rules of INSPIREHEP.ipynb (inspirehep.py), students.ipynb and
gender-genderize.ipynb, which built the published file:

1. Institutions of each Latin American country: INSPIRE institution search for the
   country name, kept when the first address is in that country (as inspirehep.py,
   only for names pycountry knows: Bolivia and Venezuela are not filtered).
2. Papers of each institution with at most 10 authors (`affid:ID and ac 1->10`),
   each paper processed once, in the order countries (reversed list) → institutions → papers.
3. Every author of those papers becomes one record per affiliation (author, institution),
   with the INSPIRE profile (name, positions, e-mails, ids, advisors) and the country of
   the institution; all records of an author share the author's list of papers, one entry
   per affiliation of the author in the paper.
4. Positions get institution_id, country and author_id; a paper gets the rank, dates and
   institution of the position held at that institution in its year (students.ipynb).
5. first_names without initials; gender from genderize-offline (replacing genderize.io),
   with the country of the author's first record.

Differences from the notebooks, all fixes: requests are cached and batched; an author
without an INSPIRE BAI keeps one id per full name; a record without positions gets no
rank (students.ipynb reused the previous record's positions).

Usage: python build/build_inspire_LA.py [--cache build/cache] [--out data/inspire_LA.json.gz]
A name ending in .gz is written gzipped, byte-reproducibly (no name or time in the header).
The cache makes a stopped run resume where it was.
"""

import argparse
import copy
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

API = 'https://inspirehep.net/api'
LA_COUNTRIES = ['Brazil', 'Mexico', 'Argentina', 'Chile', 'Colombia', 'Bolivia', 'Cuba',
                'Costa Rica', 'Ecuador', 'El Salvador', 'Guatemala', 'Honduras',
                'Nicaragua', 'Panama', 'Paraguay', 'Peru',
                'Dominican Republic', 'Uruguay', 'Venezuela']
NOT_IN_PYCOUNTRY = {'Bolivia', 'Venezuela'}  # pycountry: "Bolivia, Plurinational State of", ...
LIT_FIELDS = ('control_number,citation_count,arxiv_eprints,publication_info,preprint_date,'
              'legacy_creation_date,authors.ids,authors.full_name,authors.affiliations,authors.record')
SLEEP = 0.35  # INSPIRE allows 15 requests per 5 s
MAX_WINDOW = 9500  # INSPIRE pages at most 10,000 results of one query


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def get(url, tries=8):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'Accept': 'application/json'}),
                                        timeout=120) as r:
                out = json.load(r)
            time.sleep(SLEEP)
            return out
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ConnectionError) as e:
            wait = 60 if getattr(e, 'code', None) == 429 else 5 * (k + 1)
            log(f'retry {k + 1} in {wait}s: {e} {url[:120]}')
            time.sleep(wait)
    raise RuntimeError(f'failed: {url}')


def search(kind, q, fields=None, size=250):
    """All hits of an INSPIRE search, following `links.next`."""
    url = f'{API}/{kind}?size={size}&page=1&q={urllib.parse.quote(q)}'
    if fields:
        url += f'&fields={fields}'
    hits = []
    while url:
        d = get(url)
        hits += d['hits']['hits']
        url = d.get('links', {}).get('next')
    return hits, d['hits']['total']


def cached(path, fn):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    out = fn()
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out), encoding='utf-8')
    tmp.replace(path)
    return out


def ref_id(obj):
    try:
        return obj['record']['$ref'].split('/')[-1]
    except (KeyError, TypeError, AttributeError):
        return None


# ---------------------------------------------------------------- downloads

def institutions_of(country, cache):
    def fetch():
        hits, _ = search('institutions', country, 'control_number,legacy_ICN,addresses')
        out = []
        for h in hits:
            m = h['metadata']
            try:
                c = m['addresses'][0]['country']
            except (KeyError, IndexError, TypeError):
                c = ''
            if country in NOT_IN_PYCOUNTRY or c == country:
                out.append(m['control_number'])
        return out
    return cached(cache / f'institutions_{country}.json', fetch)


def papers_of(iid, cache):
    def fetch():
        q = f'affid:{iid} and ac 1->10'
        d = get(f'{API}/literature?size=1&q={urllib.parse.quote(q)}&fields=control_number')
        total = d['hits']['total']
        if total <= MAX_WINDOW:
            return [h['metadata'] for h in search('literature', q, LIT_FIELDS)[0]]
        out, seen = [], set()  # too many for one query: split by year
        for a, b in [(0, 1990), *((y, y + 1) for y in range(1991, datetime.now().year + 2, 2))]:
            for h in search('literature', f'{q} and date {a}->{b}', LIT_FIELDS)[0]:
                if h['metadata']['control_number'] not in seen:
                    seen.add(h['metadata']['control_number'])
                    out.append(h['metadata'])
        return out
    return cached(cache / 'literature' / f'{iid}.json', fetch)


def batch_records(kind, ids, fields, cache_file):
    """{control_number: metadata} for many ids, 100 per request, cached as JSON lines."""
    have = {}
    if cache_file.exists():
        for line in cache_file.open(encoding='utf-8'):
            m = json.loads(line)
            have[str(m['control_number'])] = m
    todo = sorted(set(map(str, ids)) - have.keys() - {'None'})
    log(f'{kind}: {len(have)} cached, {len(todo)} to fetch')
    with cache_file.open('a', encoding='utf-8') as f:
        for i in range(0, len(todo), 100):
            chunk = todo[i:i + 100]
            hits, _ = search(kind, 'control_number:(' + ' OR '.join(chunk) + ')', fields)
            for h in hits:
                m = h['metadata']
                have[str(m['control_number'])] = m
                f.write(json.dumps(m) + '\n')
            for c in set(chunk) - {str(h['metadata']['control_number']) for h in hits}:
                have[c] = {'control_number': c, 'missing': True}
                f.write(json.dumps(have[c]) + '\n')
            if i // 100 % 20 == 0:
                log(f'{kind}: {min(i + 100, len(todo))}/{len(todo)}')
    return have


# ---------------------------------------------------------------- assembly

def paper_entry(w):
    cats = []
    try:
        cats = w['arxiv_eprints'][0]['categories']
    except (KeyError, IndexError, TypeError):
        pass
    try:
        journal_id = w['publication_info'][0]['journal_record']['$ref'].split('/')[-1]
    except (KeyError, IndexError, TypeError):
        journal_id = 'None'
    try:
        year = str(w['publication_info'][0].get('year'))
    except (KeyError, IndexError, TypeError):
        year = 0
    if not year:
        try:
            year = w['preprint_date'].split('-')[0]
        except (KeyError, AttributeError):
            year = 0
    if not year:
        try:
            year = w['legacy_creation_date'].split('-')[0]
        except (KeyError, AttributeError):
            year = 0
    if not year:
        year = '0000'
    return {'recid': w['control_number'], 'year': year, 'citation_count': w.get('citation_count'),
            'primary_arxiv_category': cats, 'journal_id': journal_id}


def bai(ids):
    for i in ids or []:
        if i.get('schema') == 'INSPIRE BAI':
            return i.get('value')
    return None


def remove_initials(d):
    """first_names as in gender-genderize.ipynb."""
    if d.get('name') and d['name'].get('value'):
        x = d['name']['value'].split(', ')[-1].replace('-', ' ').strip()
    elif d.get('full_name'):
        x = d['full_name'].split(', ')[-1].replace('-', ' ').strip()
    else:
        x = ''
    x = re.sub(r'[\|†•]', '', x).strip()
    x = re.sub(r'\.', ' ', x).strip()
    x = re.sub(r'\s\w\s', '', x).strip()
    x = re.sub(r'^\w\s', '', x).strip()
    x = re.sub(r'\s\w$', '', x).strip()
    x = re.sub(r'^\w$', '', x).strip()
    return re.sub(r'^[A-Z]{2}$', '', x)


def assemble(works, profiles, inst_country):
    records = []            # in creation order
    by_key = {}             # (author_key, institution_id) -> record
    by_author = {}          # author_key -> [records]
    papers_of_author = {}   # author_key -> shared list
    for w in works:
        paper = paper_entry(w)
        for a in w.get('authors') or []:
            pid = ref_id(a)
            prof = profiles.get(pid, {}) if pid else {}
            if prof.get('missing'):
                prof = {}
            aid = bai(a.get('ids')) or bai(prof.get('ids'))
            key = aid or 'unknown:' + (a.get('full_name') or '')
            paper['author_id'] = aid
            iids = []
            for aff in a.get('affiliations') or []:
                if not aff.get('value'):
                    continue
                iid = ref_id(aff)
                if iid:
                    iids.append(iid)
                if (key, iid) in by_key:
                    continue
                r = {'author_id': aid, 'full_name': a.get('full_name'), 'institution': aff['value'],
                     'institution_id': iid, 'country': inst_country.get(iid) if iid else None,
                     'name': prof.get('name'), 'positions': copy.deepcopy(prof.get('positions')),
                     'email_addresses': prof.get('email_addresses'), 'ids': prof.get('ids'),
                     'advisors': prof.get('advisors') or []}
                if pid:
                    r['profile_id'] = pid
                r['_key'] = key
                by_key[key, iid] = r
                by_author.setdefault(key, []).append(r)
                records.append(r)
            if key not in by_author:
                continue  # an author never seen with an affiliation gets no record
            plist = papers_of_author.setdefault(key, [])
            for iid in iids or [None]:
                e = dict(paper, institution_id=iid)
                if e not in plist:
                    plist.append(e)
    for key, rs in by_author.items():
        for r in rs:
            r['papers'] = papers_of_author.get(key, [])
    # authors without a BAI: unknown00, unknown01, ... one per full name
    unknown = {}
    for r in records:
        if r['author_id'] is None:
            r['author_id'] = unknown.setdefault(r['_key'], f'unknown{len(unknown):02d}')
    return records


def extend_ranks(records):
    """students.ipynb: positions get institution_id, country, author_id; papers get the rank held."""
    country_of = {}
    for r in records:
        country_of.setdefault(r['institution_id'], r['country'])
    now = datetime.now().year
    for r in records:
        for p in r.get('positions') or []:
            p['institution_id'] = ref_id(p)
            p['country'] = country_of.get(p['institution_id']) if p['institution_id'] else None
            p['author_id'] = r['author_id']
    done = set()
    for r in records:
        if id(r['papers']) in done:  # papers are shared by the author's records
            continue
        done.add(id(r['papers']))
        dp = [dict(p, institution_id=ref_id(p)) for p in r.get('positions') or []]
        il = [p['institution_id'] for p in dp]
        for pr in r['papers']:
            if pr.get('institution_id') not in il:
                continue
            end_date = None
            for p in [p for p in dp if p['institution_id'] == pr['institution_id']]:
                if p.get('end_date'):
                    end_date = int(p['end_date'].split('-')[0])
                elif p.get('current'):
                    end_date = now + 1
                start = int(p['start_date'].split('-')[0]) if p.get('start_date') else None
                year = int(pr['year']) if str(pr['year']).isdigit() else None
                if year and start and end_date and start <= year < end_date + 2:
                    pr['rank'] = p.get('rank')
                    pr['start_date'] = p.get('start_date')
                    pr['end_date'] = p.get('end_date')
                    if p.get('current'):
                        pr['current'] = p.get('current')
                    pr['institution'] = p.get('institution')
                    pr['country'] = country_of.get(p['institution_id'])


def add_gender(records):
    from genderize_offline import guess
    # one first_names and gender per author, from the author's first record
    first = {}
    for r in records:
        first.setdefault(r['author_id'], r)
    names = {k: remove_initials(r) for k, r in first.items()}
    res = {k: guess(names[k], r.get('country') or '') for k, r in first.items()}
    for r in records:
        g, p, _ = res[r['author_id']]
        r['first_names'], r['gender'], r['gender_probability'] = names[r['author_id']], g, p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cache', default=str(Path(__file__).resolve().parent / 'cache'))
    ap.add_argument('--out', default=str(Path(__file__).resolve().parent.parent / 'data/inspire_LA.json.gz'))
    ap.add_argument('--countries', nargs='*', default=LA_COUNTRIES, help='for a test run')
    a = ap.parse_args(argv)
    cache = Path(a.cache)
    (cache / 'literature').mkdir(parents=True, exist_ok=True)

    works, seen = [], set()
    for c in [x for x in LA_COUNTRIES[::-1] if x in a.countries]:
        insts = institutions_of(c, cache)
        log(f'{c}: {len(insts)} institutions')
        for iid in insts:
            for w in papers_of(iid, cache):
                if w['control_number'] not in seen:
                    seen.add(w['control_number'])
                    works.append(w)
        log(f'{c}: {len(works)} papers so far')

    pids = {ref_id(au) for w in works for au in w.get('authors') or []} - {None}
    profiles = batch_records('authors', pids, 'control_number,name,positions,email_addresses,ids,advisors',
                             cache / 'profiles.jsonl')
    iids = {ref_id(aff) for w in works for au in w.get('authors') or [] for aff in au.get('affiliations') or []}
    insts = batch_records('institutions', iids - {None}, 'control_number,addresses', cache / 'institutions.jsonl')
    inst_country = {}
    for k, m in insts.items():
        try:
            inst_country[k] = m['addresses'][0]['country']
        except (KeyError, IndexError, TypeError):
            inst_country[k] = None

    records = assemble(works, profiles, inst_country)
    extend_ranks(records)
    add_gender(records)
    keys = ['author_id', 'country', 'email_addresses', 'full_name', 'ids', 'institution', 'institution_id',
            'name', 'papers', 'positions', 'profile_id', 'advisors', 'gender', 'first_names', 'gender_probability']
    out = [{k: r[k] for k in keys if k in r} for r in records]
    if a.out.endswith('.gz'):
        with open(a.out, 'wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=9, mtime=0) as gz:
            gz.write(json.dumps(out).encode('utf-8'))
    else:
        with open(a.out, 'w', encoding='utf-8') as f:
            json.dump(out, f)
    log(f'wrote {a.out}: {len(out)} records, {len({r["author_id"] for r in out})} authors, '
        f'{len({p["recid"] for r in out for p in r["papers"]})} papers')
    return 0


if __name__ == '__main__':
    sys.exit(main())
