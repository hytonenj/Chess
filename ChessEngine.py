'''
Class to store the information about the state of the game.
'''

class GameState():
    def __init__(self):

        # board: First letter represents the color of the piece, i.e., b for black and w for white.
        # second cahracter represents the piece: p for pawn etc.
        # "--" represents empty square.
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        self.switcher = {"p":self.getPawnMoves, "R":self.getRookMoves, "B":self.getBishopMoves,
         "N":self.getKnightMoves, "K":self.getKingMoves, "Q":self.getQueenMoves}
        self.whiteToMove = True
        self.moveList = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # coordinates where enpassant capture is possible

    # different move logic for castling, en-passant and pawn promotion
    def makeMove(self, move):
        self.board[move.start[0]][move.start[1]] = "--"
        self.board[move.end[0]][move.end[1]] = move.pieceMoved
        self.moveList.append(move) # list the moves
        self.whiteToMove = not self.whiteToMove # change turn
        #update king's location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.end[0], move.end[1])
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.end[0], move.end[1])

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.end[0]][move.end[1]] = move.pieceMoved[0]+'Q'

        # en passant
        if move.isEnpassantMove:
            self.board[move.start[0]][move.end[1]] = "--"
        # en passant possible only right after two move pawn push is made
        if move.pieceMoved[1] == "p" and abs(move.start[0]-move.end[0]) == 2:
            self.enpassantPossible = ((move.start[0]+move.end[0])//2, move.start[1])
        else:
            self.enpassantPossible = ()

    def undoMove(self):
        if self.moveList != 0:
            move = self.moveList.pop()
            self.board[move.start[0]][move.start[1]] = move.pieceMoved
            self.board[move.end[0]][move.end[1]] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update king's location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.start[0], move.start[1])
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.start[0], move.start[1])

            # undo en passant
            if move.isEnpassantMove:
                self.board[move.end[0]][move.end[1]] = "--" # leave landing square
                self.board[move.start[0]][move.end[1]] = move.pieceCaptured
                self.enpassantPossible = (move.end[0], move.end[1])
            if move.pieceMoved[1] == "p" and abs(move.start[0]-move.end[1]) == 2:
                self.enpassantPossible = ()

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        '''
        1) generate all moves
        2) for each move, make move
        3) generate all opponent's moves
        4) for each oppponent move, see if they attack king
        5) if they attack, not a valid move
        '''
        # save for generating moves
        tempEnpassantPossible = self.enpassantPossible
        
        moves = self.getAllPossibleMoves() 
        # when removing from a list - move backwards
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # switch turns
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            # switch back
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        else:
            self.staleMate = False
            self.checkMate = False

        self.enpassantPossible = tempEnpassantPossible
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # switch to opponent's pov
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch turns back
        for move in oppMoves:
            if (move.end[0] == row) and (move.end[1] == col): # if square under attack
                return True
        return False       

    '''
    All moves
    '''
    def getAllPossibleMoves(self):
        possibleMoves = [] # Move((4,6),(4,4), self.board)
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                color = self.board[row][col][0]
                if(color == "w" and self.whiteToMove) or (color == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.switcher[piece](row, col, possibleMoves)
        return possibleMoves

    def getPawnMoves(self, row, col, possibleMoves):
        # White moves
        if self.whiteToMove: 
            if self.board[row-1][col] == "--":
                possibleMoves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--":
                    possibleMoves.append(Move((row, col), (row-2, col), self.board))
            # Captures
            if col-1 >= 0: # Left side capture
                if self.board[row-1][col-1][0] == "b":
                    possibleMoves.append(Move((row, col), (row-1, col-1), self.board))
                #enpassant
                elif (row-1, col-1) == self.enpassantPossible:
                    possibleMoves.append(Move((row, col), (row-1, col-1), self.board, isEnpassantMove = True))
            if col+1 <= 7: # Right side capture
                if self.board[row-1][col+1][0] == "b":
                    possibleMoves.append(Move((row, col), (row-1, col+1), self.board))
                #enpassant
                elif (row-1, col+1) == self.enpassantPossible:
                    possibleMoves.append(Move((row, col), (row-1, col+1), self.board, isEnpassantMove = True))
        # Black moves
        if not self.whiteToMove:
            if self.board[row+1][col] == "--":
                possibleMoves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row+2][col] == "--":
                    possibleMoves.append(Move((row, col), (row+2, col), self.board))
            # Captures
            if col-1 >= 0: # Left side capture
                if self.board[row+1][col-1][0] == "w":
                    possibleMoves.append(Move((row, col), (row+1, col-1), self.board))
                #enpassant
                elif (row+1, col-1) == self.enpassantPossible:
                    possibleMoves.append(Move((row, col), (row+1, col-1), self.board, isEnpassantMove = True))
            if col+1 <= 7: # Right side capture
                if self.board[row+1][col+1][0] == "w":
                    possibleMoves.append(Move((row, col), (row+1, col+1), self.board))
                #enpassant
                elif (row+1, col+1) == self.enpassantPossible:
                    possibleMoves.append(Move((row, col), (row+1, col+1), self.board, isEnpassantMove = True))

    def getRookMoves(self, row, col, possibleMoves):
        r = row
        c = col
        canEat = "b"
        if self.whiteToMove:
            canEat = "b"
        else:
            canEat = "w"
        # Down
        for r in range(row+1, 8, 1):
            if self.board[r][col] == "--":
                possibleMoves.append(Move((row, col), (r, col), self.board))
            elif self.board[r][col][0] == canEat:
                possibleMoves.append(Move((row, col), (r, col), self.board))
                break
            else:
                break
        # Up
        for r in range(row-1, -1, -1):
            if self.board[r][col] == "--":
                possibleMoves.append(Move((row, col), (r, col), self.board))
            elif self.board[r][col][0] == canEat:
                possibleMoves.append(Move((row, col), (r, col), self.board))
                break
            else:
                break
        # Right
        for c in range(col+1, 8, 1):
            if self.board[row][c] == "--":
                possibleMoves.append(Move((row, col), (row, c), self.board))
            elif self.board[row][c][0] == canEat:
                possibleMoves.append(Move((row, col), (row, c), self.board))
                break
            else:
                break
        # Left
        for c in range(col-1, -1, -1):
            if self.board[row][c] == "--":
                possibleMoves.append(Move((row, col), (row, c), self.board))
            elif self.board[row][c][0] == canEat:
                possibleMoves.append(Move((row, col), (row, c), self.board))
                break
            else:
                break

    def getBishopMoves(self, row, col, possibleMoves):
        r = row
        c = col
        canEat = "b"
        if self.whiteToMove:
            canEat = "b"
        else:
            canEat = "w"

        # DownRight
        if col+1 < 8 and row+1 < 8:
            for r, c in zip(range(row+1, 8, 1), range(col+1, 8, 1)):
                if (self.board[r][c] == "--"):
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                elif self.board[r][c][0] == canEat:
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                    break                
                else:
                    break
        # DownLeft
        if(col-1 >= 0 and row+1 < 8):
            for r, c in zip(range(row+1, 8, 1), range(col-1, -1, -1)):
                if (self.board[r][c] == "--"):
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                elif self.board[r][c][0] == canEat:
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                    break                
                else:
                    break
        
        # UpLeft
        if(col-1 >= 0 and row-1 >= 0):
            for r, c in zip(range(row-1, -1, -1), range(col-1, -1, -1)):
                if (self.board[r][c] == "--"):
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                elif self.board[r][c][0] == canEat:
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                    break                
                else:
                    break

        # UpRight
        if(col+1 < 8 and row-1 >= 0):
            for r, c in zip(range(row-1, -1, -1), range(col+1, 8, 1)):
                if (self.board[r][c] == "--"):
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                elif self.board[r][c][0] == canEat:
                    possibleMoves.append(Move((row, col), (r, c), self.board))
                    break                
                else:
                    break


    def getKnightMoves(self, row, col, possibleMoves):
        r = row
        c = col
        canEat = "b"
        if self.whiteToMove:
            canEat = "b"
        else:
            canEat = "w"

        # RightSide
        if(col+1 < 8): # check first column edge
            if(row+2 < 8): # check both row edges
                if (self.board[row+2][col+1] == "--") or (self.board[row+2][col+1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row+2, col+1), self.board))
            if(row-2 >= 0):
                if (self.board[row-2][col+1] == "--") or (self.board[row-2][col+1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row-2, col+1), self.board))
        if(col+2 < 8): # check second column edge
            if(row+1 < 8): # check both row edges
                if (self.board[row+1][col+2] == "--") or (self.board[row+1][col+2][0] == canEat):
                    possibleMoves.append(Move((row, col), (row+1, col+2), self.board))
            if(row-1 >= 0):
                if (self.board[row-1][col+2] == "--") or (self.board[row-1][col+2][0] == canEat):
                    possibleMoves.append(Move((row, col), (row-1, col+2), self.board))    
        # LeftSide
        if(col-1 >= 0): # check first column edge
            if(row+2 < 8): # check both row edges
                if (self.board[row+2][col-1] == "--") or (self.board[row+2][col-1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row+2, col-1), self.board))
            if(row-2 >= 0):
                if (self.board[row-2][col-1] == "--") or (self.board[row-2][col-1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row-2, col-1), self.board))
        if(col-2 >= 0): # check second column edge
            if(row+1 < 8): # check both row edges
                if (self.board[row+1][col-2] == "--") or (self.board[row+1][col-2][0] == canEat):
                    possibleMoves.append(Move((row, col), (row+1, col-2), self.board))
            if(row-1 >= 0):
                if (self.board[row-1][col-2] == "--") or (self.board[row-1][col-2][0] == canEat):
                    possibleMoves.append(Move((row, col), (row-1, col-2), self.board))    

    def getQueenMoves(self, row, col, possibleMoves):
        self.getBishopMoves(row, col, possibleMoves)
        self.getRookMoves(row, col, possibleMoves)

    def getKingMoves(self, row, col, possibleMoves):
        canEat = "b"
        if self.whiteToMove:
            canEat = "b"
        else:
            canEat = "w"

        # RightSide
        if col+1 < 8:
            # right
            if (self.board[row][col+1] == "--") or (self.board[row][col+1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row, col+1), self.board))
            # diagonal down
            if row+1 < 8:
                if (self.board[row+1][col+1] == "--") or (self.board[row+1][col+1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row+1, col+1), self.board))    
            # diagonal up
            if row-1 >= 0:
                if (self.board[row-1][col+1] == "--") or (self.board[row-1][col+1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row-1, col+1), self.board))
        # Down
        if row+1 < 8:
            if (self.board[row+1][col] == "--") or (self.board[row+1][col][0] == canEat):
                    possibleMoves.append(Move((row, col), (row+1, col), self.board))
        # Up
        if row-1 >= 0:
            if (self.board[row-1][col] == "--") or (self.board[row-1][col][0] == canEat):
                    possibleMoves.append(Move((row, col), (row-1, col), self.board))
        # LeftSide
        if col-1 >= 0:
            # left
            if (self.board[row][col-1] == "--") or (self.board[row][col-1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row, col-1), self.board))
            # diagonal down
            if row+1 < 8:
                if (self.board[row+1][col-1] == "--") or (self.board[row+1][col-1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row+1, col-1), self.board))    
            # diagonal up
            if row-1 >= 0:
                if (self.board[row-1][col-1] == "--") or (self.board[row-1][col-1][0] == canEat):
                    possibleMoves.append(Move((row, col), (row-1, col-1), self.board))




'''
class to store information about the moves
'''
class Move():
    ranksToRows = {"8":0,"7":1,"6":2,"5":3,"4":4,"3":5,"2":6,"1":7}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start, end, board, isEnpassantMove = False):
        self.start = start
        self.end = end
        self.pieceMoved = board[self.start[0]][self.start[1]] # first row then col
        self.pieceCaptured = board[self.end[0]][self.end[1]]
        self.moveId = self.start[0] * 1000 + self.start[1] * 100 + self.end[0] * 10 + self.end[1]
        self.isPawnPromotion = False
        # maybe move logic into pawnMove
        if (self.pieceMoved == "wp" and self.end[0] == 0) or (self.pieceMoved == "bp" and self.end[0] == 7): 
            self.isPawnPromotion = True
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        

    def isValid(self):
        if self.pieceMoved != "--":
            return True
        else:
            return False

    def __eq__(self,other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def getChessNotation(self):
        #TBD real chess notation
        return self.getRankFile(self.start[0], self.start[1]) + self.getRankFile(self.end[0], self.end[1])

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]



