



from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import pandas as pd

app = Flask(__name__)

# Setup MongoDB connection
client = MongoClient("")# Specify url of your mongodb 
db = client['']  # Specify the name of your database
collection = db['']  # Specify the name of your data collection
collection_videos=db['']




#----------------------------------------------------------------------
def transform_data():
    transformed = {}
    data = list(collection.find({}))

    # Example function to get video IDs by category

    for entry in data:
        user_id = entry['userId']
        interactions = entry['userIntercation']
        for interaction in interactions:
            video_id = interaction['videoId']
            if user_id not in transformed:
                 transformed[user_id] = {}
            # Compute the rating numerically based on like/dislike and comments
            rating = interaction['percentWatching']
            if interaction['like']:
                    rating = rating + 1
                    if interaction.get('comments'):
                        rating = rating + 0.5
            elif interaction['dislike']:
                    rating = rating - 1
                    if interaction.get('comments'):
                        rating = rating - 0.5
 
                # Add weight to comments (assuming 0.5 weight)
            transformed[user_id][video_id] = {'rating': rating}

    # Convert transformed dictionary to DataFrame
    df = pd.DataFrame.from_dict(transformed, orient='index')

    # Set index names
    df.index.name = 'userId'
    df.columns.name = 'videoId'

    # Flatten nested dictionary within DataFrame
    df = df.stack().apply(pd.Series)
    pivot_df = df.pivot_table(index='userId', columns='videoId', values='rating', fill_value=0)

    # Print the DataFrame
    print(pivot_df)

    return pivot_df


#----------------------------------------------------------------------
def calculate_similarity_matrix(df):
    


    # Extract ratings from the pivot table
    ratings = df.values


    # Compute cosine similarity matrix between users based on ratings
    similarity_matrix = cosine_similarity(ratings)



    
    print('-------------------------------------------')
    print(similarity_matrix)
    print('-------------------------------------------')

    
    return similarity_matrix

#---------------------------------------------------------------------
def select_neighborhood(df, similarity_matrix, target_user, k):
    # Find the index of the target user in the first level of the multi-index
    try:
        target_user_index = df.index.get_level_values('userId').tolist().index(target_user)
    except ValueError:
        print("Target user not found in the list of users.")
        return None

    print('----------------------df.index.tolist--------------------------')
    print(df.index.get_level_values('userId').tolist())
    print('------------------------------------------------------')
    print("target user index:", target_user_index)

    # Get the similarity scores of the target user with all other users
    target_user_similarity = similarity_matrix[target_user_index]

    # Sort the similarity scores in descending order and get indices of top k similar users
    similar_users_indices = (-target_user_similarity).argsort()[1:k + 1]  # Exclude target user itself

    print('similar users indices:', similar_users_indices)

    return similar_users_indices
#--------------------------------------------------------------------
def predict_ratings(target_user, neighborhood, transformed):
    # Initialize dictionary to store aggregated ratings from the target user and the neighborhood
    neighborhood_ratings = {}

    # Get the set of videos the target user has interacted with
    target_interacted_videos = set()
    if target_user in transformed.index:
        target_ratings = transformed.loc[target_user]
        
        for video_id, rating in target_ratings.items():
            print('-----------------------------------------------')
            print("video_id : ",video_id," rating : ",rating)
            print('-----------------------------------------------')
            if(rating != 0):
                target_interacted_videos.add(video_id)



    print("target interacted videos : ",target_interacted_videos)
    # Aggregate ratings from the neighborhood users
    for neighbor_index in neighborhood:
        # Access user ID from the index of transformed DataFrame based on neighborhood index
        neighbor_user = transformed.index[neighbor_index]
        print('neighbor user : ',neighbor_user)

        # Check if the neighbor user is in the index
        if neighbor_user in transformed.index:
            neighbor_ratings = transformed.loc[neighbor_user]
            print('neighbor_ratings user : ',neighbor_ratings)

            for video_id, rating in neighbor_ratings.items():
                # Check if the video has been interacted with by the target user
                if video_id not in target_interacted_videos and rating != 0:

                    if video_id not in target_interacted_videos:
                        if video_id not in neighborhood_ratings :
                            neighborhood_ratings[video_id] = []
                    neighborhood_ratings[video_id].append(rating)
                    print('------------------------------------------------')
                    print('neighborhood ratings : ',neighborhood_ratings)
                    print('------------------------------------------------')


    # Predict ratings for unrated items by averaging neighborhood ratings
    predicted_ratings = {}
    for video_id, ratings in neighborhood_ratings.items():
        print("len(ratings) : ",len(ratings))
        if len(ratings) > 0:  # Check if there are ratings for the video
            predicted_ratings[video_id] = sum(ratings) / len(ratings)

    print('predicted ratings:', predicted_ratings)
    return predicted_ratings

#------------------------------------------------------------------
def generate_recommendations(predicted_ratings, n_recommendations):
    # Sort the predicted ratings in descending order and select the top n_recommendations
    recommended_videos = sorted(predicted_ratings.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
    print('recomended videos : ',recommended_videos)
    # Extract video IDs from the recommended videos
    recommended_video_ids = [video_id for video_id, rating in recommended_videos]

    
    return recommended_video_ids

#----------------------------------------------------------------------

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    
    # Transform the data and perform recommendation
    df = transform_data()  # Assuming this function returns the DataFrame with ratings and comments
    similarity_matrix = calculate_similarity_matrix(df)  # Assuming this function calculates the similarity matrix
    neighborhood = select_neighborhood(df,similarity_matrix, data['id'], k=3)  # Assuming k=5 for the neighborhood size
    predicted_ratings = predict_ratings(data['id'], neighborhood, df)  # Assuming this function predicts ratings
    recommended_video_ids = generate_recommendations(predicted_ratings, n_recommendations=20)  # Assuming n_recommendations=10
    
    # Print the value of the 'message' key
    if 'id' in data:
        print("Message received from Node.js:", data['id'])
        
        # Construct a query filter for finding documents with matching message
        query = { 'userId': data['id'] }
        
        # Find documents in the collection that match the query filter
        obj = collection.find_one(query)
        
        # Prepare response JSON with recommended video IDs
        response_data = {
            'message': 'recommended videos are ',
            'recommended_videos': recommended_video_ids
        } if obj else {
            'message': ' not found'
        }
    else:
        response_data = {
            'message': 'No message received'
        }

    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(port=5000)

#gunicorn -w 4 recommendation:app -b :5000
