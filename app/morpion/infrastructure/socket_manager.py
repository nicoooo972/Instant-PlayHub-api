from flask import request
from flask_socketio import SocketIO, join_room, leave_room
from app.morpion.application.game_service import GameService
from app.morpion.domain import board

board = board.Board()
game_service = GameService(board)

rooms = {}
scores = {}
chat_history = {}
user_sessions = {}  # New dictionary to track user sessions


def setup_morpion_sockets(socketio):
    @socketio.on('connect')
    def on_connect():
        print(f"User connected to Morpion with SID: {request.sid} gros pd")
        socketio.emit('connected',
                      {'message': 'Connected to Morpion game server.'})

    @socketio.on('disconnect')
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
        update_rooms()

    @socketio.on('create_room')
    def on_create_room(data):
        room = data['room']
        user_id = data.get('user_id', None)
        if user_id is None:
            socketio.emit('error',
                          {'message': 'User ID is required to create a room'},
                          room=request.sid)
            return

        print(f"Creating room: {room}")
        if room not in rooms:
            rooms[room] = []
            chat_history[room] = []
            user_sessions[user_id] = request.sid
            socketio.emit('room_created', {'room': room}, room=request.sid)
            update_rooms()
        else:
            socketio.emit('error', {'message': 'Room already exists'},
                          room=request.sid)

    @socketio.on('join_room')
    def on_join_room(data):
        room = data['room']
        user_id = data.get('user_id', None)
        if user_id is None:
            socketio.emit('error',
                          {'message': 'User ID is required to join a room'},
                          room=request.sid)
            return

        print(
            f"User {user_id} with SID {request.sid} attempting to join room: {room}")

        if room not in rooms:
            socketio.emit('error', {'message': 'Room does not exist'},
                          room=request.sid)
        else:
            # Check if user is already in the room with a different SID
            existing_player = next((player for player in rooms[room] if
                                    player['user_id'] == user_id), None)
            if existing_player:
                existing_player['sid'] = request.sid  # Update SID
                user_sessions[user_id] = request.sid
                join_room(room)
                socketio.emit('room_joined',
                              {'room': room, 'playerCount': len(rooms[room]),
                               'symbol': existing_player['symbol']},
                              room=request.sid)
                print(
                    f"User {user_id} reconnected to room {room} with symbol {existing_player['symbol']}")
                send_chat_history(room)
            elif len(rooms[room]) < 2:
                symbol = 'X' if len(rooms[room]) == 0 else 'O'
                rooms[room].append(
                    {'sid': request.sid, 'symbol': symbol, 'user_id': user_id})
                user_sessions[user_id] = request.sid
                join_room(room)
                socketio.emit('room_joined',
                              {'room': room, 'playerCount': len(rooms[room]),
                               'symbol': symbol}, room=request.sid)
                print(
                    f"User {user_id} joined room {room} with symbol {symbol}")
                if room not in scores:
                    scores[room] = {'X': 0, 'O': 0}
                update_player_count(room)
                send_chat_history(room)
            else:
                socketio.emit('error', {'message': 'Room is full'},
                              room=request.sid)
                print(
                    f"User {request.sid} could not join room {room} because it is full")

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

    @socketio.on('send_message_morpion')
    def on_send_message(data):
        print("DATA DE MORPION : ", data)
        room = data['room']
        message = data['message']
        if room in chat_history:
            chat_history[room].append(message)
            socketio.emit('new_message', message, room=room)

    @socketio.on('get_rooms')
    def on_get_rooms():
        update_rooms()

    def update_rooms():
        print(f"Current rooms: {rooms}")
        socketio.emit('update_rooms', rooms)

    def update_player_count(room):
        playerCount = len(rooms[room])
        print(f"Room {room} player count: {playerCount}")
        socketio.emit('update_player_count',
                      {'room': room, 'playerCount': playerCount}, room=room)

    def update_game_state(room):
        game_state = game_service.get_game_state()
        socketio.emit('update_state', game_state, room=room)
        if game_state['winner']:
            scores[room][game_state['winner']] += 1
            socketio.emit('game_over',
                          {'message': f"{game_state['winner']} wins!"},
                          room=room)
            update_scores(room)
        elif game_state['is_full']:
            socketio.emit('game_over', {'message': "Draw!"}, room=room)

    def update_scores(room):
        socketio.emit('update_scores', scores[room], room=room)

    def send_chat_history(room):
        if room in chat_history:
            socketio.emit('chat_history', chat_history[room], room=request.sid)
