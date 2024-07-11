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
user_sessions = {}

def setup_morpion_sockets(socketio):
    @socketio.on('connect_morpion')
    def on_connect():
        print(f"User connected to Morpion with SID: {request.sid}")
        socketio.emit('connected_morpion', {'message': 'Connected to Morpion game server.'})

    @socketio.on('disconnect_morpion')
    def on_disconnect():
        print(f"User disconnected from Morpion with SID: {request.sid}")
        user_id = next((u_id for u_id, s_id in user_sessions.items() if s_id == request.sid), None)
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
            socketio.emit('error_morpion', {'message': 'User ID is required to join a room'}, room=request.sid)
            return

        print(f"User {user_id} attempting to join room: {room_name}")

        room = Room.get_room_by_id(room_id)
        print("room INFO: ", room)
        if room is None:
            print("error room does not exist")
            socketio.emit('error_morpion', {'message': 'Room does not exist'}, room=request.sid)
            return

        if room_id not in rooms:
            rooms[room_id] = []

        if len(room['players']) < 2 and user_id not in room['players']:
            Room.add_player_to_room(room_id, user_id)
            room = Room.get_room_by_id(room_id)  # Refresh room data from the database
            print("room", room)
            user_sessions[user_id] = request.sid
            symbol = 'X' if len(rooms[room_id]) == 0 else 'O'
            rooms[room_id].append({'user_id': user_id, 'sid': request.sid, 'symbol': symbol})
            join_room(room_id)
            players = [User().get_one_user(player_id) for player_id in room['players']]
            player_data = [{'username': player['username'], 'avatarUrl': player['profile_picture'], 'symbol': symbol} for player, symbol in zip(players, ['X', 'O'])]
            socketio.emit('room_joined_morpion', {'room': room_id, 'players': player_data}, room=room_id)
            if len(room['players']) == 2:
                socketio.emit('start_game_morpion', {'room': room_id}, room=room_id)
        else:
            socketio.emit('error_morpion', {'message': 'Room is full or user already in room'}, room=request.sid)

    @socketio.on('start_game_morpion')
    def on_start_game(data):
        room_id = data['room']
        if room_id in rooms and any(player['sid'] == request.sid for player in rooms[room_id]):
            if len(rooms[room_id]) == 2:
                game_service.start_new_game()
                socketio.emit('game_started_morpion', {'message': 'A new Morpion game has started.'}, room=room_id)
                print("Game started in room", room_id)
                update_game_state(room_id)
            else:
                socketio.emit('error_morpion', {'message': 'Two players are required to start the game.'}, room=request.sid)
                print("Error: Two players are required to start the game.")

    @socketio.on('make_move_morpion')
    def on_make_move(data):
        print("make_move_morpion event received with data:", data)
        row = data['row']
        col = data['col']
        player = data['player']
        room = data['room']
        if room in rooms and any(p['sid'] == request.sid for p in rooms[room]):
            game_state = game_service.get_game_state()
            current_player_sid = next((p['sid'] for p in rooms[room] if p['symbol'] == game_state['current_player']), None)
            if current_player_sid != request.sid:
                socketio.emit('error_morpion', {'message': "It's not your turn!"}, room=request.sid)
                print("Error: It's not your turn!")
                return
            
            success, message = game_service.make_move(player, row, col)
            if success:
                update_game_state(room)
            else:
                socketio.emit('error_morpion', {'message': message}, room=request.sid)
                print(f"Error: {message}")


    @socketio.on('send_message_morpion')
    def on_send_message(data):
        room = data['room']
        message = data['message']
        user_id = next((u_id for u_id, s_id in user_sessions.items() if s_id == request.sid), None)
        if user_id:
            user = User().get_one_user(user_id)
            socketio.emit('new_message_morpion', {'user': user['username'], 'message': message}, room=room)

    def update_game_state(room):
        game_state = game_service.get_game_state()
        print("Updating game state for room: ", room, game_state)
        current_player = next((p for p in rooms[room] if p['symbol'] == game_state['current_player']), None)
        socketio.emit('update_state_morpion', {**game_state, 'current_player_info': current_player}, room=room)
        if game_state['winner']:
            socketio.emit('game_over_morpion', {'message': f"{game_state['winner']} wins!"}, room=room)
        elif game_state['is_full']:
            socketio.emit('game_over_morpion', {'message': "Draw!"}, room=room)

