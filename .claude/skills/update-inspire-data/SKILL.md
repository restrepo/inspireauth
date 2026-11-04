---
name: update-inspire-data
description: Download the Latin American HEP author records again from INSPIRE-HEP into data/inspire_LA.json.gz (build/build_inspire_LA.py, about 45 minutes), validate the new download against the previous one, and make the board of the updated data (reproduce/dashboard_YYYY.html), by hand or through the repository's release workflow. Use whenever someone working in a clone of restrepo/inspireauth asks to update, refresh or rebuild the INSPIRE data, to test the download on a few countries, or to see how the paper's numbers change with newer data.
---

# Update the INSPIRE-HEP data

Run from the repository root, after `pip install -r reproduce/requirements.txt`.

## Automatic

Publishing a GitHub release whose tag starts with `v` (the maintainer's job) runs
`.github/workflows/update-data.yml`, in about an hour:
1. it downloads the data again;
2. it attaches `inspire_LA.json.gz` and the board to the release;
3. it opens a pull request with them;
4. it adds the board to https://restrepo.github.io/inspireauth/.

From the Actions tab, "Update data and boards" → Run workflow with *publish* off gives a dry run whose
files are saved in the run.

## By hand

```bash
python build/build_inspire_LA.py --countries Honduras Paraguay --cache build/cache/test --out out/test.json.gz   # ~20 s check
python build/build_inspire_LA.py --cache build/cache/$(date +%F) --out out/inspire_LA.json.gz                    # ~45 min
```

- **Run the full download in the background.** It makes about 4,000 requests to INSPIRE, cached in
  `build/cache/` (ignored by git), so a stopped run resumes where it was.
- **Use a new cache folder per download date.** An old cache returns the old data.
- **The rules** are those of `INSPIREHEP.ipynb`, `students.ipynb` and `gender-genderize.ipynb` (see the
  script's docstring): papers with at most 10 authors, one record per author and institution, and
  genders from `genderize-offline` (World Gender Name Dictionary 2.0).

**Validate before using it:**
- records, authors and papers should grow compared with `data/inspire_LA.json.gz`;
- almost no earlier Latin American paper should be missing (use `country_papers()` from
  `reproduce/reproduce.py` on both files);
- `"missing": true` should be rare in `build/cache/<date>/*.jsonl`;
- the current year is partial, and e-mails are null (the INSPIRE API no longer gives them).

Report anything unusual (a country with far fewer papers, many missing profiles) before going on.

**Board of the new data:**

```bash
Y=$(date +%Y); D=$(date +%F)
python reproduce/reproduce.py out/inspire_LA.json.gz out/results.json --year $Y
python reproduce/compare.py reproduce/paper/tables.json out/results.json out/page_data.json
python reproduce/export_dashboard.py out/page_data.json out/dash/
python reproduce/standalone.py out/dash/ out/dashboard_$Y.html --edits reproduce/dashboard/edits_update.json \
  --set YEAR=$Y --set DATE=$D --set ACTIVE_FROM=$((Y-5)) --set MORE_YEARS=<Y-2022 in words>
```

To change the board itself, or to add an indicator, use the skill `reproduce-paper`.

## Hand it back

Work on a branch: copy `out/inspire_LA.json.gz` to `data/inspire_LA.json.gz` and the board to
`reproduce/dashboard_<year>.html`. Update the counts in `README.md`, then open a pull request.

- **`data/inspire_LA.json.gz` is an ordinary git file** (~21 MB). Never commit an uncompressed JSON and
  never put data in Git LFS: LFS storage is not freed by deleting commits.
- **The paper's data** (tag `v1.0.1`, Zenodo doi:10.5281/zenodo.23868569) stay as they are.
