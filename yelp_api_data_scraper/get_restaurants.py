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
    

API_KEY = ""
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'
DEFAULT_TERM = 'Asian'
DEFAULT_LOCATION = 'New York, NY'
SEARCH_LIMIT = 50

def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {'Authorization': 'Bearer %s' % api_key}
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()

#search by parameters for more info on parameter meaning see yelp API documentation: https://www.yelp.com/developers/documentation/v3/business_search
def search(api_key, term, location, sort_by='best_match', attributes=''):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'sort_by': sort_by,
        'attributes': attributes
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path, api_key)

def clean_json_file(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
    json_objects = []
    for line in data.splitlines():
        if line.strip():
            try:
                json_objects.append(json.loads(line))
            except json.JSONDecodeError:
                print("Error decoding JSON: ", line)
    with open(file_path, 'w') as f:
        for obj in json_objects:
            json.dump(obj, f)
            f.write('\n')

def query_api(term, location):
    if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
        clean_json_file('data.json')
    response = search(API_KEY, term, location)
    businesses = response.get('businesses')
    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return
    with open('data.json', 'a') as openfile:
        json.dump(response, openfile)
        openfile.write('\n')
    business_id = businesses[0]['id']
    print(u'{0} businesses found, querying business info for the top result "{1}" ...'.format(len(businesses), business_id))
    response = get_business(API_KEY, business_id)
    print(u'Result for business "{0}" found:'.format(business_id))
    pprint.pprint(response, indent=2)
    
def convert_json_to_dataframe(file_path):
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f if line.strip()]
    # Flatten the data and convert it to a DataFrame
    flattened_data = [flatten_business_info(business) for obj in data for business in obj.get('businesses', [])]
    return pd.DataFrame(flattened_data)

def flatten_business_info(business, term, location, sort_by, attributes,current_date):
    # Flatten the business JSON object to a single level dictionary to be used as a row in the DataFrame
    return {
        'id': business['id'],
        'name': business['name'],
        'image_url': business['image_url'],
        'is_closed': business['is_closed'],
        'url': business['url'],
        'review_count': business['review_count'],
        'rating': business['rating'],
        'categories': ', '.join([category['title'] for category in business['categories']]),
        'transactions': ', '.join(business.get('transactions', [])),
        'price': business.get('price', ''),
        'display_phone': business.get('display_phone', ''),
        'distance': business['distance'],
        'coordinates_latitude': business['coordinates']['latitude'],
        'coordinates_longitude': business['coordinates']['longitude'],
        'location_address1': business['location']['address1'],
        'location_address2': business['location'].get('address2', ''),
        'location_address3': business['location'].get('address3', ''),
        'location_city': business['location']['city'],
        'location_zip_code': business['location']['zip_code'],
        'location_country': business['location']['country'],
        'location_state': business['location']['state'],
        'location_display_address': ', '.join(business['location']['display_address']),
        'queried_term': term,
        'queried_location': location,
        'sort_by': sort_by,
        'attributes': attributes
    }
    
def save_data_to_csv(file_path, df_path):
    df = convert_json_to_dataframe(file_path)
    df.to_csv(df_path, index=False)
    print(f"Data saved to {df_path}")
    
def append_to_csv(dataframe, csv_path):
    # Check if the CSV file exists
    if os.path.exists(csv_path):
        # If it exists, load the existing data and append the new data
        existing_data = pd.read_csv(csv_path, low_memory=False)
        combined_data = pd.concat([existing_data, dataframe], ignore_index=True)
    else:
        # If the CSV file does not exist, just use the new df
        combined_data = dataframe
    # Save the combined data to the CSV file
    combined_data.to_csv(csv_path, index=False)

# Function to query restaurants by type
def query_restaurants_by_type(api_key, location, restaurant_type):
    url_params = {'term': f'{restaurant_type} restaurants', 'location': location, 'limit': SEARCH_LIMIT}
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

