import logging
from typing import Optional, Set
from pymongo import MongoClient
from .game import Game
from .player import Player
from db import db
import pickle

log = logging.getLogger('state')
log.setLevel(logging.INFO)


class State:
    def __init__(self):
        self.rooms_collection = db.rooms  # Correctly access the rooms
        # collection

    def allow_player(self, action: str, room: str, player: Player) -> (
    bool, Optional[str]):
        if not player.name or player.name == '':
            return False, 'name cannot be blank'
        if ' ' in player.name:
            return False, 'name should not contain white spaces'
        if room == '':
            return False, 'room should not be empty'
        players = self.get_players_by_room(room)
        if action == "Join":
            if not players:
                return False, f'cannot join game, room {room} does not exist'
        started = self.get_game_by_room(room) is not None
        if len(players) == Game.MAX_PLAYERS_ALLOWED:
            return False, f"room is full, max {Game.MAX_PLAYERS_ALLOWED} players are supported"
        if started:
            if player not in players:
                return False, f'cannot join, game in the room {room} has already started'
        else:
            if player in players:
                return False, f"name {player.name} is already taken for this room, try a different name"
        return True, None

    def get_game_by_room(self, room: str) -> Optional[Game]:
        room_data = self.rooms_collection.find_one({"room": room})
        if room_data and "game" in room_data:
            return pickle.loads(room_data["game"])
        return None

    def add_game_to_room(self, room: str, game: Game) -> None:
        self.rooms_collection.update_one(
            {"room": room},
            {"$set": {"game": pickle.dumps(game)}},
            upsert=True
        )

    def update_game_in_room(self, room: str, game: Game) -> None:
        self.add_game_to_room(room, game)

    def get_players_by_room(self, room: str) -> Set[Player]:
        room_data = self.rooms_collection.find_one({"room": room})
        if room_data and "players" in room_data:
            return {Player(player_id) for player_id in room_data["players"]}
        return set()

    def add_player_to_room(self, room: str, player: Player) -> None:
        log.info(f"adding player {player} to room {room}")
        self.rooms_collection.update_one(
            {"room": room},
            {"$addToSet": {"players": player.id}},
            upsert=True
        )

    def remove_player_from_room(self, room: str, player: Player) -> None:
        log.info(f"removing player {player} from room {room}")
        self.rooms_collection.update_one(
            {"room": room},
            {"$pull": {"players": player.id}}
        )

    def delete_all(self, room: str) -> None:
        self.rooms_collection.delete_one({"room": room})
