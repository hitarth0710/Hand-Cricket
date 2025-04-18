document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const cameraFeed = document.getElementById('camera-feed');
    const setupControls = document.getElementById('setup-controls');
    const gameControls = document.getElementById('game-controls');
    const batFirstBtn = document.getElementById('bat-first');
    const bowlFirstBtn = document.getElementById('bowl-first');
    const showMoveBtn = document.getElementById('show-move');
    const resetGameBtn = document.getElementById('reset-game');
    const turnIndicator = document.getElementById('turn-indicator');
    const playerScore = document.getElementById('player-score');
    const aiScore = document.getElementById('ai-score');
    const playerWickets = document.getElementById('player-wickets');
    const aiWickets = document.getElementById('ai-wickets');
    const playerMoveDisplay = document.getElementById('player-move-display');
    const aiMoveDisplay = document.getElementById('ai-move-display');
    const resultMessage = document.getElementById('result-message');
    const targetContainer = document.getElementById('target-container');
    const targetScore = document.getElementById('target-score');
    const timerCircle = document.getElementById('timer-circle');
    

    // Socket connection
    console.log("Initializing socket connection...");
    const socket = io();
    
    // Game state
    let gameActive = false;
    let countdown = null;
    let lastDetectedMove = null;
    
    // Connect to socket
    socket.on('connect', function() {
        console.log('Connected to server');
    });

        
    socket.on('connect_error', function(error) {
        console.error('Connection error:', error);
    });
    
    socket.on('camera_error', function(data) {
        console.error('Camera error:', data.message);
        // Show error message to user
        alert('Camera error: ' + data.message + '\nPlease make sure your camera is connected and not used by another application.');
    });

    // Handle camera updates
    socket.on('camera_update', function(data) {
        cameraFeed.src = 'data:image/jpeg;base64,' + data.frame;
        lastDetectedMove = data.move;
    });
    
    // Handle game updates
    socket.on('game_update', function(data) {
        console.log('Game update:', data);
        
        // Update turn indicator
        if (data.player_turn === 'bat') {
            turnIndicator.textContent = 'Your Turn: Batting';
            turnIndicator.className = 'text-success';
        } else {
            turnIndicator.textContent = 'Your Turn: Bowling';
            turnIndicator.className = 'text-info';
        }
        
        // Update scores and wickets
        playerScore.textContent = data.scores[1];
        aiScore.textContent = data.scores[0];
        playerWickets.textContent = data.player_wickets;
        aiWickets.textContent = data.ai_wickets;
        
        // Show target if available
        if (data.target_score !== null) {
            targetContainer.classList.remove('hidden');
            targetScore.textContent = data.target_score + 1;
        }
        
        // Show moves if available
        if (data.player_move !== null && data.ai_move !== null) {
            playerMoveDisplay.textContent = data.player_move;
            aiMoveDisplay.textContent = data.ai_move;
            
            // Show result message
            if (data.result === 'out') {
                resultMessage.textContent = 'OUT! You lost a wicket!';
                resultMessage.className = 'game-result text-danger';
            } else if (data.result === 'scored') {
                resultMessage.textContent = `You scored ${data.player_move} runs!`;
                resultMessage.className = 'game-result text-success';
            } else if (data.result === 'wicket') {
                resultMessage.textContent = 'WICKET! You got the AI out!';
                resultMessage.className = 'game-result text-success';
            } else if (data.result === 'ai_scored') {
                resultMessage.textContent = `AI scored ${data.ai_move} runs!`;
                resultMessage.className = 'game-result text-danger';
            }
        }
        
        // Handle game over
        if (data.game_over) {
            let winnerMessage = '';
            if (data.winner === 'Player') {
                winnerMessage = '🏆 You Win!';
                resultMessage.className = 'game-result text-success';
            } else if (data.winner === 'AI') {
                winnerMessage = '🤖 AI Wins!';
                resultMessage.className = 'game-result text-danger';
            } else {
                winnerMessage = '🤝 It\'s a Tie!';
                resultMessage.className = 'game-result text-warning';
            }
            resultMessage.textContent = winnerMessage;
        }
        
        // Show game controls
        setupControls.classList.add('hidden');
        gameControls.classList.remove('hidden');
    });
    
    // Handle game reset
    socket.on('game_reset', function() {
        setupControls.classList.remove('hidden');
        gameControls.classList.add('hidden');
        playerScore.textContent = '0';
        aiScore.textContent = '0';
        playerWickets.textContent = '5';
        aiWickets.textContent = '5';
        playerMoveDisplay.textContent = '-';
        aiMoveDisplay.textContent = '-';
        resultMessage.textContent = '';
        targetContainer.classList.add('hidden');
    });
    
    // Button event handlers
    batFirstBtn.addEventListener('click', function() {
        socket.emit('select_turn', { turn: 'bat' });
    });
    
    bowlFirstBtn.addEventListener('click', function() {
        socket.emit('select_turn', { turn: 'bowl' });
    });
    
    showMoveBtn.addEventListener('click', function() {
        // Disable button during countdown
        if (countdown !== null) return;
        
        // Start countdown
        let count = 3;
        timerCircle.textContent = count;
        timerCircle.classList.remove('hidden');
        
        countdown = setInterval(function() {
            count--;
            timerCircle.textContent = count;
            
            if (count <= 0) {
                clearInterval(countdown);
                countdown = null;
                timerCircle.classList.add('hidden');
                
                // Submit the detected move
                socket.emit('process_move', { move: lastDetectedMove || 0 });
            }
        }, 1000);
    });
    
    resetGameBtn.addEventListener('click', function() {
        socket.emit('reset_game');
    });
});