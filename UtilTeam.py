import logging
from collections import namedtuple
from datetime import datetime

from recordclass import recordclass

from AgentExternals import *
from BaseAgent import BaseAgent
from captureAgents import CaptureAgent
from game_code.capture import SIGHT_RANGE

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
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


class HLA:
    #due to dependency issues, set the members of HLA inside HardwiredAgent
    pass
    # set each of the HLAs to the method in HardwiredAgent that defines the behavior in that case
    # calling each of these should just require passing in the current object as the self parameter


class UtilAgent(object, BaseAgent):
    def registerInitialState(self, gameState):
        super(UtilAgent).registerInitialState(gameState)
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
                                       "safe_path_to_home", "e_dist_to_food"])

    #TODO: add the following features:
        #enemy distance to food
        #enemy distance to capsule

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
            path_home = self.pathToHome(gamestate, belief_distrib)
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



        # called when the agent should procede home

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
        return path # return the first action in the path

    # </editor-fold>






