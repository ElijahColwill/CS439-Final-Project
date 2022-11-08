import pandas as pd


def process(community_filename: str, hesitancy_df: str, date: str) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    # Read in CDC Datasets (Community Levels and Hesitancy Data)
    community_df = pd.read_csv(community_filename)
    hesitancy_df = pd.read_csv(hesitancy_df)

    # Filter community levels data by selecting relevant columns
    community_df_filtered = community_df[[
        'county',
        'county_fips',
        'state',
        'county_population',
        'covid_hospital_admissions_per_100k',
        'covid_cases_per_100k',
        'covid-19_community_level',
        'date_updated'
    ]]

    # Rename community levels columns to uniform short snake case for easier reference
    community_df_final = community_df_filtered.rename({
        'covid_hospital_admissions_per_100k': 'hospital_100k',
        'covid_cases_per_100k': 'cases_100k',
        'covid-19_community_level': 'community_level'
    }, axis='columns')

    # Filter vaccine hesitancy data by selecting relevant columns
    hesitancy_df_filtered = hesitancy_df[[
        'FIPS Code',
        'Estimated hesitant',
        'Estimated strongly hesitant',
        'Social Vulnerability Index (SVI)', 'SVI Category',
        'Percent adults fully vaccinated against COVID-19 (as of 6/10/21)',
        'Percent Hispanic',
        'Percent non-Hispanic American Indian/Alaska Native',
        'Percent non-Hispanic Asian', 'Percent non-Hispanic Black',
        'Percent non-Hispanic Native Hawaiian/Pacific Islander',
        'Percent non-Hispanic White',
        'County Boundary',
        'State Boundary'
    ]]

    # Rename vaccine hesitancy columns to uniform short snake case for easier reference
    # With the exception of percentages of racial categories so that they display is a more
    # readable way.
    hesitancy_df_final = hesitancy_df_filtered.rename({
        'FIPS Code': 'county_fips',
        'Estimated hesitant': 'percent_hesitant',
        'Estimated strongly hesitant': 'percent_strongly_hesitant',
        'Social Vulnerability Index (SVI)': 'SVI',
        'SVI Category': 'SVI_category',
        'Percent adults fully vaccinated against COVID-19 (as of 6/10/21)': 'percent_vaccinated',
        'Percent non-Hispanic American Indian/Alaska Native': 'Percent American Indian/Alaska Native',
        'Percent non-Hispanic Asian': 'Percent Asian',
        'Percent non-Hispanic Black': 'Percent Black',
        'Percent non-Hispanic Native Hawaiian/Pacific Islander': 'Percent Native Hawaiian/Pacific Islander',
        'Percent non-Hispanic White': 'Percent White',
        'County Boundary': 'county_boundary',
        'State Boundary': 'state_boundary'
    }, axis='columns')

    # Set index of both dataframes to FIPS code in place
    community_df_final.set_index('county_fips', inplace=True)
    hesitancy_df_final.set_index('county_fips', inplace=True)

    # Return filtered/renamed community and hesitancy datasets, and a dataset joined and filtered by date
    return community_df_final, hesitancy_df_final, process_date(community_df_final, hesitancy_df_final, date)


def process_date(community_df: pd.DataFrame, hesitancy_df: pd.DataFrame, date: str) -> pd.DataFrame:
    # Filter the community levels dataset to only consider the passed date.
    # Check that this date is in the list of dates and raise an exception if not.
    date_list = community_df['date_updated'].unique()
    if date not in date_list:
        raise Exception(f"Date not valid. Report dates: {date_list}")

    # Select rows with the matching report date
    community_df_date = community_df.loc[community_df['date_updated'] == date, :]

    # Join the community dataset on the passed date with the hesitancy dataset (inner join) using the FIPS code.
    # Since the codes are numpy.int64 type, they are automatically formatted (leading zeros are removed).
    return community_df_date.join(hesitancy_df, how='inner')
