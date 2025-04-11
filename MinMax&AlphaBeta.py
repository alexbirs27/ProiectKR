import sys


# Folosim o tabla de joc cu 24 de pozitii, reprezentata de constantele BOARD_SIZE, X_PIECE, O_PIECE si EMPTY_CHAR.
# Vecinii fiecarei pozitii sunt definiti in lista NEIGHBORS, iar combinatiile de pozitii care formeaza o moara
# sunt definite in lista MILL_COMBOS. Aceste structuri sunt esentiale pentru logica jocului,
# permitand generarea mutarilor si evaluarea starii curente a jocului.
# Implementarea include generarea mutarilor posibile pentru jucatori, tinand cont de fazele jocului:
# - Faza 1: Plasarea pieselor pe tabla, cu atentie la formarea unei mori si eliminarea pieselor adversarului
# - Faza 2: Mutarea pieselor de-a lungul liniilor
# - Faza 3: Zborul pieselor cand un jucator are doar trei piese ramase





# Constante globale
BOARD_SIZE = 24
X_PIECE = 'x'     # Piesa jucatorului (maximizator)
O_PIECE = '0'     # Piesa adversarului (minimizator)
EMPTY_CHAR = None # Se determina din input

'''
Tabla are 24 de pozitii, aranjate dupa urmatoarea schema:
0           1             2 
    3       4       5
        6   7   8
9   10  11      12   13   14
        15  16  17
   18       19      20
21          22            23
'''

# Vecinii fiecarei pozitii
NEIGHBORS = [
    [1, 9],         # pozitia 0
    [0, 2, 4],      # pozitia 1
    [1, 14],        # pozitia 2
    [4, 10],        # pozitia 3
    [1, 3, 5, 7],   # pozitia 4
    [4, 13],        # pozitia 5
    [7, 11],        # pozitia 6
    [4, 6, 8],      # pozitia 7
    [7, 12],        # pozitia 8
    [0, 10, 21],    # pozitia 9
    [3, 9, 11, 18], # pozitia 10
    [6, 10, 15],    # pozitia 11
    [8, 13, 17],    # pozitia 12
    [5, 12, 14, 20],# pozitia 13
    [2, 13, 23],    # pozitia 14
    [11, 16],       # pozitia 15
    [15, 17, 19],   # pozitia 16
    [12, 16],       # pozitia 17
    [10, 19],       # pozitia 18
    [16, 18, 20, 22],# pozitia 19
    [13, 19],       # pozitia 20
    [9, 22],        # pozitia 21
    [19, 21, 23],   # pozitia 22
    [14, 22]        # pozitia 23
]

# Combinatii de 3 pozitii care formeaza o moara
MILL_COMBOS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [15, 16, 17], [18, 19, 20], [21, 22, 23],
    [0, 9, 21], [3, 10, 18], [6, 11, 15],
    [2, 14, 23], [5, 13, 20], [8, 12, 17],
    [1, 4, 7], [16, 19, 22],
    [9, 10, 11], [12, 13, 14]
]

# Verifica daca o linie este moara pentru un jucator
def is_mill_line(board, line, player):
    return (board[line[0]] == board[line[1]] == board[line[2]] == player)

