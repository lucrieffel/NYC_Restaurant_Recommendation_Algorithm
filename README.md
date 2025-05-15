# NYC Restaurant Recommendation Algorithm

<div align="center">
  <img src="images/yelp_logo.svg" alt="Yelp Logo" height="80"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="images/tensorflow_logo.png" alt="TensorFlow Logo" height="80"/>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/ML-Restaurant%20Recommendation%20System-blue" alt="Restaurant Recommendation"/>
  <img src="https://img.shields.io/badge/TensorFlow-2.0+-orange" alt="TensorFlow"/>
  <img src="https://img.shields.io/badge/Python-3.7+-green" alt="Python"/>
  <img src="https://img.shields.io/badge/TFRS-Multitask%20Model-red" alt="TFRS"/>
  <img src="https://img.shields.io/badge/Firebase-Firestore-yellow" alt="Firebase"/>
  <img src="https://img.shields.io/badge/TypeScript-4.0+-blue" alt="TypeScript"/>
</p>

## Project Overview
This project implements a sophisticated recommendation system for New York City restaurants using machine learning techniques and data from the Yelp Public API. The system combines collaborative filtering with content-based features to provide personalized restaurant recommendations based on user preferences, cuisine types, and neighborhood data.

## Website(draft) Demo

<div align="center">
  <a href="https://youtu.be/ngF1s4eexYY" target="_blank">
    <img src="gifs/taste_ai_demo.gif" alt="NYC Restaurant Recommendation System Demo" width="640" />
    <p><strong>▶️ Click to watch clip video on YouTube</strong></p>
  </a>
</div>

**Note:** The web interface and recommendation model are still under active development as of May 2025. Stay tuned for an iOS app version coming soon!

### Website Tech Stack

<div align="center">
  <table>
    <tr>
      <td align="center" width="33%">
        <img src="https://firebase.google.com/downloads/brand-guidelines/PNG/logo-logomark.png" width="60" alt="Firebase Logo"/>
        <br><b>Firebase</b>
        <br><small>Authentication, Database, Hosting</small>
      </td>
      <td align="center" width="33%">
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/4c/Typescript_logo_2020.svg" width="60" alt="TypeScript Logo"/>
        <br><b>TypeScript</b>
        <br><small>Frontend Development</small>
      </td>
      <td align="center" width="33%">
        <img src="https://www.tensorflow.org/site-assets/images/project-logos/tensorflow-recommenders-logo-social.png" width="60" alt="TFRS Logo"/>
        <br><b>TensorFlow Recommenders</b>
        <br><small>Recommendation Engine</small>
      </td>
    </tr>
  </table>
</div>

- **Firebase**: Used for user authentication, real-time database for storing user preferences and restaurant data, and web application hosting
- **TypeScript**: Provides type safety and enhanced developer experience for building the interactive frontend interface
- **TensorFlow Recommenders (TFRS)**: Powers the recommendation engine, allowing for client-side model execution through TensorFlow.js

## Model Architecture
The recommendation system implements a multi-task learning approach combining two key objectives:

### Architecture Diagram
```
NYC Restaurant Recommendation Algorithm: Multitask Two-Tower Architecture
===========================================================================

Input Data: Restaurant IDs, User IDs, Ratings, Cuisine Types, Neighborhoods, Price Range
|
|
v                                                      v
+-------------------+                       +------------------------+
|   USER TOWER      |                       |   RESTAURANT TOWER     |
+-------------------+                       +------------------------+
|                   |                       |                        |
|   User ID         |                       |   Restaurant ID        |
|                   |                       |                        |
|   StringLookup    |                       |   StringLookup         |
|                   |                       |                        |
|   Embedding (32D) |                       |   Embedding (32D)      |
|                   |                       |                        |
+-------------------+                       +------------------------+
        |                                             |
        |                                             |
        +----------------+               +------------+
                         |               |
                         v               v
              +------------------------+
              |  RATING PREDICTION     |
              +------------------------+
              |  Dense (256) → ReLU    |
              |  Dense (128) → ReLU    |
              |  Dense (64)  → ReLU    |
              |  Dense (32)  → ReLU    |
              |  Dense (1)             |
              +------------------------+
                         |
                         v
                  Predicted Rating
        |                                             |
        |                                             |
        v                                             v
+-----------------------------------------------------------+
|        RETRIEVAL TASK (Similarity Matching)                |
|                                                           |
|        FactorizedTopK Metrics, Vector Similarity          |
+-----------------------------------------------------------+
                         |
                         v
              +------------------------+
              |    MULTI-TASK LOSS     |
              +------------------------+
              | λ₁·MSE(Rating) +       |
              | λ₂·Retrieval Loss      |
              +------------------------+
                         |
                         v
                Restaurant Recommendations
```

