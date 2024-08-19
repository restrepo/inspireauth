"""
main.py

Main module to execute the INSPIRE LA analysis.

Note: some functions will be taken from the Jupyter notebooks of the `exploration` branch of the project.
Date: 19/08/2024
"""

from scripts.plotting_publications import (
    plot_articles_per_year,
    plot_combined_papers_per_year,
)


def main():
    """
    Main function to execute the analysis of the INSPIRE LA dataset.
    """
    # Example usage of the plotting functions
    countries = ["Chile", "Mexico"]

    # Plot individual articles per year for a specific country
    for entry in countries:
        plot_articles_per_year(country=entry, save=True)

    # Plot combined papers per year for multiple countries
    plot_combined_papers_per_year(countries, save=True)

    print("Analysis complete!")


if __name__ == "__main__":
    main()