# Functie de evaluare a starii: calculeaza scorul pe baza pieselor si configuratiilor
def evaluate_state(game_state):
    board, remX, remO = game_state
    countX = board.count(X_PIECE)
    countO = board.count(O_PIECE)
    if remX == 0 and remO == 0:
        if countO <= 2:
            return 100000  # castiga X
        if countX <= 2:
            return -100000 # castiga O

    # Determinam jucatorul curent (cel care urmeaza sa mute)
    current_player = X_PIECE if remX > 0 else O_PIECE ########################################################
    
    # Scorul ia in calcul totalul pieselor (pe tabla si ramase)
    pieceDiff = (countX + remX) - (countO + remO)
    score = 50 * pieceDiff

    # Calculeaza cate piese sunt blocate
    xBlocked = 0
    oBlocked = 0
    for i in range(BOARD_SIZE):
        if board[i] == X_PIECE:
            if not any(board[nb] == EMPTY_CHAR for nb in NEIGHBORS[i]):
                xBlocked += 1
        elif board[i] == O_PIECE:
            if not any(board[nb] == EMPTY_CHAR for nb in NEIGHBORS[i]):
                oBlocked += 1
    score += 10 * (oBlocked - xBlocked)

    # Adauga puncte pentru configuratii si mori
    xTwoConfig = 0
    oTwoConfig = 0
    xMills = 0
    oMills = 0
    xMillCountForPos = [0] * BOARD_SIZE
    oMillCountForPos = [0] * BOARD_SIZE

    # Poziții centrale care oferă mai multe opțiuni
    CENTRAL_POSITIONS = {4, 10, 13, 19}
    
    for line in MILL_COMBOS:
        xPieces = sum(1 for pos in line if board[pos] == X_PIECE)
        oPieces = sum(1 for pos in line if board[pos] == O_PIECE)
        if xPieces == 3:
            xMills += 1
            for pos in line:
                if board[pos] == X_PIECE:
                    xMillCountForPos[pos] += 1
        if oPieces == 3:
            oMills += 1
            for pos in line:
                if board[pos] == O_PIECE:
                    oMillCountForPos[pos] += 1
        if xPieces == 2 and oPieces == 0:
            xTwoConfig += 1
        if oPieces == 2 and xPieces == 0:
            oTwoConfig += 1

    # Increase weights for mills and potential mills
    score += 25 * (xTwoConfig - oTwoConfig)
    xDoubleMorris = sum(1 for i in range(BOARD_SIZE) if board[i] == X_PIECE and xMillCountForPos[i] >= 2)
    oDoubleMorris = sum(1 for i in range(BOARD_SIZE) if board[i] == O_PIECE and oMillCountForPos[i] >= 2)
    score += 40 * (xDoubleMorris - oDoubleMorris)
    score += 30 * (xMills - oMills)

    # Add bonus for pieces that can form mills in next move
    for pos in range(BOARD_SIZE):
        if board[pos] == EMPTY_CHAR:
            # Bonus pentru poziții centrale
            if pos in CENTRAL_POSITIONS:
                if current_player == X_PIECE:
                    score += 15
                else:
                    score -= 15
            
            # Check if placing a piece here would form a mill
            mill_lines = 0
            for line in MILL_COMBOS:
                if pos in line:
                    xPieces = sum(1 for p in line if board[p] == X_PIECE and p != pos)
                    oPieces = sum(1 for p in line if board[p] == O_PIECE and p != pos)
                    if xPieces == 2:
                        score += 30  # Increased bonus for X potential mill
                        mill_lines += 1
                    if oPieces == 2:
                        score -= 30  # Increased penalty for O potential mill
                        mill_lines += 1
            
            # Bonus pentru poziții care pot forma mori în mai multe direcții
            if mill_lines > 1:
                if current_player == X_PIECE:
                    score += 20 * (mill_lines - 1)
                else:
                    score -= 20 * (mill_lines - 1)

    # Daca O este la mutare, inversam scorul pentru a maximiza pentru O
    if current_player == O_PIECE:
        score = -score

    return score

# Seteaza o piesa pe tabla la o anumita pozitie
def set_piece_on_board(board, pos, piece):
    return board[:pos] + piece + board[pos+1:]