The architecture consists of two "towers" that process user and restaurant data separately, then performs two distinct but complementary tasks. The tasks are rating prediction and retrieval based on each tower's embeddings. The combined loss function with configurable weights balances both objectives with a weight of `model = YelpRecModel(rating_weight=0.3, retrieval_weight=0.7)` to provide accurate and personalized restaurant recommendations with a heavy weight on the retrieval task.

### Embedding Layer Architecture
- Utilizes a two-tower model architecture with separate embedding spaces:
  - Restaurant embedding layer (32-dimensional)
  - User embedding layer (32-dimensional)

### Multi-Task Training Objectives
1. **Retrieval Task**:
   - Learns vector representations of restaurants and users optimized for similarity matching
   - Implements TensorFlow Recommenders' FactorizedTopK metrics for recommendation quality evaluation
   - Enables efficient nearest-neighbor lookup for real-time recommendation serving

2. **Rating Prediction Task**:
   - Leverages a five-layer neural network (256→128→64→32→1 units) with ReLU activations
   - Predicts user ratings based on learned embeddings and additional features
   - Optimized with Mean Squared Error loss to accurately model user preferences

### Model Training Process
- Employs a weighted multi-task optimization balancing retrieval and rating prediction
- Utilizes TensorFlow data pipelines for efficient batch processing
- Implements early stopping to prevent overfitting
- Achieves retrieval top-100 accuracy of 5.4% and rating RMSE of 0.112

## Data Collection Process
### Yelp API Data Scraping
The project utilizes the Yelp Fusion API to collect extensive restaurant and review data across New York City:

1. **Restaurant Data Collection (`get_restaurants.py`)**:
   - Strategically queries the Yelp API with 480+ API calls to gather diverse restaurant data
   - Implements weighted random selection from 200+ cuisine types with higher probability for popular NYC cuisines
   - Collects comprehensive restaurant attributes including location, price range, ratings, and cuisine categories
   - Includes specific restaurant metadata such as coordinates, transaction types, and operational status

2. **Review Data Collection (`get_reviews.py`)**:
   - Retrieves user reviews for sampled restaurants (3 reviews per restaurant, reviews are limited and cut off by Yelp)
   - Tracks already-queried restaurants to prevent duplication
   - Preserves user information and timestamps for temporal analysis
   - Stores all data in structured CSV format for further processing

## Data Cleaning and Preprocessing
The data cleaning pipeline (`clean_data.py`) prepares the raw API data for the recommendation model:

1. **Restaurant Data Cleaning**:
   - Removes duplicates based on unique restaurant IDs
   - Extracts multiple cuisine types from categorized data
   - Converts text-based price indicators ($, $$, $$$, $$$$) to numerical values
   - Bins review counts into meaningful categories for improved feature representation
   - Maps ZIP codes to NYC neighborhoods using reference data

2. **Review Data Cleaning**:
   - Standardizes field names across datasets
   - Extracts and structures user metadata from nested JSON
   - Implements text cleaning for review content
   - Generates comprehensive logging to track data growth over time

## Model Deployment
The trained model is exported in TensorFlow.js format (`model.json` and weights) for browser-based inference, enabling real-time recommendations without requiring server-side computation for each prediction.


