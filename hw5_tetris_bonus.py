#name: David Andrei Bratu
#andrewID: dbratu

from cmu_graphics import *
import random

# Default game dimensions
def gameDimensions():
    rows = 15
    cols = 10
    cellSize = 20
    margin = 25
    return (rows, cols, cellSize, margin)

def playTetris():
    rows, cols, cellSize, margin = gameDimensions()
    
    # Calculate the size of the window for the game
    width = cols * cellSize + 2 * margin
    height = rows * cellSize + 2 * margin
    
    # Run the game
    runApp(width = width, height = height)
    
def onAppStart(app):
    app.rows, app.cols, app.cellSize, app.margin = gameDimensions()
    app.emptyColor = 'blue'
    app.board = [[app.emptyColor] * app.cols for _ in range(app.rows)]
    app.stepsPerDrop = 7   # bigger = slower
    app.stepCounter = 0
    app.isGameOver = False
    app.score = 0

    # Seven "standard" pieces (tetrominoes)
    iPiece = [
        [  True,  True,  True,  True ]
    ]

    jPiece = [
        [  True, False, False ],
        [  True,  True,  True ]
    ]

    lPiece = [
        [ False, False,  True ],
        [  True,  True,  True ]
    ]

    oPiece = [
        [  True,  True ],
        [  True,  True ]
    ]

    sPiece = [
        [ False,  True,  True ],
        [  True,  True, False ]
    ]

    tPiece = [
        [ False,  True, False ],
        [  True,  True,  True ]
    ]

    zPiece = [
        [  True,  True, False ],
        [ False,  True,  True ]
    ]
    
    app.tetrisPieces = [iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, zPiece]
    app.tetrisPieceColors = [ "red", "yellow", "magenta", "pink", "cyan",
                              "green", "orange" ]
    app.fallingPiece = None
    app.fallingPieceColor = None
    app.fallingPieceRow = None
    app.fallingPieceCol = None
    newFallingPiece(app) # Draw the initial piece
    
    ### bonus ###
    app.bonus = False
    app.bloodStains = [
        'hw5_tetris_bonus_assets/bloodStain1.png',
        'hw5_tetris_bonus_assets/bloodStain2.png',
        'hw5_tetris_bonus_assets/bloodStain3.png'
        ]
    
    # Random interval logic
    app.panicMinPieces = 6 # Min number of pieces before next panic
    app.panicMaxPieces = 14 # Max number of pieces before next panic
    app.panicBagSize = 6 
    app.panicBag = [] # Piece interval between panic events
    refillPanicBag(app) # First refill
    app.piecesUntilPanic = popNextPanicInterval(app) # First interval
    
    # Panic events
    app.panicActive = False
    app.panicTimer = 0
    app.panicDuration = 60
    app.flashOn = False
    app.flashCounter = 0
    app.flashPeriod = 2 # bigger means more time between and during flashes
    
    # Sounds
    app.panicSound = Sound('hw5_tetris_bonus_assets/panicSound.wav')
    app.panicSoundPlaying = False
    
    # Jumpscare
    app.scareImage = 'hw5_tetris_bonus_assets/scaryFace.jpeg' 
    app.scareSound = Sound('hw5_tetris_bonus_assets/jumpscareSound.mp3') 

    app.jumpscareActive = False
    app.jumpscareDuration = 45 # bigger means the jumpscare lasts longer
    app.jumpscareTimer = 0

# This function generates a new falling piece
def newFallingPiece(app):
    randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
    
    # Choose a random shape and color
    app.fallingPiece = app.tetrisPieces[randomIndex]
    app.fallingPieceColor = app.tetrisPieceColors[randomIndex]
    
    # Store the piece's position relative to the board
    # Top row of piece
    app.fallingPieceRow = 0
    # Left col of piece
    numFallingPieceCols = len(app.fallingPiece[0])
    app.fallingPieceCol = app.cols//2 - numFallingPieceCols//2
    
# This function draws the falling pieces
def drawFallingPiece(app):
    rows, cols = len(app.fallingPiece), len(app.fallingPiece[0])
    color = app.fallingPieceColor
    for row in range(rows):
        for col in range(cols):
            if app.fallingPiece[row][col]:
                boardRow = app.fallingPieceRow + row
                boardCol = app.fallingPieceCol + col
                drawCell(app, boardRow, boardCol, color)
            
# This function moves the piece on the board
def moveFallingPiece(app, drow, dcol):
    app.fallingPieceRow += drow
    app.fallingPieceCol += dcol
    
    # undo if new position is illegal
    if not fallingPieceLegal(app):
        app.fallingPieceRow -= drow
        app.fallingPieceCol -= dcol
        return False # in this case, the move was not actually executed 
    
    return True
    
