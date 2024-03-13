"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xCount = 0
    oCount = 0
    for row in board:
        for cell in row:
            if cell == X:
                xCount += 1
            if cell == O:
                oCount += 1
    if oCount >= xCount:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    ass = set()
    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j]==EMPTY:
                ass.add((i, j))
    return ass


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action[0] not in range(0,3) or action[1] not in range(0, 3):
        raise Exception("cannot play there, stick to the board boardy")
    if board[action[0]][action[1]] != EMPTY:
        raise Exception("cannot play there, taken")
    newBoard = [[EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY]]
    for i in range(0, 3):
        for j in range(0, 3):
            newBoard[i][j] = board[i][j]
    newBoard[action[0]][action[1]] = player(newBoard)
    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """    
    for i in range(0,3):
        if board[0][i] != EMPTY and board[0][i]==board[1][i]==board[2][i]:
            return board[0][i] 
        if board[i][0] != EMPTY and board[i][0]==board[i][1]==board[i][2]:
            return board[i][0] 
    
    if board[0][0] != EMPTY and board[0][0]==board[1][1]==board[2][2]:
        return board[0][0] 
    if board[2][0] != EMPTY and board[2][0]==board[1][1]==board[0][2]:
        return board[2][0] 
    
    return None



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j] is EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    if X == w: return 1
    if O == w: return -1 
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    currPlayer = player(board)
    v = -2
    bestAction = (0, 0)
    if currPlayer == X:
        bestValue = -2
        for action in actions(board):
            v = minValue(result(board, action))
            if v > bestValue:
                bestValue = v
                bestAction = action
    else:
        bestValue = 2
        for action in actions(board):
            v = maxValue(result(board, action))
            if v < bestValue:
                bestValue = v
                bestAction = action
    return bestAction

def minValue(board) -> int:
    if terminal(board):
        return utility(board)
    v = 2
    for action in actions(board):
        v = min(v, maxValue(result(board, action)))
    return v


def maxValue(board) -> int:
    if terminal(board):
        return utility(board)
    v = -2
    for action in actions(board):
        v = max(v, minValue(result(board, action)))
    return v