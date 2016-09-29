from AgentExternals import *
from captureAgents import CaptureAgent
from game_code.capture import SIGHT_RANGE


class BaseAgent(object, CaptureAgent):
    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        CaptureAgent.registerInitialState(self, gameState)

        # set up data repository
        if self.red:
            if not TeamData.RedData:
                TeamData.RedData = TeamData(gameState, self.getTeam(gameState), self.getOpponents(gameState), self)
            self.data = TeamData.RedData

        else:
            if not TeamData.BlueData:
                TeamData.BlueData = TeamData(gameState, self.getTeam(gameState), self.getOpponents(gameState), self)
            self.data = TeamData.BlueData

        self.legalPositions = self.data.legalPositions

    # TODO: Check to see if this should be more utility-esque
    # creates exclusion zones around enemy ghosts
    def genExclusionZones(self, gamestate, beliefs=None):
        if not beliefs:
            beliefs = self.getBeliefs()
        # list of enemy ghosts we need to avoid
        enemy_ghosts = [g for g in self.getOpponents(gamestate) if
                        not gamestate.getAgentState(g).isPacman and
                        gamestate.getAgentState(g).scaredTimer == 0]  # if ghosts are scared, no exclusion zone
        my_pos = self.getMyPos(gamestate)
        zone = set()
        if not enemy_ghosts:  # short circuit if no enemy ghosts
            return zone
        # easy way to get all enemy spaces is to get the keys of border distances
        for space in self.data.borderDistances.keys():
            # check each enemy
            for enemy in enemy_ghosts:
                # if this spot is closer to the enemy then it is to us, then don't go there
                # currently is very extreme rule, might need to be tuned in the future
                # TUNE 1: only matters if space is nearer than 7, otherwise initial search has no food it can go to
                if self.getDistanceToEnemy(space, enemy, beliefs[enemy]) <= self.getMazeDistance(my_pos, space) < 7:
                    zone.add(space)
                    break
        # Note: if needed, can probably rig up a way to color the map with these by pretending they're belief distributions

        return zone

    def pathToHome(self, gamestate, beliefs):

        # find shortest path to home
        # generate exclusion zones around the enemies, find shortest path that doesn't go through an exclusion zone

        ez = self.genExclusionZones(gamestate, beliefs)

        goHomeProb = PacmanPosSearch(self.getMyPos(gamestate), self.data.borderPositions, gamestate, ez)

        def heuristic(state, problem):
            if state in self.data.borderDistances:
                return self.data.borderDistances[state]
            else:
                return 0

        path, _ = search.astar(goHomeProb, heuristic)
        if not path:
            # # relax the exclusion zones to only be where the enemy is
            # ghp2 = PacmanPosSearch(self.getMyPos(gamestate), self.data.borderPositions, gamestate,
            #                        list(self.knownEnemies.values()))
            # path, _ = search.astar(ghp2, heuristic)
            # if not path:
            #     # still no path home, probably screwed, just stop and pray
            #     path = [game.Directions.STOP]  # just wait, because can't go anywhere
            # # hollup
            pass
        return path  # return the first action in the path



    #######################################
    #        Utility Info Functions
    #######################################

    # <editor-fold desc="Utility Info">

    def getDistToNearestTeammate(self, gameState):
        return min([self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),
                                         gameState.getAgentState(agent).getPosition()) for agent in
                    self.getTeam(gameState) if agent != self.index])

    def getDistToNearestCapsule(self, gameState):
        try:
            return min([self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), cap) for cap in
                        self.getCapsules(gameState)])
        except ValueError:
            return 0

    def getScaredMovesRemaining(self, gameState):
        return gameState.getAgentState(self.index).scaredTimer

    def getEnemyAgentScaredMovesRemaining(self, gameState):
        return [gameState.getAgentState(o).scaredTimer for o in self.getOpponents(gameState)]

    def getFoodEatenByEnemyAgent(self, gameState, agentIndex):
        return gameState.getAgentState(agentIndex).numCarrying

    # food in our stomach
    def getFoodEatenBySelf(self, gameState):
        return gameState.getAgentState(self.index).numCarrying

    # checks which side of the board a given position is, returns true if its my side
    def onMySide(self, pos):
        halfway = self.getCurrentObservation().data.food.width / 2
        # copied from halfgrid
        # see comment on halfway in agent data
        if self.red:
            return pos[0] < halfway
        else:
            return pos[0] >= halfway

    # calculates the most likely distance between spos and the given enemy, using the given belief distribution
    # if given belief distribution is None, it will use the current agent distribution
    # if the position of that enemy is known, then the exact distance is returned
    # otherwise, the distance returned is the sum over all possible positions
    # of the product of the probability the enemy is at that position and the distance to that position
    def getDistanceToEnemy(self, spos, enemyI, beliefs=None):
        if not beliefs and enemyI in self.knownEnemies:
            return self.getMazeDistance(spos, self.knownEnemies[enemyI])
        else:
            if not beliefs:
                beliefs = self.getmDistribs(enemyI)

            weighted_dists = [prob * self.getMazeDistance(spos, epos) for epos, prob in beliefs.items() if prob > 0]
            if weighted_dists:
                return sum(weighted_dists)
            else:
                # we don't have any idea where the enemy is, but we know he's at least sight range units away, so return that
                return SIGHT_RANGE + 1

    # get the distance from this agents position in gamestate to the enemy with index enemyI
    # see 'getDistanceToEnemy' for details
    def getMyDistanceToEnemy(self, gamestate, enemyI, beliefs=None):
        return self.getDistanceToEnemy(self.getMyPos(gamestate), enemyI)

    def getMyPos(self, gameState):
        return gameState.getAgentPosition(self.index)

    # calculates the distance to the nearest food
    def calcFoodDist(self, gamestate):
        # TODO: consider improving this
        foodList = self.getFood(gamestate).asList()
        myPos = self.getMyPos(gamestate)
        if len(foodList):
            minDist = self.getMazeDistance(myPos, foodList[0])
            for pos in foodList:
                dist = self.getMazeDistance(myPos, pos)
                if dist < minDist:
                    minDist = dist
                    if dist == 1:
                        break
            return minDist
        else:
            return 0

    def getDistanceToHomeSide(self, gameState):
        myPos = self.getMyPos(gameState)
        return self.data.borderDistances[myPos] if myPos in self.data.borderDistances else 0

    def calcEnemyFoodDist(self, gamestate, enemyI, beliefs=None):
        foodList = self.getFoodYouAreDefending(gamestate).asList()
        if not foodList:
            return 0
        return min(self.getDistanceToEnemy(food, enemyI, beliefs) for food in foodList)

    def calcEnemyCapsuleDist(self, gamestate, enemyI, beliefs=None):
        try:
            return min([self.getDistanceToEnemy(cap, enemyI, beliefs) for cap in
                        self.getCapsulesYouAreDefending(gamestate)])
        except ValueError:
            return 0

    def getEnemyDistToHome(self, gamestate, enemyI, beliefs=None):
        if not gamestate.getAgentState(enemyI).isPacman:
            return 0
        elif not beliefs and enemyI in self.knownEnemies:
            return self.data.e_borderDistances[self.knownEnemies[enemyI]]
        else:
            if not beliefs:
                beliefs = self.getmDistribs(enemyI)

            weighted_dists = [prob * self.data.e_borderDistances[epos] for epos, prob in beliefs.items() if prob > 0
                              and epos in self.data.e_borderDistances]
            if weighted_dists:
                return sum(weighted_dists)
    # </editor-fold>


    ##################################################
    #       POSITION INFERENCE
    ##################################################



    def _setKnownPosDist(self, agentIndex, knownPos):
        self.knownEnemies[agentIndex] = knownPos
        dist = self.getmDistribs(agentIndex)
        dist.clear()
        dist[knownPos] = 1.0

    def _capturedAgent(self, agentIndex):
        self._setKnownPosDist(agentIndex, self.getCurrentObservation().getInitialAgentPosition(agentIndex))

    def getPrevPlayer(self):
        return (self.index - 1) % self.getCurrentObservation().getNumAgents()

    # if this causes a significant slowdown, can just add mDistribs attribute to this class, initialize as ref to data
    def getmDistribs(self, agentIndex):
        return self.data.mDistribs[agentIndex]

    def getBeliefs(self):
        return self.data.mDistribs

    def setDistrib(self, agentIndex, newDistrib):
        i = 3
        for p in newDistrib.keys():
            if p not in self.data.legalPositions:
                pass
        self.data.mDistribs[agentIndex] = newDistrib

    # does inference based on noisy distance to agents and updates opponents distributions
    def positionDistanceInfer(self, agentIndex, gameState=None):
        if not gameState:
            gameState = self.getCurrentObservation()
        # myState=gameState.getAgentState(self.index)

        # noisyDistance = observation
        # emissionModel = busters.getObservationDistribution(noisyDistance)
        myPos = self.getMyPos(gameState)

        noisyDistance = gameState.getAgentDistances()[agentIndex]
        beliefs = self.getmDistribs(agentIndex)
        allPossible = util.Counter()

        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, myPos)
            if beliefs[p] == 0:
                # don't need to do anything
                pass
            elif trueDistance <= SIGHT_RANGE:
                # agent would be visible if it were here, so its not here
                allPossible[p] = 0
            # if this position is not on the side of the board the agent is currently on, then the agent isn't at this location
            elif self.onMySide(p) != gameState.getAgentState(agentIndex).isPacman:
                allPossible[p] = 0
            # NOTE: original code had the check below, but this isn't a good idea because if that prob is 0, the belief
            # for p should be updated with that in mind, so this check is silly.
            # elif gameState.getDistanceProb(trueDistance, noisyDistance)>0: #only do anything if there is any possibility of getting the given noisy distance from this true distance
            else:
                allPossible[p] = beliefs[p] * gameState.getDistanceProb(trueDistance, noisyDistance)

        allPossible.normalize()
        self.setDistrib(agentIndex, allPossible)

    # does inference based on where the agent could move to and updates opponents distributions
    def positionMoveInfer(self, agentIndex, gameState=None, beliefs=None):
        if not gameState:
            gameState = self.getCurrentObservation()
        if not beliefs:
            beliefs = self.getmDistribs(agentIndex)
        # myState=gameState.getAgentState(self.index)
        myPos = self.getMyPos(gameState)

        possiblePositions = util.Counter()
        # TODO: see if this can be made more efficient by iterating over beliefs.keys or something, to avoid checking stupid legal positions
        for pos in self.legalPositions:
            # if the distance is less than SIGHT_RANGE, don't need to do inference on this position, bc we know the agent isn't there
            if beliefs[pos] > 0:
                newPosDist = self.getPositionDistribution(pos, gameState)
                for position, prob in newPosDist.items():
                    possiblePositions[position] += prob * beliefs[pos]

        possiblePositions.normalize()
        return possiblePositions

    # returns a probability distribution for the agents subsequent position, given that it is at curPos
    def getPositionDistribution(self, curPos, gameState=None):
        if not gameState:
            gameState = self.getCurrentObservation()
        neighbors = game.Actions.getLegalNeighbors(curPos, gameState.getWalls())
        probs = {}
        # currently assumes agressively moves towards closest "objective" (food or pacman) with probability .8
        objectives = self.data.defendFoodGrid[-1].asList()
        for i in self.getTeam(gameState):
            if gameState.getAgentState(i).isPacman:
                objectives.append(gameState.getAgentPosition(i))

        minDist = self.getMazeDistance(neighbors[0], objectives[0])
        bestNeighbor = neighbors[0]
        # find the neighbor that is closest to an objective
        for obj in objectives:
            for neighbor in neighbors:
                if self.getMazeDistance(obj, neighbor) < minDist:
                    bestNeighbor = neighbor
        defProb = .8
        otherProbs = (1 - defProb) / (len(neighbors) - 1)
        # set the probability we move to a neighbor that is not bestNeighbor to the correct value
        for n in neighbors:
            probs[n] = otherProbs
        probs[bestNeighbor] = defProb

        return probs

    # compares the most recent food log to the one before it, looking for any food that disappeared
    def checkFood(self):
        # TODO: Appears to be a place this is tracked by game, look at capture.py line 555
        if len(self.data.defendFoodGrid) < 2:
            return False
        prevFood = self.data.defendFoodGrid[-2]
        currFood = self.data.defendFoodGrid[-1]
        halfway = currFood.width / 2
        # copied from halfgrid
        if self.red:
            xrange = range(halfway)
        else:
            xrange = range(halfway, currFood.width)
        # TODO: can check numCarrying of previous agent to see if it changed, only do this check if it ate food
        for y in range(currFood.height):
            for x in xrange:
                if prevFood[x][y] and not currFood[x][y]:
                    # food has been eaten in the past move
                    self._setKnownPosDist(self.getPrevPlayer(), (x, y))
                    return True

    # checks if we can see either of the opponents, if so, updates their belief state and doesn't do inference
    # if not, does inference
    def updatePosDist(self, gameState=None):
        if not gameState:
            gameState = self.getCurrentObservation()
        for i in self.getOpponents(gameState):
            if gameState.getAgentPosition(i):  # can observe the given agent
                self._setKnownPosDist(i, gameState.getAgentPosition(i))

            # Only do move infer on the agent right before the current agent, as both agents haven't moved since last call
            # (if this is agent 3, agent 2 just moved, but agent 4 has not moved since agent 1 did inference.
            elif self.getPrevPlayer() == i:  # i is the previous agent
                if self.index == 0 and self.getPreviousObservation() == None:  # this is the first move, don't do inference
                    pass
                else:
                    # check if any food was eaten. If so, don't do inference. if not, do inference
                    if not self.checkFood():
                        # positionDistanceInfer returns the new distribution, so update the saved distribution
                        self.setDistrib(i, self.positionMoveInfer(i))
                        self.positionDistanceInfer(i)

            else:
                # do inference based on distance
                self.positionDistanceInfer(i)
