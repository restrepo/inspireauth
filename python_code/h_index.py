"""
This script produces the h-index of all countriesfor the
inspires database of Latin America

date: September 2022
author: Diego Restrepo, Manuel Morales Alvarado
"""

import pandas as pd
import matplotlib.pyplot as plt

def hIndex(citations: list):
    """
    https://github.com/kamyu104/LeetCode/blob/master/Python/h-index.py
    :type citations: List[int]
    :rtype: int
    
    # Given an array of citations (each citation is a non-negative integer)
    # of a researcher, write a function to compute the researcher's h-index.
    #
    # According to the definition of h-index on Wikipedia: 
    # "A scientist has index h if h of his/her N papers have
    # at least h citations each, and the other N − h papers have
    # no more than h citations each."
    #
    # For example, given citations = [3, 0, 6, 1, 5], 
    # which means the researcher has 5 papers in total
    # and each of them had received 3, 0, 6, 1, 5 citations respectively. 
    # Since the researcher has 3 papers with at least 3 citations each and 
    # the remaining two with no more than 3 citations each, his h-index is 3.
    #
    # Note: If there are several possible values for h, the maximum one is taken as the h-index.
    """
    import builtins
    sum=builtins.sum
    return sum(x >= i + 1 for i, x in enumerate(sorted(  list(citations), reverse=True)))

def h_index_country(country: str):
    """
    Calculates the h-index of `country`. 
    Parameters 
    ----------
        country: str
    Returns
        ans: int
    """
    # load the database
    db=pd.read_json('data/inspire_LA.json')
    # specify country
    db=db[db['country']==country].reset_index(drop=True)
    # get the dataframe of the publications
    dp=pd.DataFrame(db.papers.apply(pd.Series).stack().to_list()).drop_duplicates(subset='recid').reset_index(drop=True)
    ans = hIndex(dp.citation_count)
    return ans

# The LA countries that appear in the file 
LA_countries = ['Brazil', 'Mexico', 'Venezuela', 'Chile', 'Argentina', 
                'Peru', 'Colombia', 'Cuba', 'Costa Rica', 'Ecuador',
                'Uruguay', 'Guatemala', 'Bolivia', 'Paraguay', 'Honduras']

# El Salvador, Republica Dominicana, Nicaragua do not appear  

# Execute the module 
for country in LA_countries:
    h_index_country(country)


