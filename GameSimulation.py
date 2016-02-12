from decimal import Decimal

BOARD_SIZE = 5
NEXT_STATE = "next_state.txt"
INFINITY = Decimal("inf")
NEG_INFINITY = Decimal("-inf")
TRAVERSE_LOG = "traverse_log.txt"
TRACE_STATE = "trace_state.txt"

#Method to map the values of the board cells
def MapValueToBoard(row, col, trace, NodeDepth, NodeValue, AlphaBeta, node):

    if 0 == col:
        trace = "A"+str(row+1)
    elif 1 == col:
        trace = "B"+str(row+1)
    elif 2 == col:
        trace = "C"+str(row+1)
    elif 3 == col:
        trace = "D"+str(row+1)
    elif 4 == col:
        trace = "E"+str(row+1)
    else:
        trace = "root"
    
    trace = trace+","+str(NodeDepth)+","+str(NodeValue)

    if AlphaBeta:
        trace += ","+str(node.alpha)+","+str(node.beta)

    return trace

#Print the node, node depth, node values
def WriteFile(node, alphabeta=False):
    row = node.pos[0]
    col = node.pos[1]
    NodeDepth = node.depth
    NodeValue = node.score
    trace = ""
    trace = MapValueToBoard(row, col, trace, NodeDepth, NodeValue, alphabeta, node)
    
    return trace


class Node(object):

    def __init__(this, score, pos, piece, depth=0, parent=None):
        this.depth = depth
        this.parent = parent

        this.score = score
        this.pos = pos
        this.piece = piece
        
        this.nextMove = None
        this.children = None

    def AttachDescendants(this, node):
        node.parent = this
        node.depth = this.depth + 1
        if this.children == None:
            this.children = []

        this.children.append(node)




