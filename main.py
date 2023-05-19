import numpy as np
import pygame
import sys
import math
import random
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import time

BLUE = (255, 255, 0)
BLACK = (0,0,0)
RED = (255, 0, 0)
YELLOW = (0, 0, 255)

ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0  # Added
AI = 1

minimax_scores_g = []
minimax_ab_scores_g = []

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True

# Define our screen size
SQUARESIZE = 100

# Define width and height of board
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

# Initialize pygame
pygame.init()
size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (
            int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (
                int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (
                int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # Score positive diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Score negative diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, maximizing_player):
    valid_locations = get_valid_locations(board)
    terminal_node = is_terminal_node(board)

    if depth == 0 or terminal_node:
        if terminal_node:
            if winning_move(board, 2):
                return (None, 100000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, 2))

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 2)
            new_score = minimax(temp_board, depth - 1, False)[1]
            if new_score > value:
                value = new_score
                column = col
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 1)
            new_score = minimax(temp_board, depth - 1, True)[1]
            if new_score < value:
                value = new_score
                column = col
        return column, value

#################################################################
def minimax_ab(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    terminal_node = is_terminal_node(board)

    if depth == 0 or terminal_node:
        if terminal_node:
            if winning_move(board, 2):
                return (None, 100000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, 2))

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 2)
            new_score = minimax_ab(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 1)
            new_score = minimax_ab(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

board = create_board()
print_board(board)
game_over = False
turn = 0

# Calling function draw_board again
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("Montserrat", 75)

#start_time = time.time()

def run_game(algorithm, difficulty):
    # Your game logic here

    board = create_board()

    # Game loop
    game_over = False
    turn = random.choice([1, 2])
    start_time = time.time()
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # Player 1 AI's turn
        if turn == PLAYER:
            if algorithm=="Minimax":
                move_start_time = time.time()
                #minimax_scores_g.append(elapsed_time)
                if difficulty=="Easy":
                    col, minimax_score = minimax(board, 1, True)
                elif difficulty == "Medium":
                    col, minimax_score = minimax(board, 3, True)
                elif difficulty == "Hard":
                    col, minimax_score = minimax(board, 5, True)

                elapsed_time = time.time() - move_start_time

                # Store the elapsed time in the appropriate list
                minimax_scores_g.append(elapsed_time)

            elif algorithm=="Minimax with Alpha-Beta Pruning":
                move_start_time = time.time()
                #minimax_ab_scores_g.append(elapsed_time)
                if difficulty=="Easy":
                    col, minimax_ab_score = minimax_ab(board, 1, -math.inf, math.inf, True)
                elif difficulty == "Medium":
                    col, minimax_ab_score = minimax_ab(board, 3, -math.inf, math.inf, True)
                elif difficulty == "Hard":
                    col, minimax_ab_score = minimax_ab(board, 5, -math.inf, math.inf, True)

                elapsed_time = time.time() - move_start_time

                # Store the elapsed time in the appropriate list
                minimax_ab_scores_g.append(elapsed_time)

        # Player 2 AI's turn
        else:
            if algorithm=="Minimax":
                move_start_time = time.time()
                #minimax_scores_g.append(elapsed_time)
                if difficulty=="Easy":
                    col, minimax_score = minimax(board, 1, False)
                elif difficulty == "Medium":
                    col, minimax_score = minimax(board, 3, False)
                elif difficulty == "Hard":
                    col, minimax_score = minimax(board, 5, False)

            elif algorithm=="Minimax with Alpha-Beta Pruning":
                move_start_time = time.time()
                #minimax_ab_scores_g.append(elapsed_time)
                if difficulty=="Easy":
                    col, minimax_ab_score = minimax_ab(board, 1, -math.inf, math.inf, False)
                elif difficulty == "Medium":
                    col, minimax_ab_score = minimax_ab(board, 3, -math.inf, math.inf, False)
                elif difficulty == "Hard":
                    col, minimax_ab_score = minimax_ab(board, 5, -math.inf, math.inf, False)

                elapsed_time = time.time() - move_start_time

                # Store the elapsed time in the appropriate list
                minimax_ab_scores_g.append(elapsed_time)

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, turn + 1)

            if winning_move(board, turn + 1):
                label = myfont.render(f"AI {turn + 1} wins!", 1, YELLOW if turn == AI else RED)
                screen.blit(label, (40, 10))
                game_over = True
            elif is_terminal_node(board):  # Check for a draw
                label = myfont.render("Draw!", 1, YELLOW if turn == AI else RED)
                screen.blit(label, (150, 10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn %= 2

        if game_over:
            pygame.time.wait(3000)

        # messagebox.showinfo("Game Result", f"Algorithm: {algorithm}\nDifficulty: {difficulty}")
    total_elapsed_time = time.time() - start_time
    print(f"Total elapsed time for the game: {total_elapsed_time} seconds")
#elapsed_time = time.time() - start_time

def start_game():
    algorithm = algorithm_var.get()
    difficulty = difficulty_var.get()

    run_game(algorithm, difficulty)

# Create the main window
window = tk.Tk()
window.title("Game Options")

# Algorithm selection
algorithm_label = tk.Label(window, text="Select Algorithm:")
algorithm_label.pack()

algorithm_var = tk.StringVar(value="Minimax")
algorithm_option1 = tk.Radiobutton(window, text="Minimax", variable=algorithm_var, value="Minimax")
algorithm_option2 = tk.Radiobutton(window, text="Minimax with Alpha-Beta Pruning", variable=algorithm_var, value="Minimax with Alpha-Beta Pruning")
algorithm_option1.pack()
algorithm_option2.pack()

# Difficulty selection
difficulty_label = tk.Label(window, text="Select Difficulty:")
difficulty_label.pack()

difficulty_var = tk.StringVar(value="Easy")
difficulty_option1 = tk.Radiobutton(window, text="Easy", variable=difficulty_var, value="Easy")
difficulty_option2 = tk.Radiobutton(window, text="Medium", variable=difficulty_var, value="Medium")
difficulty_option3 = tk.Radiobutton(window, text="Hard", variable=difficulty_var, value="Hard")
difficulty_option1.pack()
difficulty_option2.pack()
difficulty_option3.pack()

# Start button
start_button = tk.Button(window, text="Start Game", command=start_game)
start_button.pack()

# Run the main event loop
window.mainloop()

window.mainloop()

# Plotting the graph
plt.plot(range(len(minimax_scores_g)), minimax_scores_g, label='Minimax',marker='o',markerfacecolor='green')
plt.plot(range(len(minimax_ab_scores_g)), minimax_ab_scores_g, label='Minimax with Alpha-Beta Pruning',marker='o',markerfacecolor='green')
plt.xlabel('Game Iteration')
plt.ylabel('Elapsed Time (seconds)')
plt.title('Algorithm Performance Comparison')
plt.legend()
plt.show()
