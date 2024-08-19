import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter

from processing import generate_dataframe

def plot_articles_per_year(country, save=False):
    """
    Plots the number of papers published per year for multiple countries.

    Parameters:
    countries (list of str): List of country names as strings.
    """
    # Generate the DataFrame for the specified country
    df = generate_dataframe(country)

    # Ensure the 'year' column is numeric and drop rows where 'year' is NaN
    df = df[pd.to_numeric(df['year'], errors='coerce').notnull()].reset_index(drop=True)
    df['year'] = pd.to_numeric(df['year'])

    # Filter out any papers before 1900 (if necessary)
    df = df[df['year'] >= 1900]

    # Create a range of years from the minimum year to 2021
    years_range = range(df['year'].min(), 2022)

    # Count the number of papers published each year
    year_counts = df['year'].value_counts().sort_index()
    year_counts = year_counts.reindex(years_range, fill_value=0)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 3))

    year_counts.plot(kind='bar', ax=ax, width=0.8)

    # Formatting the plot
    ax.set_title(f'Publications of {country}', size=15, pad=12)
    ax.set_xlabel('Year', size=13, labelpad=8)
    ax.set_ylabel('Number', size=13)
    ax.set_axisbelow(True)
    ax.grid(True, alpha=0.4)

    # Ensure the y-axis only shows integers
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    # Show the plot
    plt.show()

    # Optional: Save the plot as a PDF
    if save:
        namefig = f"articles_{country}_per_year"
        # Define the directory relative to the current file
        output_dir = os.path.join(os.path.dirname(__file__), '../figures/individual_articles_per_year')
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        # Save the figure
        fig.savefig(os.path.join(output_dir, f'{namefig}.pdf'), dpi=150, bbox_inches='tight')


def plot_combined_papers_per_year(countries, save=False):
    """
    Plots the number of papers published per year for multiple countries.

    Parameters:
    countries (list of str): List of country names as strings.
    """
    # Create an empty DataFrame to hold all data
    combined_df = pd.DataFrame()

    # Combine all DataFrames into one, adding a 'country' column
    for country in countries:
        df = generate_dataframe(country)
        df['country'] = country
        combined_df = pd.concat([combined_df, df])

    # Ensure the 'year' column is numeric
    combined_df = combined_df[pd.to_numeric(combined_df['year'], errors='coerce').notnull()].reset_index(drop=True)
    combined_df['year'] = pd.to_numeric(combined_df['year'])

    # Filter out any papers before 1900 and after 2021
    combined_df = combined_df[(combined_df['year'] >= 1900) & (combined_df['year'] <= 2021)]

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 4))

    # Plot each country's data
    for country, group_df in combined_df.groupby('country'):
        year_counts = group_df['year'].value_counts().sort_index()
        ax.bar(year_counts.index, year_counts.values, width=0.8, label=country, alpha=0.7)

    # Formatting the plot
    ax.set_title('Publications', size=15, pad=12)
    ax.set_xlabel('Year', size=13, labelpad=8)
    ax.set_ylabel('Number', size=13)
    ax.set_axisbelow(True)
    ax.grid(True, alpha=0.4)

    # Ensure the y-axis only shows integers
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    # Add a legend
    ax.legend()

    # Optional: Save the plot as a PDF
    if save:
        joined_string = '_'.join(countries)
        namefig = f"{joined_string}_plot"
        # Define the directory relative to the current file
        output_dir = os.path.join(os.path.dirname(__file__), '../figures/combined_articles_per_year')
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        # Save the figure
        fig.savefig(os.path.join(output_dir, f'{namefig}.pdf'), dpi=150, bbox_inches='tight')
