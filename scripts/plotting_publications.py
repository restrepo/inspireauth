"""
scripts.plotting_publications.py

Plotting module of everything related to publications of the database for the INSPIRE LA dataset.

Note: some functions will be taken from the Jupyter notebooks of the `exploration` branch of the project.
Date: 19/08/2024
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter

from scripts.processing import generate_dataframe
from scripts.processing import generate_dataframe_latam
from scripts.processing import generate_articles_year_count


def plot_articles_per_year(country, save=False):
    """
    Plots the number of papers published per year for multiple countries.

    Parameters:
    countries (list of str): List of country names as strings.
    """
    # Generate the DataFrame for the specified country
    df = generate_dataframe(country=country)

    # Ensure the 'year' column is numeric and drop rows where 'year' is NaN
    df = df[pd.to_numeric(df["year"], errors="coerce").notnull()].reset_index(drop=True)
    df["year"] = pd.to_numeric(df["year"])

    # Filter out any papers before 1900 (if necessary)
    df = df[df["year"] >= 1900]

    # Create a range of years from the minimum year to 2021
    years_range = range(df["year"].min(), 2022)

    # Count the number of papers published each year
    year_counts = df["year"].value_counts().sort_index()
    year_counts = year_counts.reindex(years_range, fill_value=0)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 3))

    year_counts.plot(kind="bar", ax=ax, width=0.8)

    # Formatting the plot
    ax.set_title(f"Publications of {country}", size=15, pad=12)
    ax.set_xlabel("Year", size=13, labelpad=8)
    ax.set_ylabel("Number", size=13)
    ax.set_axisbelow(True)
    ax.grid(True, alpha=0.4)

    # Ensure the y-axis only shows integers
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%d"))

    # Show the plot
    plt.show()

    # Optional: Save the plot as a PDF
    if save:
        namefig = f"articles_{country}_per_year"
        # Define the directory relative to the current file
        output_dir = os.path.join(
            os.path.dirname(__file__),
            "../analysis_figures/individual_articles_per_year",
        )
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        # Save the figure
        fig.savefig(
            os.path.join(output_dir, f"{namefig}.pdf"), dpi=150, bbox_inches="tight"
        )


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
        df["country"] = country
        combined_df = pd.concat([combined_df, df])

    # Ensure the 'year' column is numeric
    combined_df = combined_df[
        pd.to_numeric(combined_df["year"], errors="coerce").notnull()
    ].reset_index(drop=True)
    combined_df["year"] = pd.to_numeric(combined_df["year"])

    # Filter out any papers before 1900 and after 2021
    combined_df = combined_df[
        (combined_df["year"] >= 1900) & (combined_df["year"] <= 2021)
    ]

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 4))

    # Plot each country's data
    for country, group_df in combined_df.groupby("country"):
        year_counts = group_df["year"].value_counts().sort_index()
        ax.bar(
            year_counts.index, year_counts.values, width=0.8, label=country, alpha=0.7
        )

    # Formatting the plot
    ax.set_title("Publications", size=15, pad=12)
    ax.set_xlabel("Year", size=13, labelpad=8)
    ax.set_ylabel("Number", size=13)
    ax.set_axisbelow(True)
    ax.grid(True, alpha=0.4)

    # Ensure the y-axis only shows integers
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%d"))

    # Add a legend
    ax.legend()

    # Optional: Save the plot as a PDF
    if save:
        joined_string = "_".join(countries)
        namefig = f"{joined_string}_plot"
        # Define the directory relative to the current file
        output_dir = os.path.join(
            os.path.dirname(__file__), "../analysis_figures/combined_articles_per_year"
        )
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        # Save the figure
        fig.savefig(
            os.path.join(output_dir, f"{namefig}.pdf"), dpi=150, bbox_inches="tight"
        )


def plot_articles_per_year_latam(save=False):
    """
    Plots the number of papers published per year for Latin America.

    Parameters:
        save (bool): Whether to save the plot as a PDF. Default is False.

    Returns:
        None

    Example:
        plot_articles_per_year_latam()
    """
    # Generate the DataFrame for the publications of Latin America
    df = generate_dataframe_latam()

    # Generate the Series of the number of articles published each year
    year_counts = generate_articles_year_count(df)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 3))

    year_counts.plot(kind="bar", ax=ax, width=0.8)

    # Formatting the plot
    ax.set_title(f"Publications of Latin America", size=15, pad=12)
    ax.set_xlabel("Year", size=13, labelpad=8)
    ax.set_ylabel("Number", size=13)
    ax.set_axisbelow(True)
    ax.grid(True, alpha=0.4)

    # Ensure the y-axis only shows integers
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%d"))

    # Show the plot
    plt.show()

    # Optional: Save the plot as a PDF
    if save:
        namefig = f"articles_latam_per_year"
        # Define the directory relative to the current file
        output_dir = os.path.join(
            os.path.dirname(__file__),
            "../analysis_figures/metrics_latam_per_year",
        )
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        # Save the figure
        fig.savefig(
            os.path.join(output_dir, f"{namefig}.pdf"), dpi=150, bbox_inches="tight"
        )

    return None


def plot_publication_percentage(df_combined, save=False):
    # Create a figure and axis object
    fig, ax = plt.subplots(figsize=(17, 4))

    # Plot the data on the axis
    ax.bar(df_combined.index, df_combined["Percentage"])

    # Set the labels and title
    ax.set_xlabel("Year", size=14, labelpad=8)
    ax.set_ylabel("Percentage", labelpad=8, size=14)
    ax.set_title(
        f"Latin American publications compared to global publications", size=15, pad=12
    )

    # Set the tick parameters
    ax.tick_params(
        axis="both", which="major", labelsize=12
    )  # Increase label size for major ticks

    ax.set_axisbelow(True)
    ax.grid(True, alpha=0.3)

    # Display the plot
    plt.show()

    # Optional: Save the plot as a PDF
    if save:
        namefig = f"articles_percentage_latam_per_year"
        # Define the directory relative to the current file
        output_dir = os.path.join(
            os.path.dirname(__file__),
            "../analysis_figures/metrics_latam_per_year",
        )
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        # Save the figure
        fig.savefig(
            os.path.join(output_dir, f"{namefig}.pdf"), dpi=150, bbox_inches="tight"
        )

    return None
