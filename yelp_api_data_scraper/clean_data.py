import numpy as np
import pandas as pd
import os
from datetime import datetime
import ast

#clean restaurants dataframe function
def clean_restaurants(df, neighborhood_df):
    #drop duplicates
    df = df.drop_duplicates(subset='id', keep='last', ignore_index=True).copy()
    
    #rename columns for consistency
    df.rename(columns={'id': 'restaurant_id', 'name': 'restaurant_name'}, inplace=True)
    
    #split on cuisine type(first 3 only)
    cuisine_df = df['categories'].str.split(',', expand=True)
    for i in range(3):  # Assuming you're only interested in the first three cuisines
        df.loc[:, f'cuisine_{i}'] = cuisine_df[i]
    
    #get price rating as a number
    df.loc[:, 'price_num'] = df['price'].str.len()
    
    #bin review counts
    bins = [0, 10, 50, 100, 200, 500, 1000, 5000, 10000, 20000, 50000, np.inf]
    labels = ['0-10', '11-50', '51-100', '101-200', '201-500', '501-1000', '1001-5000', '5001-10000', '10001-20000', '20001-50000', '50001+']
    df.loc[:, 'review_count_bins'] = pd.cut(df['review_count'], bins=bins, labels=labels)
    
    #get neighborhood based on zip codes
    df['location_zip_code'] = df['location_zip_code'].astype(str)
    df['location_zip_code'] = df['location_zip_code'].str.split('.').str[0]
    neighborhood_df['ZipCode'] = neighborhood_df['ZipCode'].astype(str)
    zip_to_neighborhood = neighborhood_df.set_index('ZipCode')['Neighborhood'].to_dict()
    df['neighborhood'] = df['location_zip_code'].map(zip_to_neighborhood)
    return df

#clean reviews dataframe
def clean_reviews(df):
    df.rename(columns={'business_id': 'restaurant_id'}, inplace=True)
    df['user'] = df['user'].apply(string_to_dict)
    user_columns = ['user_id', 'user_name', 'user_profile_url', 'user_image_url']
    for col in user_columns:
        df[col] = df['user'].apply(lambda x: x.get(col.split('_')[1]) if x else None)
    df['review_id'] = df['id'].fillna(df['review_id'])
    return df

def string_to_dict(string):
    try:
        return ast.literal_eval(string)
    except (ValueError, SyntaxError):
        # print("ValueError/SyntaxError: ", string)
        return {}

# Log Update Functions
def update_log_file(df, log_file_path, log_columns, unique_count_column):
    try:
        log_df = pd.read_csv(log_file_path)
    except FileNotFoundError:
        log_df = pd.DataFrame(columns=log_columns)
    total_count = len(df[unique_count_column].unique())
    queried_date = datetime.now().strftime('%Y-%m-%d')
    new_row = {'queried_date': queried_date, log_columns[1]: total_count}
    log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
    # log_df.drop_duplicates(subset='queried_date', keep='last', ignore_index=True, inplace=True)
    log_df.to_csv(log_file_path, index=False)
    return log_df


def main():
    #get base directory
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    # print("Current Directory", current_dir)
    project_base_dir = os.path.dirname(current_dir)  # Navigate one level up
    # print("Project Base Directory", project_base_dir)

    #relative paths for 'yelp_scraper' and 'yelp_api_scraper' folders
    scraper_path = os.path.join(project_base_dir, 'yelp_scraper', 'yelp_api_scraper')
    neighborhoods_path = os.path.join(project_base_dir, 'yelp_scraper', 'yelp_api_scraper', 'nyc-zip-codes.csv')
    
    #define file paths
    reviews_path = os.path.join(scraper_path, 'yelp_reviews.csv')
    restaurants_path = os.path.join(scraper_path, 'yelp_restaurants.csv')
    
    #error handling for file paths
    for path in [reviews_path, restaurants_path, neighborhoods_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file {path} does not exist. Please check the file paths and directory structure.")
    
    # Load DataFrames
    reviews = pd.read_csv(reviews_path, low_memory=False)
    restaurants = pd.read_csv(restaurants_path, low_memory=False)
    neighborhoods = pd.read_csv(neighborhoods_path)
    
    # print(neighborhoods_path)
    
    # clean dataframes
    cleaned_restaurants = clean_restaurants(restaurants, neighborhoods)
    cleaned_reviews = clean_reviews(reviews)
    
    # update Logs
    restaurant_log_path = os.path.join(current_dir, 'restaurant_count_log.csv')
    review_log_path = os.path.join(current_dir, 'review_count_log.csv')
    update_log_file(cleaned_restaurants, restaurant_log_path, ['queried_date', 'total_restaurant_count'], 'restaurant_id')
    update_log_file(cleaned_reviews, review_log_path, ['queried_date', 'total_review_count'], 'restaurant_id')
    
    cleaned_restaurants_path = os.path.join(current_dir, 'cleaned_yelp_restaurants.csv')
    cleaned_reviews_path = os.path.join(current_dir, 'cleaned_yelp_reviews.csv')
    cleaned_restaurants.to_csv(cleaned_restaurants_path, index=False)
    cleaned_reviews.to_csv(cleaned_reviews_path, index=False)

if __name__ == "__main__":
    main()