import uuid
from db import db

class Score:
    def create_score(self, user_id, game_type):
        score = {
            "_id": uuid.uuid4().hex,
            "user_id": user_id,
            "game_type": game_type,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "score": 0
        }
        return db.scores.insert_one(score)

    def get_score_by_user_and_game(self, user_id, game_type):
        return db.scores.find_one({"user_id": user_id, "game_type": game_type})

    def get_scores_by_game(self, game_type):
        return list(db.scores.find({"game_type": game_type}))

    def get_scores_by_user(self, user_id):
        return list(db.scores.find({"user_id": user_id}))

    def update_score(self, user_id, game_type, result):
        score = self.get_score_by_user_and_game(user_id, game_type)
        if not score:
            self.create_score(user_id, game_type)
            score = self.get_score_by_user_and_game(user_id, game_type)
        
        if result == "win":
            db.scores.update_one({"_id": score["_id"]}, {"$inc": {"wins": 1, "score": 100}})
        elif result == "draw":
            db.scores.update_one({"_id": score["_id"]}, {"$inc": {"draws": 1, "score": 50}})
        elif result == "loss":
            db.scores.update_one({"_id": score["_id"]}, {"$inc": {"losses": 1}})

score_model = Score()