# Genereaza toate mutarile posibile pentru jucatorul curent
def generate_moves(game_state, curPlayer):
    board, remX, remO = game_state
    moves = []
    phase1_placing = False
    canFly = False

    # Verifica daca suntem in faza de plasare (mai sunt piese ramase)
    if curPlayer == X_PIECE:
        if remX > 0:
            phase1_placing = True
        else:
            if board.count(X_PIECE) == 3:
                canFly = True
    else:
        if remO > 0:
            phase1_placing = True
        else:
            if board.count(O_PIECE) == 3:
                canFly = True

    # Mutari in faza de plasare
    if phase1_placing:
        for pos in range(BOARD_SIZE):
            if board[pos] == EMPTY_CHAR:
                newBoard = set_piece_on_board(board, pos, curPlayer)
                if curPlayer == X_PIECE:
                    newGameState = (newBoard, remX - 1, remO)
                else:
                    newGameState = (newBoard, remX, remO - 1)
                millFormed = False
                for line in MILL_COMBOS:
                    if pos in line and is_mill_line(newBoard, line, curPlayer):
                        millFormed = True
                        break
                if millFormed:
                    opponent = O_PIECE if curPlayer == X_PIECE else X_PIECE
                    removable = []
                    inMill = []
                    for i in range(BOARD_SIZE):
                        if newBoard[i] == opponent:
                            flagInMill = False
                            for line in MILL_COMBOS:
                                if i in line and is_mill_line(newBoard, line, opponent):
                                    flagInMill = True
                                    break
                            if flagInMill:
                                inMill.append(i)
                            else:
                                removable.append(i)
                    if not removable:
                        removable = inMill
                    for remPos in removable:
                        boardAfterRemoval = set_piece_on_board(newBoard, remPos, EMPTY_CHAR)
                        moves.append((boardAfterRemoval, newGameState[1], newGameState[2]))
                else:
                    moves.append(newGameState)
    # Mutari in faza de deplasare sau flying
    else:
        for frm in range(BOARD_SIZE):
            if board[frm] == curPlayer:
                if canFly:
                    for to in range(BOARD_SIZE):
                        if board[to] == EMPTY_CHAR and to != frm:
                            newBoard = set_piece_on_board(set_piece_on_board(board, frm, EMPTY_CHAR), to, curPlayer)
                            millFormed = False
                            for line in MILL_COMBOS:
                                if to in line and is_mill_line(newBoard, line, curPlayer):
                                    millFormed = True
                                    break
                            if millFormed:
                                opponent = O_PIECE if curPlayer == X_PIECE else X_PIECE
                                removable = []
                                inMill = []
                                for i in range(BOARD_SIZE):
                                    if newBoard[i] == opponent:
                                        flagInMill = False
                                        for line in MILL_COMBOS:
                                            if i in line and is_mill_line(newBoard, line, opponent):
                                                flagInMill = True
                                                break
                                        if flagInMill:
                                            inMill.append(i)
                                        else:
                                            removable.append(i)
                                if not removable:
                                    removable = inMill
                                for remPos in removable:
                                    boardAfterRemoval = set_piece_on_board(newBoard, remPos, EMPTY_CHAR)
                                    moves.append((boardAfterRemoval, remX, remO))
                            else:
                                moves.append((newBoard, remX, remO))
                else:
                    for to in NEIGHBORS[frm]:
                        if board[to] == EMPTY_CHAR:
                            newBoard = set_piece_on_board(set_piece_on_board(board, frm, EMPTY_CHAR), to, curPlayer)
                            millFormed = False
                            for line in MILL_COMBOS:
                                if to in line and is_mill_line(newBoard, line, curPlayer):
                                    millFormed = True
                                    break
                            if millFormed:
                                opponent = O_PIECE if curPlayer == X_PIECE else X_PIECE
                                removable = []
                                inMill = []
                                for i in range(BOARD_SIZE):
                                    if newBoard[i] == opponent:
                                        flagInMill = False
                                        for line in MILL_COMBOS:
                                            if i in line and is_mill_line(newBoard, line, opponent):
                                                flagInMill = True
                                                break
                                        if flagInMill:
                                            inMill.append(i)
                                        else:
                                            removable.append(i)
                                if not removable:
                                    removable = inMill
                                for remPos in removable:
                                    boardAfterRemoval = set_piece_on_board(newBoard, remPos, EMPTY_CHAR)
                                    moves.append((boardAfterRemoval, remX, remO))
                            else:
                                moves.append((newBoard, remX, remO))
    return moves

# Algoritmul minimax recursiv
def minimax(game_state, depth, maximizingPlayer):
    board, remX, remO = game_state
    countX = board.count(X_PIECE)
    countO = board.count(O_PIECE)
    if depth == 0 or (remX == 0 and remO == 0 and (countO <= 2 or countX <= 2)):
        return evaluate_state(game_state), game_state

    if maximizingPlayer:
        maxEval = -1000000
        moves = generate_moves(game_state, X_PIECE)
        if not moves:
            return -100000
        for nextState in moves:
            eval_value, _ = minimax(nextState, depth - 1, False)
            if eval_value > maxEval:
                maxEval = eval_value
                bestMove = nextState
        return maxEval, bestMove
    else:
        minEval = 1000000
        moves = generate_moves(game_state, O_PIECE)
        if not moves:
            return 100000
        for nextState in moves:
            eval_value, _ = minimax(nextState, depth - 1, True)
            if eval_value < minEval:
                minEval = eval_value
                bestMove = nextState
        return minEval, bestMove

