from app import create_app, socketio
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if database file exists
db_path = 'instance/hand_cricket.db'
if not os.path.exists(db_path):
    logger.warning(f"Database file not found at {db_path}")
    if not os.path.exists('instance'):
        os.makedirs('instance')
        logger.info("Created instance directory")

app = create_app()

if __name__ == "__main__":
    logger.info("Starting Hand Cricket application...")
    try:
        # Use a different host if needed
        # Default is only accessible from localhost
        socketio.run(app, debug=True)
    except Exception as e:
        logger.error(f"Error starting application: {e}")