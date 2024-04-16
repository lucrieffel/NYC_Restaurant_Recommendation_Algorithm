#Source: https://github.com/noelkonagai/yelp-fusion/tree/master/fusion/python
#https://noelkonagai.github.io/Workshops/web_scraping_pt1_yelp/

from __future__ import print_function
import argparse
import json
import pprint
import requests
import sys
import os
import urllib
import time
from datetime import datetime
import pandas as pd
import random

try:
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

API_KEY = "jwcPnr8t-sDfENRF4g5AB2Wdg3ulPmVGBD0R0NRcWfs3iDrTF-5v-N-W6X551FvO01eg3GicECjNhAM-CrVPXimlA9Khs2u1nx15a88ZrudDb8QebDSp9I9IOrdCZXYx"
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'
DEFAULT_LOCATION = 'New York, NY'
SEARCH_LIMIT = 50

def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = f'{host}{quote(path.encode("utf8"))}'
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers, params=url_params)
    return response.json()

#get 3 reviews for each restaurant
def get_reviews(api_key, business_id, limit=3, sort_by='yelp_sort'):
    reviews_path = f"{business_id}/reviews"
    url_params = {
        'limit': limit,
        'sort_by': sort_by
    }
    return request(API_HOST, BUSINESS_PATH + reviews_path, api_key, url_params=url_params)

def clean_text(text):
    # Remove newlines and other formatting issues
    return " ".join(text.split())

def append_to_csv(dataframe, csv_path):
    if os.path.exists(csv_path):
        existing_data = pd.read_csv(csv_path)
        combined_data = pd.concat([existing_data, dataframe], ignore_index=True)
    else:
        combined_data = dataframe
    combined_data.to_csv(csv_path, index=False)
    
def load_queried_ids(filename):
    """Load previously queried restaurant IDs into a DataFrame."""
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=['queried_id'])

def append_id_to_csv(queried_id, filename):
    """Append a new queried restaurant ID to the CSV file."""
    new_row = pd.DataFrame({'queried_id': [queried_id]})
    if os.path.exists(filename):
        # Load the existing data
        df = pd.read_csv(filename)
        # Append new row
        df = pd.concat([df, new_row], ignore_index=True)
        # Drop duplicates
        df.drop_duplicates(subset='queried_id', inplace=True)
    else:
        df = new_row
    df.to_csv(filename, index=False)

    

def save_queried_ids(queried_ids, filename):
    pd.Series(list(queried_ids)).to_csv(filename, index=False, header=False)

def main():
    queried_ids_filename = 'queried_restaurant_ids.csv'
    queried_restaurant_ids_df = load_queried_ids(queried_ids_filename)
    print(f"Initial Length of Queried restaurant IDs: {len(queried_restaurant_ids_df)}")
    
    restaurants = pd.read_csv('yelp_restaurants.csv', low_memory=False)
    restaurants_drop_duplicates = restaurants.drop_duplicates(subset='id', keep='last', ignore_index=True)
    restaurants = restaurants_drop_duplicates.copy()
    
    reviews_data = []
    max_api_calls = 20  # Set the desired number of API calls for reviews
    api_calls_made = 0
    current_date = datetime.now().strftime('%Y-%m-%d')
    for index, row in restaurants.iterrows(): # Iterate over the rows of the DataFrame in  the yelp_restaurants.csv file
        if api_calls_made >= max_api_calls:
            break  # Stop if the max number of API calls is reached
        business_id = row['id'] # Get the business ID from the row
        if business_id in queried_restaurant_ids_df['queried_id'].values:
            print(f"Restaurant ID {business_id} has already been queried.")
            continue #skip if the restaurant has already been queried
        try:
            reviews_response = get_reviews(API_KEY, business_id, limit=3, sort_by='newest')
            for review in reviews_response.get('reviews', []):
                review['text'] = clean_text(review['text'])  # Clean the text of the review
                review['business_id'] = business_id  # Add the business_id to the review
                reviews_data.append(review)
            print(f"Got reviews for restaurant ID: {business_id}", end = '\n')
            print(f"Total reviews collected: {len(reviews_data)}", end = '\n')
            # Save the queried restaurant ID to the CSV file
            append_id_to_csv(business_id, queried_ids_filename)
            api_calls_made += 1  # Increment the API calls counter after each successful call
        except HTTPError as error:
            print(f'HTTP error {error.code}: {error.reason}')
        except Exception as e:
            print(f"An error occurred: {e}")

    # Create a DataFrame from the reviews data
    reviews_df = pd.DataFrame(reviews_data)
    # Flatten the reviews JSON structure and add more fields as necessary
    reviews_df = reviews_df.apply(lambda x: pd.Series({
        'business_id': x.get('business_id', ''),  # Include the business_id
        'review_id': x.get('id', ''),
        'url': x.get('url', ''),
        'text': x.get('text', ''),
        'rating': x.get('rating', ''),
        'time_created': x.get('time_created', ''),
        'user_id': x['user'].get('id', '') if x.get('user') else '',
        'user_name': x['user'].get('name', '') if x.get('user') else '',
        'user_profile_url': x['user'].get('profile_url', '') if x.get('user') else '',
        'user_image_url': x['user'].get('image_url', '') if x.get('user') else ''
    }), axis=1)
    
    reviews_df = pd.DataFrame(reviews_data)
    reviews_df['queried_date'] = current_date
    # reviews_df.to_csv('yelp_reviews.csv', index=False, encoding='utf-8')
    append_to_csv(reviews_df, 'yelp_reviews.csv')
    print("Reviews data saved to yelp_reviews.csv")
    

if __name__ == '__main__':
    main()