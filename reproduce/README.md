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

| Script | Output |
|---|---|
| `reproduce.py` | `results.json`: per-country authors, papers, citations, h-index, ranks, gender, collaborations, world share and R² |
| `compare.py` | `page_data.json`: each table cell of Tables 5, 6, 7, 10, 11 and 12 with status exact, rounded, truncated or differs; prints matches per table |
| `export_dashboard.py` | the eight dataset files of the dashboard |
| `standalone.py` | `dashboard.html`: the whole dashboard in one self-contained file (page, data and d3 inlined; opens offline) |
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
