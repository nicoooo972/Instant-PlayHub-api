from flask import request
from flask_socketio import SocketIO, join_room, leave_room
from breakout.application.game_service import GameService

game_service = GameService()
rooms = {}
user_sessions = {}

def setup_breakout_sockets(socketio):
    @socketio.on('connect')
    def on_connect():
        print(f"User connected to Breakout with SID: {request.sid}")
        socketio.emit('connected', {'message': 'Connected to Breakout game server.'})

    @socketio.on('disconnect')
    def on_disconnect():
        print(f"User disconnected from Breakout with SID: {request.sid}")
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
                    break
        update_rooms()

    @socketio.on('create_room')
    def on_create_room(data):
        room = data['room']
        user_id = data.get('user_id')
        if user_id is None:
            socketio.emit('error', {'message': 'User ID is required to create a room'}, room=request.sid)
            return

        print(f"Creating room: {room}")
        if room not in rooms:
            rooms[room] = []
            user_sessions[user_id] = request.sid
            socketio.emit('room_created', {'room': room}, room=request.sid)
            update_rooms()
        else:
            socketio.emit('error', {'message': 'Room already exists'}, room=request.sid)

    @socketio.on('join_room')
    def on_join_room(data):
        room = data['room']
        user_id = data.get('user_id')
        if user_id is None:
            socketio.emit('error', {'message': 'User ID is required to join a room'}, room=request.sid)
            return

        print(f"User {user_id} with SID {request.sid} attempting to join room: {room}")

        if room not in rooms:
            socketio.emit('error', {'message': 'Room does not exist'}, room=request.sid)
        else:
            existing_player = next((player for player in rooms[room] if player['user_id'] == user_id), None)
            if existing_player:
                existing_player['sid'] = request.sid
                user_sessions[user_id] = request.sid
                join_room(room)
                socketio.emit('room_joined', {'room': room, 'playerCount': len(rooms[room])}, room=request.sid)
                print(f"User {user_id} reconnected to room {room}")
            elif len(rooms[room]) < 2:
                rooms[room].append({'sid': request.sid, 'user_id': user_id})
                user_sessions[user_id] = request.sid
                join_room(room)
                socketio.emit('room_joined', {'room': room, 'playerCount': len(rooms[room])}, room=request.sid)
                print(f"User {user_id} joined room {room}")
            else:
                socketio.emit('error', {'message': 'Room is full'}, room=request.sid)
                print(f"User {request.sid} could not join room {room} because it is full")

    @socketio.on('start_game')
    def on_start_game(data):
        room = data['room']
        if room in rooms and any(player['sid'] == request.sid for player in rooms[room]):
            game_service.start_new_game()
            socketio.emit('game_started', {'message': 'A new Breakout game has started.'}, room=room)
            update_game_state(room)

    @socketio.on('make_move')
    def on_make_move(data):
        player = data['player']
        direction = data['direction']
        room = data['room']
        if room in rooms and any(p['sid'] == request.sid for p in rooms[room]):
            game_service.make_move(player, direction)
            update_game_state(room)

    @socketio.on('update_ball')
    def on_update_ball(data):
        room = data['room']
        if room in rooms:
            game_service.update_ball()
            update_game_state(room)

    def update_rooms():
        print(f"Current rooms: {rooms}")
        socketio.emit('update_rooms', rooms)

    def update_game_state(room):
        game_state = game_service.get_game_state()
        socketio.emit('update_state', game_state, room=room)
