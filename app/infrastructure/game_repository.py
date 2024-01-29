from db import db
from bson import ObjectId

class GameRepository:
    def __init__(self):
        self.collection = db.db['games']
        
    def get_all(self):
        games = self.collection.find()
        return [
            {
                '_id': str(game['_id']), 
                'title': game['title'], 
                'genre': game['genre'], 
                'releaseYear': game['releaseYear'], 
                'developer': game['developer'], 
                'rating': game['rating']
                }
            for game in games
        ]