import pandas as pd


def process(community_filename: str, hesitancy_df: str) -> pd.DataFrame:
    # Read in CDC Datasets (Community Levels and Hesitancy Data)
    community_df = pd.read_csv(community_filename)
    hesitancy_df = pd.read_csv(hesitancy_df)

    # Filter the community levels dataset to only consider the earliest reports closest to when the
    # hesitancy data was collected.
    community_df_earliest = community_df.loc[community_df['date_updated'] == min(community_df['date_updated']), :]

    # Join the community dataset with the hesitancy dataset (inner join) using the FIPS code. Since the codes are
    # numpy.int64 type, they are automatically formatted (leading zeros are removed).
    joined_df = community_df_earliest.set_index('county_fips'). \
        join(hesitancy_df.set_index('FIPS Code'), how='inner')

    # Filter only the relevant columns from the joined dataset
    filtered_df = joined_df[['county', 'state', 'county_population',
                             'covid_hospital_admissions_per_100k',
                             'covid_cases_per_100k',
                             'covid-19_community_level',
                             'Estimated hesitant',
                             'Estimated strongly hesitant',
                             'Social Vulnerability Index (SVI)', 'SVI Category',
                             'Percent adults fully vaccinated against COVID-19 (as of 6/10/21)',
                             'Percent Hispanic',
                             'Percent non-Hispanic American Indian/Alaska Native',
                             'Percent non-Hispanic Asian', 'Percent non-Hispanic Black',
                             'Percent non-Hispanic Native Hawaiian/Pacific Islander',
                             'Percent non-Hispanic White',
                             'County Boundary', 'State Boundary']]

    # Rename columns to shorter snake case uniform formatting
    final_df = filtered_df.rename({
        'covid_hospital_admissions_per_100k': 'hospital_100k',
        'covid_cases_per_100k': 'cases_100k',
        'covid-19_community_level': 'community_level',
        'Estimated hesitant': 'percent_hesitant',
        'Estimated strongly hesitant': 'percent_strongly_hesitant',
        'Social Vulnerability Index (SVI)': 'SVI',
        'SVI Category': 'SVI_category',
        'Percent adults fully vaccinated against COVID-19 (as of 6/10/21)': 'percent_vaccinated',
        'Percent Hispanic': 'percent_hispanic',
        'Percent non-Hispanic American Indian/Alaska Native': 'percent_AIAN',
        'Percent non-Hispanic Asian': 'percent_asian',
        'Percent non-Hispanic Black': 'percent_black',
        'Percent non-Hispanic Native Hawaiian/Pacific Islander': 'percent_NHPI',
        'Percent non-Hispanic White': 'percent_white',
        'County Boundary': 'county_boundary',
        'State Boundary': 'state_boundary'},
        axis='columns')

    return final_df
