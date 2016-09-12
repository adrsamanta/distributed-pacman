from collections import namedtuple
from recordclass import recordclass

import search
from capture import SIGHT_RANGE
from captureAgents import CaptureAgent
import random, util
import game
from AgentExternals import *
import logging
from datetime import datetime

timestamp='{:%m-%d_%H.%M.%S}'.format(datetime.now())
logger = logging.getLogger("base")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("logs/all_"+timestamp+".txt"))

#currently not in use, will use later if needed
# off_log = logging.getLogger("base.offense")
# offense_handler=logging.FileHandler("logs/offense_"+timestamp+".txt")
# off_log.addHandler(offense_handler)
#
# def_log = logging.getLogger("base.defense")
# defense_handler=logging.FileHandler("logs/defense_"+timestamp+".txt")
# def_log.addHandler(defense_handler)


def createTeam(firstIndex, secondIndex, isRed,
               first='UtilAgent', second='UtilAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


class HLA:
    #due to dependency issues, set the members of HLA inside HardwiredAgent
    pass
    # set each of the HLAs to the method in HardwiredAgent that defines the behavior in that case
    # calling each of these should just require passing in the current object as the self parameter


class UtilAgent(CaptureAgent):
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
        # set the members of HLA to the HardwiredAgent methods
        # HLA.goHome = HardwiredAgent.goHomeAction
        # HLA.runAway = None
        # HLA.eatFood = HardwiredAgent.eatFoodAction
        # HLA.chaseEnemy = HardwiredAgent.chasePacmanAction
        # HLA.eatCapsule = HardwiredAgent.eatCapsuleAction

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
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
        self.offensive = self.data.getOffensive()
        if self.offensive:
            self.logger = logger
        else:
            self.logger = logger


        # set up distribution list that will hold belief distributions for agents

    def chooseAction(self, gameState):
        self.logger.info("Beginning new move")
        self.knownEnemies = {}  # enemy position, key is enemy index
        self.data.logFood(gameState)
        self.updatePosDist(gameState)
        if self.getScaredMovesRemaining(gameState) > 2:
            self.offensive = True
        elif self.getScaredMovesRemaining(gameState) == 1:
            self.offensive = self.data.getOffensive()
        # print "infer time: ", time()-startTime
        self.displayDistributionsOverPositions(self.data.mDistribs)
        action = self.action_search(gameState)
        new_pos = game.Actions.getSuccessor(self.getMyPos(gameState), action)
        if new_pos in self.knownEnemies.values():
            for e, p in self.knownEnemies.items():
                if new_pos==p:
                    self._capturedAgent(e)
        return action

    def action_search(self, gamestate):
        #how much to discount future utility by, so if a state is 3 in the future, its utility is UTIL_DISCOUNT**3 * calculated_utility
        UTIL_DISCOUNT = .8

        #maximum depth of search
        MAX_SEARCH_DEPTH = 3
        #queue that holds future states to visit
        toVisit = util.Queue()
        #each item on toVisit is a tuple (starting action, gamestate, beliefs, depth, prev_action)
        #beliefs is the belief distribution of enemy positions at that point
        #prev action is the action taken to get to this state, to avoid checking the immediately previous position again
        State = namedtuple("State", ["starting_action", "gamestate", "beliefs", "depth", "prev_action"])


        #dictionary to track the utility of each state spawned off each starting action
        #action_utils[action] is a list of the utilities of all the states generated from this starting action
        action_utils = {}

        #create initial states
        legal_a=gamestate.getLegalActions(self.index)
        for action in legal_a:
            # if action == game.Directions.STOP and len(legal_a)>2:
            #     continue #only consider stop if there is only 1 alternative
            newgs = gamestate.generateSuccessor(self.index, action)
            toVisit.push(State(action, newgs, self.data.mDistribs, 0, action))
            action_utils[action]=[] #initialize action_utils for this action

        while not toVisit.isEmpty(): #while toVisit still has stuff in it
            #new "State" tuple
            ns = toVisit.pop()
            #calculate the utility of this state and add it to action utils
            self.logger.debug("\nconsidering position %s", self.getMyPos(ns.gamestate))
            nsu = self.getUtility(ns.gamestate, ns.beliefs)
            action_utils[ns.starting_action].append(nsu * UTIL_DISCOUNT**ns.depth)

            #only explore further if doesn't excede max search depth
            if ns.depth<MAX_SEARCH_DEPTH:
                successor_actions = ns.gamestate.getLegalActions(self.index)
                if len(successor_actions)>1:#if there are several subsequent actions, remove the 'double back' option
                    successor_actions.remove(game.Actions.reverseDirection(ns.prev_action))
                #the above code should, in the case that we went north to get here, and we can go either north or south
                #remove the option "south" from legal actions, so we do not needlessly double back
                #if however we entered a dead end, and we can thus only double back, it allows that to occur
                nsb = self.genNewBeliefs(ns.beliefs, ns.gamestate)  # generate the new beliefs for this state
                for action in successor_actions: #add all legal successors
                    newgs = ns.gamestate.generateSuccessor(self.index, action)

                    toVisit.push(State(ns.starting_action, newgs, nsb, ns.depth+1, action))

        #TODO: pick action based on highest average or highest sum?
        avg_action_util = [(u, sum(action_utils[u])/len(action_utils[u])) for u in action_utils.keys()]
        #TODO: figure out what to do here
        #trim all lists to be the same length
        #otherwise the action with the fewest possibilities will often win, as it's highest utility course will
        #pull the average more than that of the other courses
        min_length = min(len(x) for x in action_utils.values())

        new_pairs = {a : sorted(v, reverse=True)[:min_length] for a, v in action_utils.items()}
        avg_new_pair = [(u, sum(new_pairs[u])/len(new_pairs[u])) for u in new_pairs.keys()]
        best_action = max(new_pairs.keys(), key = lambda x:  sum(new_pairs[x])/len(new_pairs[x]))
        self.logger.info("Action: %s \n", best_action)
        return best_action


    #######################################
    #        Belief manipulation?
    #######################################

    def genNewBeliefs(self, oldBeliefs, gamestate):
        ### Limitations
        #Doesn't account for other players on this team moving
        #very basic move logic
        #doesn't update position in gamestate
        #TODO: Idea for updating pos in gs: have it move to a position with the assumed probability it goes there
            # TODO: (see position distribution, if goes .8 it goes to a place, it moves there w/ prob .8)
        ####
        nb = [None]*len(oldBeliefs)
        for i in self.getOpponents(gamestate):
            nb[i]=self.positionMoveInfer(i, gamestate, oldBeliefs[i])

        return nb
    #######################################
    #        Features/Weights
    #######################################

    # <editor-fold desc="Features/Weights stuff">
    Features = recordclass("Features", ["e_ghost_dist", "e_pac_dist", "food_dist", "capsule_dist", "score",
                                       "my_scared_moves", "enemy_scared_moves", "my_food", "home_dist", "enemy_food",
                                       "safe_path_to_home"])

    def getUtility(self, gamestate, belief_distrib):

        weights = self.getWeights(gamestate)
        features = self.getFeatures(gamestate, belief_distrib)
        util = 0
        for w, f, n in zip(weights, features, weights._fields):
            delta = w(gamestate, f)
            util+= delta
            self.logger.debug("Feature %s with value %s changed utility %f to new total %f", n, f, delta, util)
        return util

    #called weights, but really each entry is a function that calculates the utility from the given feature
    def getWeights(self, gamestate):
        #fill with dummy values
        weights = UtilAgent.Features(*range(len(UtilAgent.Features._fields)))

        def eghostutil(gs, ghost_dists):
            if gamestate.getAgentState(self.index).isPacman and ghost_dists:
                return min(-1./d for d in ghost_dists if d>0)
            else:
                return 0


        def epacutil(gs, pac_dists):
            u=0
            for d in pac_dists:
                if d>0:
                    u+=1./d
                else:
                    u+=1.3
            if len(pac_dists)==0:
                u+=1.3
            if self.offensive:
                return .5*u
            else:
                return u

        def efoodutil(gs, efl):
            return sum(-.8*ef for ef in efl)

        def home_dist(gs, d):
            mfood =  self.getFoodEatenBySelf(gamestate)
            if mfood>0:
                return .5*mfood*.8/d
            else:
                return 0

        def score_util(gs, s):
            if s!=0:
                return 1.8*s
            else:
                return -.5

        def food_dist_u(gs, d):
            if d>0:
                if self.getScore(gs)<=0:
                    return 1.7/d
                else:
                    return 1.3/d
            else:
                return 0

        weights.e_ghost_dist = eghostutil
        weights.e_pac_dist = epacutil
        weights.food_dist = food_dist_u
        weights.capsule_dist = lambda gs, d : .8/d if d>0 else 0
        weights.score = score_util
        weights.my_scared_moves = lambda gs, m : 0
        weights.enemy_scared_moves = lambda gs, m: .2*m
        weights.my_food = lambda gs, food: 1.2*food
        weights.home_dist = home_dist
        weights.enemy_food = efoodutil
        weights.safe_path_to_home = lambda gs, b: 1 if b else -1

        return weights

    #features of the current position
    def getFeatures(self, gamestate, belief_distrib):
        #flesh with dummy values
        feat = UtilAgent.Features(*range(len(UtilAgent.Features._fields)))

        e_ghost_dists=[]
        e_pac_dists=[]
        e_food=[]
        #do calculations that occur for each enemy
        for enemy in self.getOpponents(gamestate):
            # for each enemy, calculate the distance to them, then add that distance to the list corresponding to their mode
            dist = self.getMyDistanceToEnemy(gamestate, enemy, belief_distrib)
            if gamestate.getAgentState(enemy).isPacman:
                e_pac_dists.append(dist)
            else:
                e_ghost_dists.append(dist)

            e_food.append(gamestate.getAgentState(enemy).numCarrying)
        feat.e_ghost_dist = e_ghost_dists
        feat.e_pac_dist = e_pac_dists

        feat.food_dist = self.calcFoodDist(gamestate)

        feat.capsule_dist = self.getDistToNearestCapsule(gamestate)
        feat.score = self.getScore(gamestate)
        feat.my_scared_moves = self.getScaredMovesRemaining(gamestate)
        feat.enemy_scared_moves = self.getScaredMovesRemaining(gamestate) #TODO: factor this out into above loop?
        feat.my_food = self.getFoodEatenBySelf(gamestate)
        feat.enemy_food = e_food

        if self.onMySide(self.getMyPos(gamestate)):
            feat.safe_path_to_home=True
            feat.home_dist=0
        else:
            path_home = self.goHomeAction(gamestate, belief_distrib)
            if path_home:
                feat.safe_path_to_home = True
                feat.home_dist = len(path_home)
            else:
                #no safe path home
                feat.safe_path_to_home = False
                feat.home_dist = -1 #set to -1 to indicate bad value
        return feat
    # </editor-fold>


    #######################################
    #        Pathfinding Functions
    #######################################

    # <editor-fold desc="Pathfinding Stuff">

    #TODO: Check to see if this should be more utility-esque
    #creates exclusion zones around enemy ghosts
    def genExclusionZones(self, gamestate, beliefs):
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

        # called when the agent should procede home
    def goHomeAction(self, gamestate, beliefs):

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
        return path # return the first action in the path

    # </editor-fold>


    #######################################
    #        Utility Info Functions
    #######################################

    # <editor-fold desc="Utility Info">
    def getScaredMovesRemaining(self, gameState):
        return gameState.getAgentState(self.index).scaredTimer

    def getEnemyAgentScaredMovesRemaining(self, gameState):
        return [gameState.getAgentState(o).scaredTimer for o in self.getOpponents(gameState)]

    def getFoodEatenByEnemyAgent(self, gameState, agentIndex):
        return gameState.getAgentState(agentIndex).numCarrying

    #food in our stomach
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

    def getDistToNearestCapsule(self, gameState):
        try:
            return min([self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), cap) for cap in
                        self.getCapsules(gameState)])
        except ValueError:
            return 0

    #calculates the most likely distance between spos and the given enemy, using the given belief distribution
    #if given belief distribution is None, it will use the current agent distribution
    #if the position of that enemy is known, then the exact distance is returned
    #otherwise, the distance returned is the sum over all possible positions
    # of the product of the probability the enemy is at that position and the distance to that position
    def getDistanceToEnemy(self, spos, enemyI, beliefs=None):
        if not beliefs and enemyI in self.knownEnemies:
            return self.getMazeDistance(spos, self.knownEnemies[enemyI])
        else:
            if not beliefs:
                beliefs = self.getmDistribs(enemyI)

            weighted_dists = [prob*self.getMazeDistance(spos, epos) for epos, prob in beliefs.items() if prob>0]
            if weighted_dists:
                return sum(weighted_dists)
            else:
                #we don't have any idea where the enemy is, but we know he's at least sight range units away, so return that
                return SIGHT_RANGE+1

    #get the distance from this agents position in gamestate to the enemy with index enemyI
    #see 'getDistanceToEnemy' for details
    def getMyDistanceToEnemy(self, gamestate, enemyI, beliefs=None):
        return self.getDistanceToEnemy(self.getMyPos(gamestate), enemyI)

    def getMyPos(self, gameState):
        return gameState.getAgentPosition(self.index)

    #calculates the distance to the nearest food
    def calcFoodDist(self, gamestate):
        #TODO: consider improving this
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
        #TODO: see if this can be made more efficient by iterating over beliefs.keys or something, to avoid checking stupid legal positions
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



