"""
This script produces the number of papers for the
countries of the inspires database of Latin America

date: August 2022
author: Diego Restrepo, Manuel Morales Alvarado
"""

import pandas as pd

def number_of_papers(name_of_country):
    """
    Calculates the total number of papers
    published by the country. 
    Parameters
    ----------
        name_of_country: str
    Returns
    -------
        None 
    """
    db=pd.read_json('data/inspire_LA.json')
    db=db[db['country']==name_of_country].reset_index(drop=True)
    dp=pd.DataFrame( db.papers.apply(pd.Series).stack().to_list() ).drop_duplicates(subset='recid').reset_index(drop=True)
    print(f"{name_of_country} = {dp.shape[0]} papers.")
    pass
  
# The LA countries that appear in the file 

LA_countries = ['Brazil', 'Mexico', 'Venezuela', 'Chile', 'Argentina', 
                'Peru', 'Colombia', 'Cuba', 'Costa Rica', 'Ecuador',
                'Uruguay', 'Guatemala', 'Bolivia', 'Paraguay', 'Honduras']

# El Salvador, Republica Dominicana, Nicaragua do not appear  

# Execute the module 
for country in LA_countries:
    number_of_papers(country)