# Versiunea alphabeta a algoritmului minimax
def alphabeta(game_state, depth, alpha, beta, maximizingPlayer):
    board, remX, remO = game_state
    countX = board.count(X_PIECE)
    countO = board.count(O_PIECE)
    if depth == 0 or (remX == 0 and remO == 0 and (countO <= 2 or countX <= 2)):
        return evaluate_state(game_state), game_state

    if maximizingPlayer:
        maxEval = float('-inf')
        moves = generate_moves(game_state, X_PIECE)
        if not moves:
            return -100000, game_state
        bestMove = moves[0]
        for nextState in moves:
            eval_value, _ = alphabeta(nextState, depth - 1, alpha, beta, False)
            if eval_value > maxEval:
                maxEval = eval_value
                bestMove = nextState
            alpha = max(alpha, eval_value)
            if beta <= alpha:
                break
        return maxEval, bestMove
    else:
        minEval = float('inf')
        moves = generate_moves(game_state, O_PIECE)
        if not moves:
            return 100000, game_state
        bestMove = moves[0]
        for nextState in moves:
            eval_value, _ = alphabeta(nextState, depth - 1, alpha, beta, True)
            if eval_value < minEval:
                minEval = eval_value
                bestMove = nextState
            beta = min(beta, eval_value)
            if beta <= alpha:
                break
        return minEval, bestMove

def format_board(board_str):
    positions = list(board_str)
    
    # Format the board with the actual positions
    formatted = []
    formatted.append(f"{positions[0]}           {positions[1]}             {positions[2]}")
    formatted.append(f"    {positions[3]}       {positions[4]}       {positions[5]}")
    formatted.append(f"        {positions[6]}   {positions[7]}   {positions[8]}")
    formatted.append(f"{positions[9]}   {positions[10]}   {positions[11]}       {positions[12]}   {positions[13]}     {positions[14]}")
    formatted.append(f"        {positions[15]}   {positions[16]}   {positions[17]}")
    formatted.append(f"    {positions[18]}       {positions[19]}       {positions[20]}")
    formatted.append(f"{positions[21]}           {positions[22]}             {positions[23]}")
    return formatted

# Functia principala care citeste input-ul, ruleaza algoritmul si scrie output
def main():
    
    global EMPTY_CHAR
    # Citim input-ul direct din fisierul "input.txt"
    with open("input.txt", "r") as infile:
        inp = infile.read().split()
    
    ID = inp[0]
    stateInput = inp[1]
    tupleStr = inp[2]
    algorithm = inp[3].lower()
    depth = int(inp[4])

    # Det caracterul pentru poz libera (diferit de X_PIECE si O_PIECE)
    EMPTY_CHAR = '*'
    for c in stateInput:
        if c != X_PIECE and c != O_PIECE:
            EMPTY_CHAR = c
            break
    if len(stateInput) < BOARD_SIZE:
        print("Dimensiunea starii nu este corecta.\n")
        return
    
    # Parsam tuplul (nx, n0)
    tupleStr = tupleStr.strip("()")
    parts = tupleStr.split(',')
    remX = int(parts[0])
    remO = int(parts[1])

    # Determinam cine este la mutare
    if remX < remO:
        curPlayer = O_PIECE
    else:
        curPlayer = X_PIECE

    print(f"Este randul lui: {'0' if curPlayer == O_PIECE else 'x'}")

    # Modify stateInput to be a tuple with three elements: board, remX, remO
    stateInput = (stateInput, remX, remO)

    # generam toate mutarile posibile pentru jucatorul curent
    all_moves = generate_moves(stateInput, curPlayer)
    
    # Alegem algoritmul de cautare
    if algorithm == "minimax":
        if curPlayer == X_PIECE:
            bestNextState = minimax(stateInput, depth, True)[1]
        else:  # O_PIECE
            bestNextState = minimax(stateInput, depth, False)[1]
    else:  # alphabeta
        if curPlayer == X_PIECE:
            bestNextState = alphabeta(stateInput, depth, float('-inf'), float('inf'), True)[1]
        else:  # O_PIECE
            bestNextState = alphabeta(stateInput, depth, float('-inf'), float('inf'), False)[1]

    # Facem output-ul in "output.txt"
    output_lines = []
    output_lines.append(f"ID: {ID}")
    
    # Format the initial board
    output_lines.append("Initial board:")
    output_lines.extend(format_board(stateInput[0]))
    output_lines.append("")
    
    # Format the best move
    output_lines.append("Best move:")
    output_lines.extend(format_board(bestNextState[0]))
    output_lines.append("")
    
    output_lines.append("Generated moves:")
    for move in all_moves:
        move_str = move[0]
        score = evaluate_state(move)
        output_lines.append(f"{move_str} (score: {score})")

    output_text = "\n".join(output_lines)   
    print("Verifica output.txt")
    with open("output.txt", "w") as outfile:
        outfile.write(output_text)

if __name__ == '__main__':
    main()