# This  function rotates the piece on the board
def rotateFallingPiece(app):
    # Map the old dimensions in case we need to revert the changes
    oldPiece = app.fallingPiece
    oldRows, oldCols = len(app.fallingPiece), len(app.fallingPiece[0])
    oldRow, oldCol = app.fallingPieceRow, app.fallingPieceCol # old top-left 
    
    # Generate the new piece
    newRows = oldCols
    newCols = oldRows
    newPiece = [[None] * newCols for _ in range(newRows)]
    for row in range(oldRows):
        for col in range(oldCols):
            if oldPiece[row][col]:
                newPiece[oldCols - 1 - col][row] = True
    
    # update existing piece            
    app.fallingPiece = newPiece
    app.fallingPieceRow = oldRow + oldRows//2 -newRows//2 #same center as before
    app.fallingPieceCol = oldCol + oldCols//2 -newCols//2 #same center as before
    
    # undo if new postion is illegal
    if not fallingPieceLegal(app):
        app.fallingPiece = oldPiece
        app.fallingPieceRow = oldRow
        app.fallingPieceCol = oldCol
        
# This function places the falling piece
def placeFallingPiece(app):
    rows, cols = len(app.fallingPiece), len(app.fallingPiece[0])
    color = app.fallingPieceColor
    for row in range(rows):
        for col in range(cols):
            if app.fallingPiece[row][col]:
                boardRow = app.fallingPieceRow + row
                boardCol = app.fallingPieceCol + col
                app.board[boardRow][boardCol] = color
    removeFullRows(app)
    
    # Bonus: countdown until next panic event
    if app.bonus and (not app.panicActive):
        app.piecesUntilPanic -= 1
        
        if app.piecesUntilPanic <= 0:
            # Initialize panic event
            app.panicActive = True
            app.panicTimer = app.panicDuration
            app.flashOn = True
            app.flashCounter = 0
            
            if not app.panicSoundPlaying:
                app.panicSound.play(restart=True)
                app.panicSoundPlaying = True
            
            # Reset to next interval
            app.piecesUntilPanic = popNextPanicInterval(app)
            
        
# Helper function that checks whether a move is legal
def fallingPieceLegal(app):
    rows, cols = len(app.fallingPiece), len(app.fallingPiece[0])
    for row in range(rows):
        for col in range(cols):
            if app.fallingPiece[row][col]:
                boardRow = app.fallingPieceRow + row
                boardCol = app.fallingPieceCol + col
                if not (0<= boardRow < app.rows and 0<= boardCol < app.cols):
                    return False
                if (app.board[boardRow][boardCol] != app.emptyColor):
                    return False
    return True

# This function removes full rows
def removeFullRows(app):
    fullRows = 0
    newBoard = []
    
    for rowList in app.board:
        if app.emptyColor not in rowList:
            fullRows += 1
        else: newBoard.append(rowList)
    
    # Add new empty rows at the top
    emptyRows = [[app.emptyColor] * app.cols for _ in range(fullRows)]
    newBoard = emptyRows + newBoard
    app.board = newBoard
    
    # Keeping track of score
    app.score += fullRows**2

# Main draw function
def redrawAll(app):
    # Draw background (plus bonus color)
    if app.bonus: color = 'black'
    else: color = 'orange'
    drawRect(0, 0, app.width, app.height, fill = color)
    
    # Draw Board
    drawBoard(app)
    drawFallingPiece(app)
    drawScore(app)
    
    # Game over screen
    if app.isGameOver:
        bannerWidth = app.cellSize * app.cols
        bannerHeight = app.cellSize * (app.rows // 6)
        drawRect(app.margin, app.margin + app.cellSize, bannerWidth,
                 bannerHeight, fill = 'black')
        drawLabel('Game Over!', app.width/2,
                  app.margin + app.cellSize + bannerHeight/2, fill = 'yellow',
                  size = 16, bold = True)
        
    # Bonus Version
    if app.bonus:
        drawBlood(app)
    if app.bonus and app.panicActive and app.flashOn:
        drawRect(0, 0, app.width, app.height, fill='white', opacity=30)
    if app.jumpscareActive:
        drawImage(app.scareImage, app.width/2, app.height/2, align='center',
                  width=app.width,height=app.height)

# Helper function that draws the board
def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col) 

# Helper function that draws one cell
def drawCell(app, row, col, color = None):
    if color is None:
        color = app.board[row][col]
    x = app.margin + app.cellSize * col
    y = app.margin + app.cellSize * row
    drawRect(x, y, app.cellSize, app.cellSize, fill = color, border = 'black')

