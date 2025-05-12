# NYC Restaurant Recommendation Algorithm

<div align="center">
  <img src="images/yelp_logo.svg" alt="Yelp Logo" height="80"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="images/tensorflow_logo.png" alt="TensorFlow Logo" height="80"/>
</div>

## Project Overview
This project implements a sophisticated recommendation system for New York City restaurants using machine learning techniques and data from the Yelp Fusion API. The system combines collaborative filtering with content-based features to provide personalized restaurant recommendations based on user preferences, cuisine types, and neighborhood data.

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

The architecture consists of two parallel "towers" that process user and restaurant data separately, then performs two distinct but complementary tasks: rating prediction and similarity-based retrieval. The combined loss function with configurable weights balances both objectives to provide accurate and personalized restaurant recommendations.

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

## References & Acknowledgments
- TensorFlow TFRS Tutorial: https://github.com/tensorflow/recommenders/blob/main/docs/examples/multitask.ipynb
- Taufik Azri: https://github.com/fickaz/TFRS-on-Retail-Data/blob/main/README.md
- Yelp Public Developer's API: https://docs.developer.yelp.com/docs/getting-started
- Noel Konagai, Yelp API Python Scraper: https://noelkonagai.github.io/Workshops/web_scraping_pt1_yelp/

All restaurant data is scraped directly from the Yelp API in accordance with their terms of use. Data is not used in any way for commercial purposes.

Developed with assistance from ChatGPT 4.0 and GitHub CoPilot
