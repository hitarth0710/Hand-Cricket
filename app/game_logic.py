import random
import logging

logger = logging.getLogger(__name__)

class HandCricketGame:
    def __init__(self):
        logger.info("Initializing game")
        self.reset_game()
    
    def reset_game(self):
        logger.debug("Resetting game state")
        self.player_turn = None
        self.player_wickets = 5
        self.ai_wickets = 5
        self.scores = [0, 0]  # [AI, Player]
        self.target_score = None
        self.ai_move = 0
        self.player_move = None
        self.game_state = "setup"  # setup, playing, finished
        self.winner = None
    
    def set_player_turn(self, turn):
        logger.debug(f"Setting player turn to {turn}")
        self.player_turn = turn
        self.game_state = "playing"
        return {"status": "success", "turn": turn, "player_turn": turn, "player_wickets": self.player_wickets, 
                "ai_wickets": self.ai_wickets, "scores": self.scores, "target_score": self.target_score}
    
    def process_move(self, player_move):
        logger.debug(f"Processing move: player={player_move}")
        self.player_move = player_move
        self.ai_move = random.randint(0, 5)
        logger.debug(f"AI move: {self.ai_move}")
        
        # Game Logic
        if self.player_turn == "bat":
            if self.player_move == self.ai_move:
                self.player_wickets -= 1
                result = "out"
                logger.debug("Player out!")
            else:
                self.scores[1] += self.player_move
                result = "scored"
                logger.debug(f"Player scored {self.player_move}")

            if self.player_wickets == 0:
                logger.debug(f"Player all out! Score: {self.scores[1]}")
                self.target_score = self.scores[1]
                self.player_turn = "bowl"
                
        elif self.player_turn == "bowl":
            if self.player_move == self.ai_move:
                self.ai_wickets -= 1
                result = "wicket"
                logger.debug("AI out!")
            else:
                self.scores[0] += self.ai_move
                result = "ai_scored"
                logger.debug(f"AI scored {self.ai_move}")

            if self.ai_wickets == 0:
                logger.debug(f"AI all out! Score: {self.scores[0]}")
                self.target_score = self.scores[0]
                self.player_turn = "bat"
        
        # Check if game is finished
        game_over = self.check_game_over()
        
        return {
            "player_move": self.player_move,
            "ai_move": self.ai_move,
            "player_wickets": self.player_wickets,
            "ai_wickets": self.ai_wickets,
            "scores": self.scores,
            "target_score": self.target_score,
            "player_turn": self.player_turn,
            "result": result,
            "game_over": game_over,
            "winner": self.winner
        }
    
    def check_game_over(self):
        # Check if second batting team has won immediately
        if self.target_score is not None:
            if self.player_turn == "bat" and self.scores[1] > self.target_score:
                logger.debug("Player wins!")
                self.winner = "Player"
                self.game_state = "finished"
                return True
            elif self.player_turn == "bowl" and self.scores[0] > self.target_score:
                logger.debug("AI wins!")
                self.winner = "AI"
                self.game_state = "finished"
                return True

        # If both teams completed innings, declare winner
        if self.player_wickets == 0 and self.ai_wickets == 0:
            if self.scores[0] > self.scores[1]:
                logger.debug("AI wins!")
                self.winner = "AI"
            elif self.scores[1] > self.scores[0]:
                logger.debug("Player wins!")
                self.winner = "Player"
            else:
                logger.debug("It's a tie!")
                self.winner = "Tie"
            self.game_state = "finished"
            return True
        
        return False