# Helper function that draws the score at the top of the window
def drawScore(app):
    if app.bonus: color = 'red'
    else: color = 'black'
    x = app.width/2
    y = app.margin/2
    drawLabel(f'Score: {app.score}', x, y, size = 16, bold = True, fill = color)

# Bonus helper that draws blood marks
def drawBlood(app):
    size = app.margin*2
    drawImage(app.bloodStains[0], app.width/4*3, app.height-app.margin/2,
              align = 'center', width = size, height = size)
    drawImage(app.bloodStains[1], app.margin/2, app.height/2,
              align = 'center', width = size, height = size)
    drawImage(app.bloodStains[2], app.width-app.margin, app.margin/2,
              align = 'center', width = size, height = size)

# Bonus helper that sets the interval between panic events
def refillPanicBag(app):
    bag = []
    for _ in range(app.panicBagSize):
        bag.append(random.randint(app.panicMinPieces, app.panicMaxPieces))
    random.shuffle(bag)
    app.panicBag = bag

# Bonus helper that picks the interval and updates the bag
def popNextPanicInterval(app):
    if app.panicBag == []:
        refillPanicBag(app)
    return app.panicBag.pop()

# Helper that stops the panic effects
def stopBonusEffects(app):
    app.panicActive = False
    app.panicTimer = 0

    app.flashOn = False
    app.flashCounter = 0

    if app.panicSoundPlaying:
        app.panicSound.pause()
        app.panicSoundPlaying = False
    
# Helper that initializes the jumpscare
def startJumpscare(app):
    # cancel bonus effects
    stopBonusEffects(app)

    app.jumpscareActive = True
    app.jumpscareTimer = app.jumpscareDuration

    # play scream once
    app.scareSound.play(restart=True)
    
def onStep(app):
    if app.isGameOver:
        return
    
    # Bonus
    if app.jumpscareActive:
        app.jumpscareTimer -= 1
        if app.jumpscareTimer <= 0:
            app.jumpscareActive = False
            app.isGameOver = True
        return

    if app.bonus and app.panicActive:
        app.panicTimer -= 1
        
        # If timer runs out, you lose
        if app.panicTimer <= 0:
            startJumpscare(app)
            return
            
        # Flash cues    
        app.flashCounter += 1
        if app.flashCounter >= app.flashPeriod:
            app.flashCounter = 0
            app.flashOn = not app.flashOn
    
    app.stepCounter += 1
    if app.stepCounter < app.stepsPerDrop:
        return
    
    app.stepCounter = 0
    
    if not moveFallingPiece(app, 1, 0):
        placeFallingPiece(app) # place existing piece
        newFallingPiece(app) # generate the next piece
        if not fallingPieceLegal(app):
            stopBonusEffects(app)
            app.isGameOver = True # immediately illegal -> game over
            

def onKeyPress(app, key):
    if key == 'r':
        onAppStart(app)
        return
    
    if key == 'b':
        app.bonus = not app.bonus
        if app.bonus:
            printBonusInstructions()
        else:
            print("BONUS MODE DEACTIVATED")
            stopBonusEffects(app) # Immediately cancel all panic event states
            app.jumpscareActive = False
            app.jumpscareTimer = 0
        return
    
    if app.isGameOver:
        return
    
    if key == 'left':
        moveFallingPiece(app, 0, -1)
    elif key == 'right':
        moveFallingPiece(app, 0, 1)
    elif key == 'down':
        moveFallingPiece(app, 1, 0)
    elif key == 'up':
        rotateFallingPiece(app)
    elif key == 'space':
        # Bonus
        if app.bonus and app.panicActive:
            stopBonusEffects(app)
        
        # Normal hard drop
        while moveFallingPiece(app, 1, 0):
            pass
        placeFallingPiece(app)
        newFallingPiece(app)
        if not fallingPieceLegal(app):
            app.isGameOver = True
        

def printBonusInstructions():
    print("""\
BONUS MODE ACTIVATED: HORROR TETRIS

!!! PLAYER DISCRETION ADVISED !!!
This bonus mode contains flashing visuals, intense sound effects,
and a sudden jumpscare image. Please enable at your own discretion.

What changes in bonus mode:
1) Random "PANIC" events occur.
   - The screen flashes briefly.
   - Intense audio plays during the panic state.
   - You MUST press SPACE immediately to hard-drop the current piece.
   - If you fail to press SPACE in time, a jumpscare appears and the game ends.

Controls:
- arrow keys: move/rotate as normal
- space: hard drop (also used to survive PANIC)
- r: restart
- b: toggle bonus mode
""")

playTetris()
    
    