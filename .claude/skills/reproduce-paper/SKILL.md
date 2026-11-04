---
name: reproduce-paper
description: Reproduce the tables and figures of "Statistical Analysis of Scientific Metrics in High Energy, Cosmology, and Astroparticle Physics in Latin America" (JDIS) from this repository's INSPIRE-HEP data, build the self-contained HTML boards (reproduce/dashboard.html, reproduce/dashboard_YYYY.html), and add new indicators, charts or tabs to them. Use whenever someone working in a clone of restrepo/inspireauth asks to rerun or check the paper's numbers, open or change a board, add an indicator (for example where PhDs go, citations by field, female share by country), or answer a question from data/inspire_LA.json.gz.
---

# Reproduce the paper and extend its boards

Everything runs from the repository root with Python ≥ 3.10:

```bash
pip install -r reproduce/requirements.txt     # only dependency: genderize-offline
```

## The data

- **`data/inspire_LA.json.gz`:** the latest INSPIRE-HEP download, a gzipped list of records (one per
  author and institution). The fields are documented in `README.md`. Read it with
  `gzip.open(path, 'rt')` + `json.load`.
- **The paper's data (up to 2022):** download it once; there's no need for Git LFS.

  ```bash
  curl -L -o data/inspire_LA_paper.json https://media.githubusercontent.com/media/restrepo/inspireauth/v1.0.1/data/inspire_LA.json
  ```

  Its sha256 begins with `f9a3b1ce`. Don't commit it.
- **The paper's printed tables:** they are in `reproduce/paper/tables.json`, so the manuscript isn't
  needed.

## Reproduce the paper

```bash
mkdir -p out
python reproduce/reproduce.py data/inspire_LA_paper.json out/results.json        # --year 2022 is the default
python reproduce/compare.py reproduce/paper/tables.json out/results.json out/page_data.json
python reproduce/export_dashboard.py out/page_data.json out/dash/
python reproduce/standalone.py out/dash/ out/dashboard.html
```

`compare.py` prints the agreement per table. Expected results:
- authors 71/72, publications, citations and h-index 54/54, ranks 162/162 and 161/162;
- the two known differences: Costa Rica active authors (10 vs 12) and Paraguay Senior papers (0 vs 1).

`out/dashboard.html` opens in any browser, offline. For the latest data, run
`reproduce.py data/inspire_LA.json.gz … --year <year of the download>`, and then use
`standalone.py … --edits reproduce/dashboard/edits_update.json --set YEAR=… --set DATE=… --set ACTIVE_FROM=<year-5> --set MORE_YEARS=<words>`.

The counting rules are in `reproduce/README.md`, and they follow the notebooks in
`INSPIREHEP_new_nbs/` and `students.ipynb`. Keep them unless the user asks to change them.

## Add an indicator

The pipeline is: data → `reproduce.py` (computes) → `compare.py` (passes it through) →
`export_dashboard.py` (one JSON dataset) → `dashboard/index.html` (draws it) → `standalone.py`
(inlines it).

1. **Compute it** in `reproduce.py` `main()`, as `out['<key>'] = …` (plain lists or dicts). Reuse
   `country_papers()`, `year_of()`, `LA`, `CURRENT_YEAR`, and the `records` list already loaded.
2. **Pass it through** in `compare.py`, by adding `'<key>'` to the keys copied into `out`.
3. **Export it** in `export_dashboard.py`, with `dump('<key>', rows)`, where `rows` is a list of flat
   dicts (one row per country, year, …).
4. **Name it** in `store_docs.py`: give it a title and a one-line description in `DATASETS`. The
   board's Sources section and its downloads list come from there.
5. **Draw it** in `reproduce/dashboard/index.html`:
   - add a card (`<div class="card">`) to a tab `<section>`, or a new tab (a `<button class="tab" data-tab="x">` and a `<section id="x" role="tabpanel" hidden>`);
   - put a chart container in the card: `<div class="chart" data-draw="my-chart" data-source="<key>"></div>`;
   - draw it with `dash.draw('my-chart', (el) => { … })`, using `dash.data('<key>').data` and d3 v7;
   - copy the pattern of an existing drawer (`mob-chart` for stacked bars, `pubs-dots` for a dot plot, `gender-chart` for a line);
   - keep text in the HTML and numbers in the data. Use `dash.colors[i]` and the CSS variables for colours, and `rp.tip(el)` for tooltips.
6. **Rebuild and check:** run the four commands again, open `out/dashboard.html`, and click through
   the tabs. With browser tools, check that only one tab panel is visible, that the new chart has SVG
   marks, and that the console has no errors. Check that every earlier dataset in `out/dash/` is
   unchanged.

Answering a one-off question doesn't need a board. Read the data with a short Python script, state the
counting rule you used, and offer to make it an indicator.

## Hand it back

Work on a branch and open a pull request; never push to `main`. A pull request that touches
`reproduce/` or `build/` runs a quick test on GitHub (Honduras and Paraguay).

- Commit the code and `reproduce/dashboard/index.html`.
- Commit `reproduce/dashboard.html` and `reproduce/dashboard_<year>.html` only if you rebuilt them from
  the data they belong to.
- Don't commit `out/` or the paper's JSON.

The boards on https://restrepo.github.io/inspireauth/ are updated by the maintainer (branch
`gh-pages`, `reproduce/pages_index.py`).
