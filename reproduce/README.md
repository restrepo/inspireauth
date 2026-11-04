# Reproducing the manuscript

These scripts recompute the tables and figures of the JDIS manuscript
("High-energy physics in Latin America", `jdis-version.tex`) from
`data/inspire_LA.json.gz` and compare them cell by cell with the printed values.
They use the Python standard library and genderize-offline.

```bash
# the paper's data: git show v1.0.1:data/inspire_LA.json (Git LFS) or Zenodo; the current file is a later rebuild
pip install -r reproduce/requirements.txt      # genderize-offline, from PyPI
python reproduce/reproduce.py data/inspire_LA.json.gz results.json
python reproduce/compare.py ../jdis-version.tex results.json page_data.json
python reproduce/export_dashboard.py page_data.json dash/
python reproduce/standalone.py dash/ reproduce/dashboard.html
```

The paper's board (`dashboard.html`) is built from the paper's data (tag `v1.0.1`, `--year 2022`, the default).
The board of the 2026 rebuild, [`dashboard_2026.html`](dashboard_2026.html), compares the same tables with the
paper after four more years of data:

```bash
python reproduce/reproduce.py data/inspire_LA.json.gz results.json --year 2026
python reproduce/compare.py ../jdis-version.tex results.json page_data.json
python reproduce/export_dashboard.py page_data.json dash/
python reproduce/standalone.py dash/ reproduce/dashboard_2026.html --edits reproduce/dashboard/edits_2026.json
```

| Script | Output |
|---|---|
| `reproduce.py` | `results.json`: per-country authors, papers, citations, h-index, ranks, gender, collaborations, world share and R² |
| `compare.py` | `page_data.json`: each table cell of Tables 5, 6, 7, 10, 11 and 12 with status exact, rounded, truncated or differs; prints matches per table |
| `export_dashboard.py` | the ten dataset files of the dashboard |
| `standalone.py` | `dashboard.html` / `dashboard_2026.html`: the whole dashboard in one self-contained file (page, data and d3 inlined; opens offline); `--edits` adapts the wording |
| `pages_index.py` | the GitHub Pages index of every board (`add`, `render`) |
| `store_docs.py` | the dashboard's store documents, from `dashboard/blobs.json` (uploaded blob ids) |

[`dashboard.html`](dashboard.html) is the dashboard as one file: download it and open it in a browser.
`dashboard/index.html` is its page in the online dashboard
(<https://claude.ai/artifact/68auWa5zrhfda8bjZ6yS3w>).

## Counting rules

- A country's papers are the papers of its records whose `institution_id` is one of the
  country's institutions, deduplicated by recid.
- Authors are the distinct `author_id` of the country's records; an author is active if
  the first record has such a paper from 2017 or later.
- Table 6 counts distinct (author, position); Table 7 counts distinct
  (recid, author, institution, start date) of papers published under a rank.
- Table 8 takes a position whose years cover a year in which the author published,
  and gender probability ≥ 0.9. Genders come from [genderize-offline](https://pypi.org/project/genderize-offline/) 0.1.0 (World Gender Name Dictionary 2.0); `--genderize-io` uses the genderize.io fields stored in the dataset instead. These agree with
  genderize.io for 99.6% of the authors both assign, and Table 8 and Fig. 21 move by less
  than their 95% margins.

Not recomputed: Tables 3–4 (INSPIRE web queries, read from
`INSPIREHEP_new_nbs/world_papers.csv`), the OpenAlex section and the rank-mobility figures.

## Automatic updates and GitHub Pages

Publishing a release whose tag starts with `v` (v2.0.0, …) runs the workflow
[`update-data.yml`](../.github/workflows/update-data.yml) (about an hour):

1. it downloads the data again from INSPIRE-HEP (`build/build_inspire_LA.py`);
2. it recomputes the paper's tables with `--year` set to the current year and compares them with the
   printed values, read from [`paper/tables.json`](paper/tables.json) (extracted from the manuscript with
   `compare.py --dump`, so the workflow doesn't need it);
3. it makes the board (`standalone.py --edits dashboard/edits_update.json --set YEAR=… --set DATE=…`);
4. it attaches `inspire_LA.json.gz` and the board to the release, opens a pull request that puts them
   on `main`, and adds the board to GitHub Pages.

The Pages site, branch `gh-pages`, keeps every board in `boards/<date>/` and lists them in its
`index.html` (`pages_index.py`), the paper's board included: <https://restrepo.github.io/inspireauth/>.
The workflow can also run by hand (Actions → Update data and boards → Run workflow, with *publish*
off for a dry run); pull requests that change `build/` or `reproduce/` run it on two small countries
without publishing anything.