#long list of restaurant types taken directly from yelp in the restaurants category:https://blog.yelp.com/businesses/yelp_category_list/
restaurant_types = [
    'Afghan', 'African', 'Senegalese', 'South African', 'American (New)', 'American (Traditional)',
    'Arabian', 'Armenian', 'Asian Fusion', 'Australian', 'Austrian', 'Bangladeshi', 'Barbeque', 'Basque', 'Bavarian',
    'Beer Garden', 'Beer Hall', 'Beisl', 'Belgian', 'Flemish', 'Bistros', 'Black Sea',
    'Brasseries', 'Brazilian', 'Brazilian Empanadas', 'Central Brazilian', 'Northeastern Brazilian',
    'Northern Brazilian', 'Rodizios', 'Breakfast & Brunch', 'Pancakes', 'British', 'Buffets',
    'Bulgarian', 'Burgers', 'Burmese', 'Cafes', 'Themed Cafes', 'Cafeteria', 'Cajun/Creole',
    'Cambodian', 'Canadian (New)', 'Canteen', 'Caribbean', 'Dominican', 'Haitian', 'Puerto Rican',
    'Trinidadian', 'Catalan', 'Cheesesteaks', 'Chicken Shop', 'Chicken Wings', 'Chilean',
    'Chinese', 'Cantonese', 'Congee', 'Dim Sum', 'Fuzhou', 'Hainan', 'Hakka', 'Henghwa',
    'Hokkien', 'Hunan', 'Pekinese', 'Shanghainese', 'Szechuan', 'Teochew', 'Comfort Food',
    'Corsican', 'Creperies', 'Cuban', 'Curry Sausage', 'Cypriot', 'Czech', 'Czech/Slovakian',
    'Danish', 'Delis', 'Diners', 'Dinner Theater', 'Dumplings', 'Eastern European', 'Eritrean',
    'Ethiopian', 'Fast Food', 'Filipino', 'Fish & Chips', 'Flatbread',
    'Fondue', 'Food Court', 'Food Stands', 'Freiduria', 'French', 'Alsatian', 'Auvergnat',
    'Galician', 'Game Meat', 'Gastropubs', 'Georgian', 'German', 'Baden', 'Eastern German',
    'Gluten-Free', 'Greek', 'Guamanian', 'Halal', 'Hawaiian',
    'Honduran', 'Hong Kong Style Cafe', 'Hot Dogs', 'Hot Pot', 'Hungarian', 'Iberian', 'Indian',
    'Indonesian', 'International', 'Irish', 'Israeli', 'Italian', 'Abruzzese',
    'Altoatesine', 'Apulian', 'Calabrian', 'Cucina Campana', 'Emilian', 'Friulan', 'Ligurian',
    'Lumbard', 'Napoletana', 'Piemonte', 'Roman', 'Sardinian', 'Sicilian', 'Tuscan', 'Venetian',
    'Japanese', 'Blowfish', 'Conveyor Belt Sushi', 'Donburi', 'Gyudon', 'Oyakodon', 'Hand Rolls',
    'Horumon', 'Izakaya', 'Japanese Curry', 'Kaiseki', 'Kushikatsu', 'Oden', 'Okinawan', 'Okonomiyaki',
    'Onigiri', 'Ramen', 'Robatayaki', 'Soba', 'Sukiyaki', 'Takoyaki', 'Tempura', 'Teppanyaki',
    'Tonkatsu', 'Udon', 'Unagi', 'Western Style Japanese Food', 'Yakiniku', 'Yakitori', 'Jewish',
    'Kebab', 'Kopitiam', 'Korean', 'Kosher', 'Kurdish', 'Laos', 'Laotian', 'Latin American',
    'Colombian', 'Salvadoran', 'Venezuelan', 'Live/Raw Food', 'Lyonnais', 'Malaysian', 'Mamak',
    'Nyonya', 'Meatballs', 'Mediterranean', 'Falafel', 'Mexican', 'Eastern Mexican', 'Jaliscan',
    'Northern Mexican', 'Oaxacan', 'Pueblan', 'Tacos', 'Tamales', 'Yucatan', 'Middle Eastern',
    'Egyptian', 'Lebanese',  'Modern European', 'Mongolian',
    'Moroccan', 'New Zealand' 'Night Food', 'Nikkei', 'Noodles',
    'Norcinerie', 'Open Sandwiches', 'Oriental', 'Pakistani', 'Pan Asian', 'Parent Cafes', 'Parma',
    'Persian/Iranian', 'Peruvian', 'PF/Comercial', 'Pita', 'Pizza', 'Polish', 'Pierogis', 'Polynesian',
    'Pop-Up Restaurants', 'Portuguese', 'Alentejo', 'Algarve', 'Azores', 'Beira', 'Fado Houses',
    'Madeira', 'Minho', 'Ribatejo', 'Tras-os-Montes', 'Potatoes', 'Poutineries', 'Pub Food', 'Rice',
    'Romanian', 'Russian', 'Salad', 'Sandwiches', 'Scandinavian',
    'Scottish', 'Seafood', 'Serbo Croatian', 'Signature Cuisine', 'Singaporean', 'Slovakian', 'Somali',
    'Soul Food', 'Soup', 'Southern', 'Spanish', 'Arroceria/Paella', 'Sri Lankan', 'Steakhouses',
    'Supper Clubs', 'Sushi Bars', 'Swabian', 'Swedish', 'Swiss Food', 'Syrian', 'Taiwanese',
    'Tapas Bars', 'Tapas/Small Plates', 'Tavola Calda', 'Tex-Mex', 'Thai', 'Traditional Norwegian',
    'Traditional Swedish', 'Turkish',  'Homemade Food',
    'Turkish Ravioli', 'Ukrainian', 'Uzbek', 'Vegan', 'Vegetarian', 'Venison',
    'Vietnamese', 'Waffles', 'Wok', 'Wraps']