class BoardGame(object):
    def __init__(this, prob_file):

        this.AvailableCell = '*'                        
        this.opponent = lambda piece: 'X' if piece == 'O' else 'O'

        
        with open(prob_file) as fileRead:
            ReadCount = 0
            lines = fileRead.readlines()
            
            this.GameMode = int(lines[0].strip())

            if this.GameMode >= 4:
                this.myPlayer = lines[1].strip()
                this.myPlayerAlgorithm = int(lines[2].strip())
                this.myPlayerCutOffDepth = int(lines[3].strip())

                this.oppPlayer = lines[4].strip()
                this.oppPlayerAlgorithm = int(lines[5].strip())
                this.oppPlayerCutOffDepth = int(lines[6].strip())
                ReadCount = 7

            if this.GameMode <= 3:
                this.myPawn = lines[1].strip()
                this.oppPawn = this.opponent(this.myPawn)
                this.cutoffDepth = int(lines[2].strip())
                ReadCount = 3

            this.boardValues = [[int(j) for j in lines[ReadCount + i].strip().split()]
                          for i in range(BOARD_SIZE)]
            ReadCount += 5

            this.boardState = [[j for j in lines[ReadCount + i].strip()]
                              for i in range(BOARD_SIZE)]

    def isGameFinished(this, boardState):

        for row, col in this.GetCells():
            if '*' == boardState[row][col]:
                return False

        return True

    def printboardState(this, boardState, stateFile):
        state = ""
        
        for row in boardState:
            for cell in row:
                state += cell
            state += "\n"

        if stateFile:
            with open(stateFile, 'w') as wr:
                wr.write(state)
        return state


    def CalculateScore(this, boardState, myPlayer, oppPlayer, score):
        for (row, col) in this.GetCells():
            if boardState[row][col] == myPlayer:
                score += this.boardValues[row][col]
            elif boardState[row][col] == oppPlayer:
                score -= this.boardValues[row][col]

        return score

    def getMyScore(this, row, col, score):
        score += this.boardValues[row][col]
        return score

    def getOppScore(this, row, col, score):
        score -= this.boardValues[row][col]
        return score


    def evaluateboardState(this, boardState, player):
        score = 0
        opponent = this.opponent(player)
        score = this.CalculateScore(boardState, player, opponent, score)

        return score

    def NextboardStateHeuristic(this, boardState, myPlayer):
        
        oppPawn = this.opponent(myPlayer)
        GameHeur = [[None for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]

        currentScore = this.evaluateboardState(boardState, myPlayer)
        for row, col in this.GetCells():
            if boardState[row][col] == this.AvailableCell:  

                GameHeur[row][col] = currentScore + this.boardValues[row][col]
                raid = False

                adjacent_cells = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
                
                MyGain = 0
                for HorCell, VerCell in adjacent_cells:
                    if 0 <= HorCell < BOARD_SIZE and 0 <= VerCell < BOARD_SIZE:
                        if boardState[HorCell][VerCell] == myPlayer:
                            raid = True
                        elif boardState[HorCell][VerCell] == oppPawn:
                            MyGain += this.boardValues[HorCell][VerCell]
                        
                if raid:
                    GameHeur[row][col] = GameHeur[row][col] + (2 * MyGain)

        return GameHeur

    def GetCells(this):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                yield (row, col)

    def findEmptyCells(this, boardState):
        EmptyCells = []
        for i in range(BOARD_SIZE):
           for j in range(BOARD_SIZE):
                if '*' == boardState[i][j]:
                    EmptyCells.append((i, j))
        return EmptyCells

    def MoveType(this, HorzVertCells, boardState, myPlayer, oppPawn, RemoveLog):
        raid = False
        oppCells = []
        for row, col in HorzVertCells:
            if 0 <= row < BOARD_SIZE and  0 <= col < BOARD_SIZE:
                if boardState[row][col] == oppPawn:
                    oppCells.append((row, col))
                elif boardState[row][col] == myPlayer:
                    raid = True
        if raid:
            for m, n in oppCells:
                boardState[m][n] = myPlayer
                RemoveLog.append((m, n, oppPawn))



    def AggresiveMove(this, myPlayer, row, col, boardState ):
        oppPawn = this.opponent(myPlayer)
        RemoveLog = []
        if boardState[row][col] == this.AvailableCell:

            this.boardState[row][col] = myPlayer
            RemoveLog.append((row, col, this.AvailableCell))

            HorzVertCells = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
            this.MoveType(HorzVertCells, boardState, myPlayer, oppPawn, RemoveLog)
       

        return RemoveLog

    

    def greedyBFS(this,player):
        
        GameHeur = this.NextboardStateHeuristic(this.boardState, player)
        pos = None
        maxVal = NEG_INFINITY
        

        for row, col in this.GetCells():
            if GameHeur[row][col] != None:
                if GameHeur[row][col] > maxVal:
                    maxVal = GameHeur[row][col]
                    position = (row, col)
        if position:
            return this.AggresiveMove(player, position[0], position[1], this.boardState)
    
    def PlayGame(this, logfile, GameAlgorithm):
        
        if GameAlgorithm == 3:
            root = AlphaBetaMode(this,this.myPawn,this.oppPawn,this.cutoffDepth, logfile).alphabetaBegin(this.boardState)
        
        
        elif GameAlgorithm == 2:
            root = MiniMaxMode(this,this.myPawn,this.oppPawn,this.cutoffDepth, logfile).minimaxBegin(this.boardState)
           
        
        if root.nextMove:
            move = root.nextMove
            this.AggresiveMove(move.piece, move.pos[0], move.pos[1], this.boardState )
    


        
    def miniMax(this,logfile):
        GameAlgorithm = 2
        this.PlayGame(logfile, GameAlgorithm)

    def alphaBetaPruning(this,logfile):
        GameAlgorithm = 3
        this.PlayGame(logfile, GameAlgorithm)

    def gameSimulation(this):
        turn = 0
        with open(TRACE_STATE, 'w') as out:
            while not this.isGameFinished(this.boardState):
                if turn % 2 == 1:
                    this.playerTurn(this.oppPlayerAlgorithm, this.oppPlayer, this.myPlayer, this.oppPlayerCutOffDepth)
                else:
                    this.playerTurn(this.myPlayerAlgorithm, this.myPlayer, this.oppPlayer, this.myPlayerCutOffDepth)
                
                if turn > 0:
                    out.write("\r\n")

                res = this.printboardState(this.boardState,None).strip()
                out.write(res)
                turn += 1

    def playerTurn(this, GameMode, player, opponent, cutoffDepth):

        if 1 == GameMode:
            this.greedyBFS(player)
        elif 3 == GameMode:
            move = AlphaBetaMode(this, player, opponent, cutoffDepth,None).alphabetaBegin(this.boardState).nextMove
            this.AggresiveMove( move.piece, move.pos[0], move.pos[1], this.boardState)
        elif 2 == GameMode:
            move = MiniMaxMode(this, player, opponent, cutoffDepth,None).minimaxBegin(this.boardState).nextMove
            this.AggresiveMove(move.piece, move.pos[0], move.pos[1], this.boardState )
            pass


    def nextMove(this, algorithm):
        
        if algorithm == 2:
            with open(TRAVERSE_LOG, 'w') as logfile:
                this.miniMax(logfile)
                
        elif algorithm == 3:
            with open(TRAVERSE_LOG, 'w') as logfile:
                this.alphaBetaPruning(logfile)
        elif algorithm == 1:
            this.greedyBFS(this.myPawn)
                
        elif algorithm == 4:
            this.gameSimulation()

        if algorithm == 1 or algorithm == 2 or algorithm == 3:
            problem.printboardState(problem.boardState, NEXT_STATE)

    def readboardStateFile(this, fileName, n):
        with open(fileName) as f:
            return [[j for j in next(f).strip()] for _ in range(n)]

    def areboardStatesSame(this, boardState1, boardState2):
        for i, j in this.GetCells():
            if boardState1[i][j] != boardState2[i][j]:
                return False
        return True


class MiniMaxMode(object):

    def __init__(this, problem, maxPlayer, minPlayer, cutoffDepth, logfile):
        this.maxPlayer = maxPlayer
        this.logfile = logfile
        this.evaluateboardState = lambda boardState : problem.evaluateboardState(boardState, maxPlayer)
        
        this.minPlayer = minPlayer
        this.maxdepth = cutoffDepth
        this.problem = problem
    
    
    def minimaxBegin(this, boardState):
        this.WriteLogHeader(this.logfile)
        ancestor = Node(NEG_INFINITY, (None, None), None)
     
        this.MinimaxMax(boardState, ancestor)
        return ancestor

    def AttachMinAndUpdate(this, emptycells, ancestor, boardState):
        for cell, (row, col) in enumerate(emptycells):
            RemoveMove = this.problem.AggresiveMove(this.minPlayer, row, col, boardState )     
            descendant = Node(NEG_INFINITY, (row, col), this.minPlayer)
            ancestor.AttachDescendants(descendant)
            this.MinimaxMax(boardState, descendant)                             
            if descendant.score < ancestor.score:
                ancestor.score = descendant.score
                ancestor.nextMove = descendant
            this.WriteLog(cell, emptycells, this.logfile, ancestor, RemoveMove, boardState)


    def MinimaxMin(this, boardState, ancestor):
        emptycells = this.problem.findEmptyCells(boardState)
        if ancestor.depth == this.maxdepth or not emptycells:
            ancestor.score = this.evaluateboardState(boardState)
        else:
            if this.logfile:
                this.logfile.write("\n" + WriteFile(ancestor))
            this.AttachMinAndUpdate(emptycells, ancestor, boardState)
               
        if this.logfile:
            this.logfile.write("\n" + WriteFile(ancestor))
        return ancestor.score

    def AttachMaxAndUpdate(this, emptycells, ancestor, boardState):
        for cell, (i, j) in enumerate(emptycells):
            RemoveMove = this.problem.AggresiveMove(this.maxPlayer, i, j, boardState )    
            descendant = Node(INFINITY, (i, j), this.maxPlayer)
            ancestor.AttachDescendants(descendant)
            descendant.score = this.MinimaxMin(boardState, descendant)              
            if descendant.score > ancestor.score:
                ancestor.score = descendant.score
                ancestor.nextMove = descendant
                
            this.WriteLog(cell, emptycells, this.logfile, ancestor, RemoveMove, boardState)

    def MinimaxMax(this, boardState, ancestor):
        emptycells = this.problem.findEmptyCells(boardState)
        if ancestor.depth == this.maxdepth or not emptycells:
            ancestor.score = this.evaluateboardState(boardState)
        else:
            if this.logfile:
                this.logfile.write("\n" + WriteFile(ancestor))
            this.AttachMaxAndUpdate(emptycells, ancestor, boardState)

        if this.logfile:
            this.logfile.write("\n" + WriteFile(ancestor))
        return ancestor.score



    def WriteLog(this, cell, cells, logfile, ancestor, RemoveMove, boardState):
        if cell < len(cells) -1: 
                    if this.logfile:
                        this.logfile.write("\n" + WriteFile(ancestor))
        for a in RemoveMove:
            boardState[a[0]][a[1]] = a[2]


    def WriteLogHeader(this, logfile):
        if logfile:
            logfile.write("Node,Depth,Value")    


class AlphaBetaMode(MiniMaxMode):

    
    def alphabetaBegin(this, boardState):
        this.WriteLogHeader(this.logfile)
        ancestor = Node(NEG_INFINITY, (None, None), None) 

        ancestor.beta = INFINITY
        ancestor.alpha = NEG_INFINITY                     
                            
        this.AlphabetaMax(boardState, ancestor)
        
        return ancestor

    def WriteLog(this, logfile, ancestor):
        if this.logfile:
            this.logfile.write("\n" + WriteFile(ancestor, True))


    def AlphabetaMin(this, boardState, ancestor):
        emptycells = this.problem.findEmptyCells(boardState)
        
        if ancestor.depth == this.maxdepth or not emptycells:
            ancestor.score = this.evaluateboardState(boardState)
        else:
            this.WriteLog(this.logfile, ancestor)
            for cell, (row, col) in enumerate(emptycells):
                RemoveMove = this.problem.AggresiveMove(this.minPlayer, row, col, boardState)     

                descendant = Node(NEG_INFINITY, (row, col), this.minPlayer)
                
                descendant.beta = ancestor.beta

                descendant.alpha = ancestor.alpha
               
                this.AttachABMin(ancestor, descendant, boardState, RemoveMove)
                if descendant.score < ancestor.score:
                    ancestor.score = descendant.score
                    ancestor.nextMove = descendant
                if descendant.score <= ancestor.alpha:
                    break
                if descendant.score < ancestor.beta:
                    ancestor.beta = descendant.score

                if cell < len(emptycells) -1: 
                    this.WriteLog(this.logfile, ancestor)
        
        this.WriteLog(this.logfile, ancestor)
        return ancestor.score

    def AlphabetaMax(this, boardState, ancestor):
        emptycells = this.problem.findEmptyCells(boardState)
        if ancestor.depth == this.maxdepth or not emptycells:
            ancestor.score = this.evaluateboardState(boardState)
        else:
            this.WriteLog(this.logfile, ancestor)
            for cell, (row, col) in enumerate(emptycells):
                RemoveMove = this.problem.AggresiveMove(this.maxPlayer, row, col, boardState )    
                descendant = Node(INFINITY, (row, col), this.maxPlayer)     

                descendant.beta = ancestor.beta
                descendant.alpha = ancestor.alpha                        
                
                this.AttachABMax(ancestor, descendant, boardState, RemoveMove)

                if descendant.score > ancestor.score:
                    ancestor.score = descendant.score
                    ancestor.nextMove = descendant
                if descendant.score >= ancestor.beta: 
                    break
                if descendant.score > ancestor.alpha:
                    ancestor.alpha = descendant.score

                if cell < len(emptycells) - 1:         
                    this.WriteLog(this.logfile, ancestor)
        
        this.WriteLog(this.logfile, ancestor)

        return ancestor.score


    def AttachABMax(this, ancestor, descendant, boardState, RemoveMove):
        ancestor.AttachDescendants(descendant)                          
        this.AlphabetaMin(boardState, descendant)              
        for a in RemoveMove:
            boardState[a[0]][a[1]] = a[2]

    def AttachABMin(this, ancestor, descendant, boardState, RemoveMove):
        ancestor.AttachDescendants(descendant)
        this.AlphabetaMax(boardState, descendant)                             
                
        for a in RemoveMove:
            boardState[a[0]][a[1]] = a[2] 
            
            

    def WriteLogHeader(this, logfile):
        if logfile:
            logfile.write("Node,Depth,Value,Alpha,Beta")



import sys
problem = BoardGame(sys.argv[2])
problem.nextMove(problem.GameMode)