## Dataset Description

This project contains two primary cleaned datasets that serve as the foundation for the recommendation system:

### cleaned_yelp_restaurants.csv

<div align="center">
  <table>
    <tr>
      <th colspan="2" style="text-align:center; background-color:#f8f8f8;">Restaurant Dataset Overview</th>
    </tr>
    <tr>
      <td width="30%"><b>File Size</b></td>
      <td>4.0 MB</td>
    </tr>
    <tr>
      <td><b>Number of Records</b></td>
      <td>~7,300 unique NYC restaurants</td>
    </tr>
    <tr>
      <td><b>Coverage</b></td>
      <td>All 5 NYC boroughs with 25+ neighborhoods</td>
    </tr>
    <tr>
      <td><b>Cuisine Types</b></td>
      <td>200+ distinct cuisine categories</td>
    </tr>
  </table>
</div>

#### Key Fields

| Field Name | Description | Data Type |
|------------|-------------|-----------|
| `restaurant_id` | Unique Yelp ID for each restaurant | string |
| `restaurant_name` | Normalized name of the restaurant | string |
| `categories` | Comma-separated list of cuisine types | string |
| `price_num` | Numerical representation of price level (1-4) | float |
| `rating` | Average Yelp rating (1-5) | float |
| `review_count` | Number of reviews on Yelp | integer |
| `review_count_bins` | Binned categories of review counts | categorical |
| `neighborhood` | NYC neighborhood | string |
| `location_zip_code` | Restaurant ZIP code | string |
| `coordinates_latitude` | Latitude coordinate | float |
| `coordinates_longitude` | Longitude coordinate | float |
| `cuisine_0`, `cuisine_1`, `cuisine_2` | Extracted primary cuisine types | string |

### cleaned_yelp_reviews.csv

<div align="center">
  <table>
    <tr>
      <th colspan="2" style="text-align:center; background-color:#f8f8f8;">Review Dataset Overview</th>
    </tr>
    <tr>
      <td width="30%"><b>File Size</b></td>
      <td>21 MB</td>
    </tr>
    <tr>
      <td><b>Number of Records</b></td>
      <td>~20,000 user reviews</td>
    </tr>
    <tr>
      <td><b>Average Reviews per Restaurant</b></td>
      <td>2.7 reviews</td>
    </tr>
    <tr>
      <td><b>Rating Distribution</b></td>
      <td>Skewed toward positive (4-5 star) ratings</td>
    </tr>
  </table>
</div>

#### Key Fields

| Field Name | Description | Data Type |
|------------|-------------|-----------|
| `review_id` | Unique identifier for review | string |
| `restaurant_id` | Restaurant being reviewed (foreign key) | string |
| `user_id` | Yelp user ID of reviewer | string |
| `user_name` | Username of reviewer | string |
| `rating` | User rating (1-5) | float |
| `text` | Cleaned review text content | string |
| `time_created` | Timestamp of review | datetime |
| `queried_date` | Date when review was scraped | date |

Both datasets are extensively pre-processed to ensure consistency, handle missing values, and optimize for model training. Adding, validating, and cleaning data will be done separately via AWS Lambda and PostgreSQL. 

## References & Acknowledgments
- TensorFlow TFRS Tutorial: https://github.com/tensorflow/recommenders/blob/main/docs/examples/multitask.ipynb
- Taufik Azri: https://github.com/fickaz/TFRS-on-Retail-Data/blob/main/README.md
- Yelp Public Developer's API: https://docs.developer.yelp.com/docs/getting-started
- Noel Konagai, Yelp API Python Scraper: https://noelkonagai.github.io/Workshops/web_scraping_pt1_yelp/

All restaurant data is scraped directly from the Yelp API in accordance with their terms of use. Data is not used in any way for commercial purposes.

Developed with assistance from ChatGPT 4.0, v0, Claude 3.7 Sonnet, and GitHub CoPilot