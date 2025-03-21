import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(maxHands=1)

timer = 0
stateResult = False
startGame = False
playerTurn = None  # "bat" or "bowl"
playerWickets = 1
aiWickets = 1
scores = [0, 0]  # [AI, Player]
targetScore = None  # Target score to be chased

# Function to display final score and winner
def display_final_score(winner):
    print(f"Game Over! AI: {scores[0]} | Player: {scores[1]}")
    cv2.putText(imgBG, f"Final Score: AI {scores[0]} - Player {scores[1]}", (500, 500), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 5)
    cv2.putText(imgBG, winner, (500, 600), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 5)
    cv2.imshow("BG", imgBG)
    cv2.waitKey(3000)
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Game Start - Player Chooses Batting or Bowling
print("Welcome to Hand Cricket!")
while True:
    try:
        choice = int(input("Enter 1 to Bat or 2 to Bowl: "))
        if choice == 1:
            playerTurn = "bat"
            print("You are Batting first!")
            break
        elif choice == 2:
            playerTurn = "bowl"
            print("You are Bowling first!")
            break
        else:
            print("Invalid choice! Enter 1 or 2.")
    except ValueError:
        print("Invalid input! Enter a number.")

while True:
    imgBG = cv2.imread("Resources/BG.png")
    success, img = cap.read()

    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Find Hands
    hands, img = detector.findHands(imgScaled)

    if startGame:
        if stateResult is False:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0

                if hands:
                    playerMove = None
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)

                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 0
                    elif fingers == [0, 1, 0, 0, 0]:
                        playerMove = 1
                    elif fingers == [0, 1, 1, 0, 0]:
                        playerMove = 2
                    elif fingers == [0, 1, 1, 1, 0]:
                        playerMove = 3
                    elif fingers == [0, 1, 1, 1, 1]:
                        playerMove = 4
                    elif fingers == [1, 1, 1, 1, 1]:
                        playerMove = 5

                    aiMove = random.randint(0, 5)
                    imgAI = cv2.imread(f'Resources/{aiMove}.png', cv2.IMREAD_UNCHANGED)
                    imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                    # Game Logic
                    if playerTurn == "bat":
                        if playerMove == aiMove:
                            playerWickets -= 1
                        else:
                            scores[1] += playerMove

                        if playerWickets == 0:
                            print(f"All out! Player Score: {scores[1]}")
                            targetScore = scores[1]  # Set target score
                            playerTurn = "bowl"
                            time.sleep(2)

                    elif playerTurn == "bowl":
                        if playerMove == aiMove:
                            aiWickets -= 1
                        else:
                            scores[0] += aiMove

                        if aiWickets == 0:
                            print(f"AI All out! AI Score: {scores[0]}")
                            targetScore = scores[0]  # Set target score
                            playerTurn = "bat"
                            time.sleep(2)

    imgBG[234:654, 795:1195] = imgScaled

    if stateResult:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

    # Scoreboard UI
    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # Wickets Display
    cv2.putText(imgBG, f"Player Wickets: {playerWickets}", (100, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)  # Left side
    cv2.putText(imgBG, f"AI Wickets: {aiWickets}", (700, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)  # Adjusted left

    # Display Target Score if available
    if targetScore is not None:
        cv2.putText(imgBG, f"Target: {targetScore+1}", (500, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 0), 5)

    cv2.imshow("BG", imgBG)

    key = cv2.waitKey(1)
    if key == ord('s'):
        # **Check if second batting team has won immediately**
        if targetScore is not None:  
            if playerTurn == "bat" and scores[1] > targetScore:  
                display_final_score("🏆 Player Wins!")  
            elif playerTurn == "bowl" and scores[0] > targetScore:  
                display_final_score("🏆 AI Wins!")  

        # If both teams completed innings, declare winner
        if playerWickets == 0 and aiWickets == 0:
            if scores[0] > scores[1]:  
                display_final_score("🏆 AI Wins!")
            elif scores[1] > scores[0]:  
                display_final_score("🏆 Player Wins!")
            else:  
                display_final_score("🤝 It's a Tie!")

        startGame = True
        initialTime = time.time()
        stateResult = False
