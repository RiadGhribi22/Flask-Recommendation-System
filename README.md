# Flask Recommendation System

## Description
This is a recommendation system built using Flask, MongoDB, and scikit-learn. It calculates user similarity based 
on video interactions and provides personalized video recommendations.

## Features
- User-based collaborative filtering
- Cosine similarity for recommendations
- MongoDB for data storage
- REST API for receiving user data and returning recommendations

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- MongoDB
- pip (Python package manager)

### Steps to Run the Project
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/RiadGhribi22/Flask-Recommendation-System.git
   cd your-repo-name
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r Libraries.txt
   ```
3. **Start MongoDB:**
   ```bash
   mongod --dbpath /path/to/your/mongodb/data
   ```
4. **Run the Flask App:**
   ```bash
   python recommendation.py
   ```
5. The server will start on `http://localhost:5000`

## API Endpoints
### `POST /data`
- **Description:** Receives user interaction data and returns recommended videos.
- **Request Body:**
  ```json
  {
    "id": "user123"
  }
  ```
- **Response:**
  ```json
  {
    "message": "recommended videos are",
    "recommended_videos": ["video1", "video2", "video3"]
  }
  ```

## Technologies Used
- **Backend:** Flask, MongoDB, scikit-learn
- **Database:** MongoDB
- **Tools:** Postman, Git, VS Code

## Deployment
To deploy with Gunicorn:
```bash
  gunicorn -w 4 recommendation:app -b :5000
```



