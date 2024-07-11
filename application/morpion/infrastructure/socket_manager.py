from functools import wraps

from flask import request
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from flask_socketio import SocketIO, join_room, leave_room, disconnect

from application.infrastructure.user import User
from application.morpion.application.game_service import GameService
from application.morpion.domain import board
from application.rooms.domain.room import Room

board = board.Board()
game_service = GameService(board)

rooms = {}
scores = {}
chat_history = {}
user_sessions = {}  # New dictionary to track user sessions


def setup_morpion_sockets(socketio):
    @socketio.on('connect_morpion')
    def on_connect():
        print(f"User connected to Morpion with SID: {request.sid}")
        socketio.emit('connected_morpion',
                      {'message': 'Connected to Morpion game server.'})

    @socketio.on('disconnect_morpion')
    def on_disconnect():
        print(f"User disconnected from Morpion with SID: {request.sid}")
        user_id = next((u_id for u_id, s_id in user_sessions.items() if
                        s_id == request.sid), None)
        if user_id:
            del user_sessions[user_id]
        for room, players in rooms.items():
            for player in players:
                if player['sid'] == request.sid:
                    players.remove(player)
                    print(f"Removed player {request.sid} from room {room}")
                    if len(players) == 0:
                        del rooms[room]
                        print(f"Deleted room {room} as it became empty")
                        if room in chat_history:
                            del chat_history[room]
                    break

    @socketio.on('join_room_morpion')
    def on_join_room(data):
        print("join_room_morpion event received with data:", data)
        room_name = data['room']
        user_id = data['user_id']
        room_id = data['room_id']

        if user_id is None:
            socketio.emit('error_morpion',
                          {'message': 'User ID is required to join a room'},
                          room=request.sid)
            return

        print(f"User {user_id} attempting to join room: {room_name}")

        room = Room.get_room_by_id(room_id)
        print("room INFO: ", room)
        if room is None:
            print("error room does not exist")
            socketio.emit('error_morpion', {'message': 'Room does not exist'},
                          room=request.sid)
            return

        if len(room['players']) < 2 and user_id not in room['players']:
            Room.add_player_to_room(room_id, user_id)
            room = Room.get_room_by_id(
                room_id)  # Refresh room data from the database
            print("room", room)
            rooms[room_id] = room['players']
            print("rooms info :", rooms)
            user_sessions[user_id] = request.sid
            join_room(room_id)
            players = [User().get_one_user(player_id) for player_id in
                       room['players']]
            player_data = [{'username': player['username'],
                            'avatarUrl': player['profile_picture']} for player
                           in players]
            socketio.emit('room_joined_morpion',
                          {'room': room_id, 'players': player_data},
                          room=room_id)
        elif len(room['players']) < 2 and user_id in room['players']:
            print("User rejoining room")
            user_sessions[user_id] = request.sid
            join_room(room_id)
            players = [User().get_one_user(player_id) for player_id in
                       room['players']]
            player_data = [{'username': player['username'],
                            'avatarUrl': player['profile_picture']} for player
                           in players]
            socketio.emit('room_joined_morpion',
                          {'room': room_id, 'players': player_data},
                          room=room_id)
        else:
            print("error room full")
            socketio.emit('error_morpion',
                          {'message': 'Room is full or user already in room'},
                          room=request.sid)

        print(f"User {user_id} joined room {room_id}")

    @socketio.on('start_game')
    def on_start_game(data):
        room = data['room']
        if room in rooms and any(
                player['sid'] == request.sid for player in rooms[room]):
            game_service.start_new_game()
            socketio.emit('game_started',
                          {'message': 'A new Morpion game has started.'},
                          room=room)
            update_game_state(room)

    @socketio.on('make_move')
    def on_make_move(data):
        row = data['row']
        col = data['col']
        player = data['player']
        room = data['room']
        if room in rooms and any(p['sid'] == request.sid for p in rooms[room]):
            success, message = game_service.make_move(player, row, col)
            if success:
                update_game_state(room)
            else:
                socketio.emit('error', {'message': message}, room=request.sid)

    @socketio.on('send_message')
    def on_send_message(data):
        room = data['room']
        message = data['message']
        if room in chat_history:
            chat_history[room].append(message)
            socketio.emit('new_message', message, room=room)

    def update_player_count(room):
        playerCount = len(rooms[room])
        print(f"Room {room} player count: {playerCount}")
        socketio.emit('update_player_count',
                      {'room': room, 'playerCount': playerCount}, room=room)

    def update_game_state(room):
        game_state = game_service.get_game_state()
        socketio.emit('update_state_morpion', game_state, room=room)
        if game_state['winner']:
            scores[room][game_state['winner']] += 1
            socketio.emit('game_over',
                          {'message': f"{game_state['winner']} wins!"},
                          room=room)
            update_scores(room)
        elif game_state['is_full']:
            socketio.emit('game_over_morpion', {'message': "Draw!"}, room=room)

    def update_scores(room):
        socketio.emit('update_scores_morpion', scores[room], room=room)

    def send_chat_history(room):
        if room in chat_history:
            socketio.emit('chat_history_morpion', chat_history[room],
                          room=request.sid)