#create a dictionary with favorite restaurant types and approximate weights that will be used to randomly select a restaurant type with a higher probability
#this dict was updated 2/9/2024
#this dict was created by counting the number of NYC cuisine values in the Beli app
favorite_restaurant_types = {
    'Bagels': 40, #11
    'Japanese': 5, #42
    'Italian': 10, #31
    'Cafe': 30, #30
    'Thai': 35,
    'American': 25,
    'Sushi': 10, #25
    'Chinese': 25,
    'Vietnamese': 50, #25
    'Korean': 24,
    'Breakfast & Brunch': 50, #20
    'Healthy': 20,
    'French': 16,
    'Bakery': 16,
    'Mediterranean': 16,
    'Cocktail Bars': 15,     #suggest bars too(cocktail bars, wine bars, breweries, anything with cool vibes)
    # 'Bagels': 11,
    'Dim Sum': 9,
    'Cantonese': 7, 
    'Omakase': 10,
    'Indian': 6,
    'Mexican': 6,
    'Pizza': 4,
}

def main():
    all_restaurants = []
    max_api_calls = 480  # Set the desired number of API calls
    api_calls_made = 0
    current_date = datetime.now().strftime('%Y-%m-%d')
    while api_calls_made < max_api_calls:
        # 1/3 chance to select from favorite categories with weights
        if random.choice([False, False, True]):
            selected_type = random.choices(list(favorite_restaurant_types.keys()), weights=favorite_restaurant_types.values(), k=1)[0]
        else:
            # Otherwise, select randomly without weights(from the long list of restaurant types taken directly from yelp in the restaurants category:https://blog.yelp.com/businesses/yelp_category_list/)
            selected_type = random.choice(restaurant_types)
            # selected_type = random.choice(list(favorite_restaurant_types.keys()))
            
        attributes = 'hot_and_new' if random.choice([False, False, False, True]) else ''
        try:
            response = search(API_KEY, selected_type + ' restaurants', DEFAULT_LOCATION, sort_by='best_match', attributes=attributes)
            for business in response.get('businesses', []):
                business_info = flatten_business_info(business, selected_type, DEFAULT_LOCATION, 'best_match', attributes, current_date)
                all_restaurants.append(business_info)
            print(f"Found {len(response.get('businesses', []))} {selected_type} restaurants with {('hot_and_new' if attributes else 'no specific')} attribute. Total restaurants: {len(all_restaurants)}")
            api_calls_made += 1
        except HTTPError as error:
            print(f'Encountered HTTP error {error.code} on {error.url}: {error.read()} during API call {api_calls_made}')
        except Exception as e:
            print(f"The following error occurred: {e}")
    df = pd.DataFrame(all_restaurants)
    #add queried_date to the dataframe
    df['queried_date'] = current_date
    append_to_csv(df, 'yelp_restaurants.csv')
    print(f"Restaurants data saved/appended to yelp_restaurants.csv")

if __name__ == '__main__':
    main()
