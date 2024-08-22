"""
main.py

Main module to execute the INSPIRE LA analysis.

Note: some functions will be taken from the Jupyter notebooks of the `exploration` branch of the project.
Date: 19/08/2024
"""

from scripts.loading import load_data, load_world_papers

from scripts.processing import (
    generate_dataframe_latam,
    generate_articles_year_count,
    generate_publication_percentage,
)

from scripts.plotting_publications import (
    plot_articles_per_year,
    plot_combined_papers_per_year,
    plot_articles_per_year_latam,
    plot_publication_percentage,
)


def main():
    """
    Main function to execute the analysis of the INSPIRE LA dataset.
    """
    # Analysis for collective Latin America analysis
    plot_articles_per_year_latam()

    # TODO: make sure all imports and variables are defined
    df_world = load_world_papers()
    df_latam = generate_articles_year_count(generate_dataframe_latam())
    df_combined = generate_publication_percentage(df_latam, df_world)

    # Plot the publication percentage of Latin America compared to the global production
    plot_publication_percentage(df_combined, save=True)

    # Example usage of the plotting functions
    countries = ["Chile", "Mexico"]

    # Plot individual articles per year for a specific country
    for entry in countries:
        plot_articles_per_year(country=entry, save=False)

    # Plot combined papers per year for multiple countries
    plot_combined_papers_per_year(countries, save=False)

    print("Analysis complete!")


if __name__ == "__main__":
    main()
