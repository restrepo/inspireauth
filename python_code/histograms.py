"""
This script produces the histograms for the
inspires database of Latin America

date: August 2022
author: Diego Restrepo, Manuel Morales Alvarado
"""

import pandas as pd
import matplotlib.pyplot as plt

def plot_articles_per_year(name_of_country):
    """
    Plot the articles published per year 
    of `name_of_country` and saves it as a pdf.
    Parameters
    ----------
        name_of_country: str
            name of the country for the histogram
    Returns
    -------
        None
    """
    # load the inspire_LA file with all authors
    db=pd.read_json('data/inspire_LA.json')
    # retain the ones whose institution belongs to `name_of_country`
    db=db[db['country']==name_of_country].reset_index(drop=True)
    # here we have several operations
    # 1 - db.papers: pd.Series with the lisf of papers of the author 
    # 2 - db.papers.apply(pd.Series): pd.Dataframe where the columns
    # are now the papers of each author
    # 3- db.papers.apply(pd.Series).stack(): pd.Series stacks all 
    # papers one column to make a pd.Series
    # 4 - b.papers.apply(pd.Series).stack().to_list(): self-explanatory
    dp=pd.DataFrame(db.papers.apply(pd.Series).stack().to_list())
    # drop duplicates in case two or more authors
    # collaborated on the same paper  
    dp=dp.drop_duplicates(subset='recid').reset_index(drop=True)
    # map the year column to numerical values
    dp['year'] = pd.to_numeric(dp['year'])

    # initialise axes
    fig, ax = plt.subplots(figsize=(10,3))
    dp[(dp['year']!='None') & (dp['year'] >= 1900)]['year'].value_counts().sort_index().plot(kind='bar')

    # formatting
    ax.set_title(f'Articles from {name_of_country} with up to 10 authors', size=15)
    ax.set_xlabel('Year', size=15, labelpad=6)
    ax.set_ylabel('Number of articles', size=15)
    ax.set_axisbelow(True)
    ax.grid(True)
    # save the figure
    fig.savefig(f'articles_countries_per_year/articles_{name_of_country}_per_year.pdf', dpi=150, bbox_inches = 'tight')

# The LA countries that appear in the file 

LA_countries = ['Brazil', 'Mexico', 'Venezuela', 'Chile', 'Argentina', 
                'Peru', 'Colombia', 'Cuba', 'Costa Rica', 'Ecuador',
                'Uruguay', 'Guatemala', 'Bolivia', 'Paraguay', 'Honduras']

# El Salvador, Republica Dominicana, Nicaragua do not appear  

# Execute the module 
for country in LA_countries:
    plot_articles_per_year(country)


