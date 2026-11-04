# inspireauth
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23868569.svg)](https://doi.org/10.5281/zenodo.23868569)

INSPIRE-HEP author records for Latin America, and the code used to build them.

## The dataset: `data/inspire_LA.json.gz`

[`data/inspire_LA.json.gz`](./data/inspire_LA.json.gz) is the full dataset: a single gzipped JSON file (21 MB; 333 MB uncompressed) with **73,118 records of 36,570 distinct authors** in High Energy Physics, Cosmology and Astroparticle Physics with affiliations to Latin American institutions in [INSPIRE-HEP](https://inspirehep.net), and 60,538 distinct papers, downloaded on 2026-11-03 (papers up to 2026).

The paper *Statistical Analysis of Scientific Metrics in High Energy, Cosmology, and Astroparticle Physics in Latin America* (M. Morales-Alvarado, F. Quevedo, M. Ramos-Hamud, D. Restrepo) used the earlier version, with 57,588 records of 29,979 authors and 49,181 papers up to 2022: it is in the [Zenodo release](https://doi.org/10.5281/zenodo.23868569) and in the git tag `v1.0.1` of this repository.

It is an ordinary git file (no Git LFS needed). The paper's version, `data/inspire_LA.json` at tag `v1.0.1`, is stored with [Git LFS](https://git-lfs.com): check it out with `git-lfs` installed, or download it from [Zenodo](https://doi.org/10.5281/zenodo.23868569).

```python
import gzip, json
with gzip.open('data/inspire_LA.json.gz', 'rt', encoding='utf-8') as f:
    authors = json.load(f)          # list of 73,118 dicts
```

or `pandas.read_json('data/inspire_LA.json.gz')`; `gunzip -k data/inspire_LA.json.gz` gives the plain JSON.

### How the records were built

For each Latin American country, the institutions of that country were taken from INSPIRE-HEP, and for each institution its papers with at most 10 authors. Every author of those papers became a record. Authors are then extended with their INSPIRE profile (positions, advisors, e-mails, identifiers), each paper gets the rank and affiliation the author held when it was published ([students.ipynb](students.ipynb)), and gender is inferred from the first names and the country of the affiliation ([gender.ipynb](gender.ipynb), [gender-genderize.ipynb](gender-genderize.ipynb)). The construction code is in [INSPIREHEP.ipynb](INSPIREHEP.ipynb); [build/build_inspire_LA.py](build/build_inspire_LA.py) follows the same rules in one script (cached, batched requests; gender with [genderize-offline](https://pypi.org/project/genderize-offline/)) and built the current file: `python build/build_inspire_LA.py` (writes `data/inspire_LA.json.gz`; the same data give the same bytes). Publishing a release of this repository rebuilds it automatically and adds its board to <https://restrepo.github.io/inspireauth/> (see [reproduce/README.md](reproduce/README.md#automatic-updates-and-github-pages)).

<img src="img/authors.svg" width=900 alt="Structure of an inspire_LA record">

**There is one record per author and institution.** An author with several institutions in INSPIRE (current or past, in Latin America or elsewhere) appears once for each of them, and every one of those records carries the author's whole list of papers. Deduplicate by `author_id` to count authors, and by `papers[].recid` to count papers.

### Data schema

Every field of a record, with its type, how often it is present, where it comes from and the
pitfalls (the string `"None"`, the shared paper lists), is documented in
**[docs/data-schema.md](docs/data-schema.md)**. A JSON Schema is in
[docs/inspire_LA.schema.json](docs/inspire_LA.schema.json); check a file with
`python docs/validate_schema.py data/inspire_LA.json.gz`. Both the 2026 rebuild and the paper's version
pass it. The diagram above is drawn by `docs/tools/draw_schema.py`.

## Other files

| File | Content |
|---|---|
| `data/inspire_institutions.json` | INSPIRE-HEP institutions. |
| `data/inspire_dois.json`, `data/recids.json` | DOIs and INSPIRE record numbers of the papers, used for the OpenAlex comparison. |
| `data/only_inspire_in_OpenAlex.json.gz`, `data/only_openalex.json`, `data/openalex_topics.json.gz` | Comparison with OpenAlex ([openalex-topics.ipynb](openalex-topics.ipynb)). |
| `data/genderize.csv`, `data/test_gender.csv` | Input and test data of the gender inference. |
| `data/cinvestav.csv`, `data/work.json` | Example and test data. |

## Citation

Cite the dataset with its DOI, [10.5281/zenodo.23868569](https://doi.org/10.5281/zenodo.23868569); see [CITATION.cff](CITATION.cff). License: CC0-1.0.

## Maintenance: delete older versions of the dataset
To delete older versions of a file in your repository, you need to remove or clean up the history where those versions exist. Here are the steps you can follow:

1. **Identify the Commits**: Find the commits where the older versions of the file exist.
2. **Rebase or Filter the History**: Use tools like `git rebase` or `git filter-repo` to edit the history and remove the older versions of the file.
3. **Force Push**: After editing the history, you will need to force push the changes to the remote repository.

Here is an example using `git filter-repo`:

1. Install `git-filter-repo` if you haven't already:

   ```sh
   pip install git-filter-repo
   ```

2. Run the following command to remove the file from the history:

   ```sh
   git filter-repo --path data/inspire_LA.json --invert-paths
   ```

3. Force push the changes:

   ```sh
   git push origin --force
   ```

Please note that rewriting history can have significant effects, especially if others are working on the same repository. Ensure you coordinate with your team and understand the implications before proceeding.
