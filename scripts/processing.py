import pandas as pd


def generate_dataframe(db_master: pd.DataFrame, country: str) -> pd.DataFrame:
    """
    Generate a DataFrame whose rows are all the publications of a given country.
    The `recid` entry is unique for each publication.
    """
    # select column
    db = db_master[db_master["country"] == country].reset_index(drop=True)

    # obtain list of the institutions of the country
    inst_list = db["institution_id"].drop_duplicates().to_list()

    # stack papers and select the ones from the appropriate institutions
    dp = pd.DataFrame(db.papers.apply(pd.Series).stack().to_list()).reset_index(
        drop=True
    )
    dp = dp[dp["institution_id"].isin(inst_list)]

    # get rid of paper duplicates
    dp = dp.drop_duplicates(subset="recid")

    # skip entries without listed `year`. This ignores the papers that do not have year.
    dp = dp[pd.to_numeric(dp["year"], errors="coerce").notnull()].reset_index(drop=True)

    # transform to numerical values
    dp["year"] = pd.to_numeric(dp["year"])
    # get rid of old entries
    dp = dp[dp["year"] >= 1900]

    return dp
