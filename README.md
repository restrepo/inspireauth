# inspireauth
Get authors info from INSPIRE-HEP

# Construction of JSON object Authors from INSPIRE-HEP
<img src="https://raw.githubusercontent.com/restrepo/inspire/master/img/authors.svg" width=700>

Example of authors JSON file for Latin Americans author in [data](./data) → [inspire_LA.json](./data/inspire_LA.json) with 
extended scheme as in [students.ipynb](students.ipynb) and gender as in [gender.ipynb](./gender.ipynb)

## Install

## Usage

## Delete older version of dataset
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
