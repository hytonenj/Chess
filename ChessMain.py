import pygame as p
import ChessEngine

width = 512
height = 512
dimension = 8
squareSize = height//dimension
fps = 15
images = {}


def main():
    p.init()
    screen = p.display.set_mode((width,height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # generate valid moves when move is made (flag variable)

    loadImages()
    squareSelected = () # selected square (row, col)
    playerClicks = [] # track player clicks


    running = True
    while running:
        for e in p.event.get():
            # Quit event
            if e.type == p.QUIT:
                running = False

            # Mouse click event
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # mouse location x,y
                col = location[0] // squareSize
                row = location[1] // squareSize

                if squareSelected == (row, col): # unallow to select the same square
                    squareSelected = ()
                    playerClicks = []
                else:
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)
                if len(playerClicks) == 2: # check if second click -> make move
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    # check if the move is valid (cant move empty sq. on top of piece)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]: 
                            #print(move.getChessNotation())
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            squareSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [squareSelected]

            # Key press event
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    gs.undoMove()
                    moveMade = True

        # Whenever move is made - generate valid moves
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(fps)
        p.display.flip()

def loadImages():
    pieces = ["bp","wp","bR","wR","bN","wN","bB","wB","bQ","wQ","bK","wK"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/"+piece+".png"), (squareSize,squareSize))

def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("light blue")]
    for row in range(dimension):
        for col in range(dimension):
            color = colors[((row+col)%2)]
            p.draw.rect(screen, color, p.Rect(col*squareSize,row*squareSize,squareSize,squareSize))

def drawPieces(screen, board):
    for row in range(dimension):
        for col in range(dimension):
            piece = board[row][col]
            if piece != "--": #not empty
                screen.blit(images[piece],p.Rect(col*squareSize,row*squareSize,squareSize,squareSize))





if __name__ == "__main__":
    main()
