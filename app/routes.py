from flask import Blueprint, render_template, jsonify, session
from app import socketio
from app.camera import Camera
from app.game_logic import HandCricketGame
import time
import threading
import logging
from flask_login import login_required, current_user
from flask_socketio import disconnect

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Game and camera instances
game = HandCricketGame()
camera = None
camera_thread = None
camera_active = False

def camera_loop():
    global camera, camera_active, game
    logger.debug("Camera loop started")
    while camera_active:
        try:
            frame, move = camera.get_frame()
            if frame:
                socketio.emit('camera_update', {'frame': frame, 'move': move})
        except Exception as e:
            logger.error(f"Error in camera loop: {e}")
        time.sleep(0.1)

# Add this function to check authentication in Socket.IO connections
def authenticated_only(f):
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
            return
        else:
            return f(*args, **kwargs)
    return wrapped
    

@main_bp.route('/')
def index():
    logger.debug("Rendering index page")
    game.reset_game()
    return render_template('index.html')

@main_bp.route('/game')
@login_required
def game_page():
    logger.debug("Rendering game page")
    return render_template('game.html')

@socketio.on('connect')
# Temporarily comment out this decorator to test if it's causing issues
# @authenticated_only
def handle_connect():
    global camera, camera_thread, camera_active
    
    try:
        logger.debug("Client connected")
        # Add this logging to see if we reach this point
        logger.debug(f"Authentication status: {current_user.is_authenticated}")
        
        if camera is None:
            logger.debug("Initializing camera")
            try:
                camera = Camera()
                logger.debug("Camera initialized successfully")
            except Exception as camera_error:
                logger.error(f"Camera initialization failed: {camera_error}")
                # Send error to client
                socketio.emit('camera_error', {'message': str(camera_error)})
        
        if not camera_active and camera is not None:
            camera_active = True
            camera_thread = threading.Thread(target=camera_loop)
            camera_thread.daemon = True
            camera_thread.start()
            logger.debug("Camera thread started")
    except Exception as e:
        logger.error(f"Error in connect handler: {e}")
        import traceback
        logger.error(traceback.format_exc())

@socketio.on('disconnect')
def handle_disconnect():
    global camera, camera_active
    logger.debug("Client disconnected")
    camera_active = False
    if camera:
        camera.release()
        camera = None

@socketio.on('select_turn')
def handle_select_turn(data):
    logger.debug(f"Turn selected: {data['turn']}")
    result = game.set_player_turn(data['turn'])
    socketio.emit('game_update', result)

@socketio.on('process_move')
def handle_process_move(data):
    logger.debug(f"Processing move: {data['move']}")
    player_move = data['move']
    result = game.process_move(player_move)
    socketio.emit('game_update', result)

@socketio.on('reset_game')
def handle_reset_game():
    logger.debug("Game reset")
    game.reset_game()
    socketio.emit('game_reset')