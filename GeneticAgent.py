from LearnBase import LearnerBase
from collections import namedtuple
import util
from captureAgents import CaptureAgent
from game_code import game
import logging
from datetime import datetime

import re


def createTeam(firstIndex, secondIndex, isRed, weightvec1, weightvec2=None,
               first='GeneticAgent', second='GeneticAgent'):
    def createWeights(vec):
        weights = [float(f.group()) for f in re.finditer("\d", vec)]
        return weights

    floatvec1 = createWeights(weightvec1)
    if weightvec2:
        floatvec2 = createWeights(weightvec2)
    else:
        floatvec2 = createWeights(weightvec1)

    return [eval(first)(firstIndex, floatvec1), eval(second)(secondIndex, floatvec2)]


class GeneticAgent(LearnerBase):
    def __init__(self, index, weights):
        self.initSetup(index)
        self.weights = weights
        timestamp = '{:%m-%d_%H.%M.%S}'.format(datetime.now())
        logger = logging.getLogger("base")
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.FileHandler("logs/all_" + timestamp + ".txt"))
        self.logger = logger

    def chooseAction(self, gameState):
        self.logger.debug("going to choose action")
        # super(LearnerBase, self).chooseAction(gameState)
        LearnerBase.chooseAction(self, gameState)
        action = self.action_search(gameState)
        self.logger.debug("chose action")
        return action

    def getUtility(self, gamestate, beliefs):
        features = self.getFeatures(gamestate, beliefs, True)  # normalize to 2!
        utilVal = 0
        l_type = type([])
        for w, f in zip(self.weights, features):
            delta = 0  # overall utility change
            if type(f) == l_type:
                # have a list feature, just multiply weight by all of it

                for fl in f:
                    l_d = w * fl  # little delta, for this specific case of feature
                    delta += l_d
            else:
                delta = w * f
            utilVal += delta
        return utilVal

    def action_search(self, gamestate):
        # how much to discount future utility by, so if a state is 3 in the future, its utility is UTIL_DISCOUNT**3 * calculated_utility
        UTIL_DISCOUNT = .8

        # maximum depth of search
        MAX_SEARCH_DEPTH = 3
        # queue that holds future states to visit
        toVisit = util.Queue()
        # each item on toVisit is a tuple (starting action, gamestate, beliefs, depth, prev_action)
        # beliefs is the belief distribution of enemy positions at that point
        # prev action is the action taken to get to this state, to avoid checking the immediately previous position again
        State = namedtuple("State", ["starting_action", "gamestate", "beliefs", "depth", "prev_action"])

        # dictionary to track the utility of each state spawned off each starting action
        # action_utils[action] is a list of the utilities of all the states generated from this starting action
        action_utils = {}

        # create initial states
        legal_a = gamestate.getLegalActions(self.index)
        for action in legal_a:
            # if action == game.Directions.STOP and len(legal_a)>2:
            #     continue #only consider stop if there is only 1 alternative
            newgs = gamestate.generateSuccessor(self.index, action)
            toVisit.push(State(action, newgs, self.data.mDistribs, 0, action))
            action_utils[action] = []  # initialize action_utils for this action
        self.logger.debug("searching toVisit")
        while not toVisit.isEmpty():  # while toVisit still has stuff in it
            # new "State" tuple
            ns = toVisit.pop()
            # calculate the utility of this state and add it to action utils

            # self.logger.debug("\nconsidering position %s", self.getMyPos(ns.gamestate))

            nsu = self.getUtility(ns.gamestate, ns.beliefs)
            action_utils[ns.starting_action].append(nsu * UTIL_DISCOUNT ** ns.depth)

            # only explore further if doesn't excede max search depth
            if ns.depth < MAX_SEARCH_DEPTH:
                successor_actions = ns.gamestate.getLegalActions(self.index)
                if len(
                        successor_actions) > 1:  # if there are several subsequent actions, remove the 'double back' option
                    reverse = game.Actions.reverseDirection(ns.prev_action)
                    if reverse in successor_actions:
                        successor_actions.remove(reverse)
                    else:
                        # we've been eaten! lol
                        # print "reverse not in successor actions??", reverse, ns.prev_action, successor_actions
                        pass
                # the above code should, in the case that we went north to get here, and we can go either north or south
                # remove the option "south" from legal actions, so we do not needlessly double back
                # if however we entered a dead end, and we can thus only double back, it allows that to occur
                nsb = self.genNewBeliefs(ns.beliefs, ns.gamestate)  # generate the new beliefs for this state
                for action in successor_actions:  # add all legal successors
                    newgs = ns.gamestate.generateSuccessor(self.index, action)

                    toVisit.push(State(ns.starting_action, newgs, nsb, ns.depth + 1, action))
        self.logger.debug("done checking tovisit")
        # TODO: pick action based on highest average or highest sum?
        avg_action_util = [(u, sum(action_utils[u]) / len(action_utils[u])) for u in action_utils.keys()]
        # TODO: figure out what to do here
        # trim all lists to be the same length
        # otherwise the action with the fewest possibilities will often win, as it's highest utility course will
        # pull the average more than that of the other courses
        min_length = min(len(x) for x in action_utils.values())

        new_pairs = {a: sorted(v, reverse=True)[:min_length] for a, v in action_utils.items()}
        avg_new_pair = [(u, sum(new_pairs[u]) / len(new_pairs[u])) for u in new_pairs.keys()]
        best_action = max(new_pairs.keys(), key=lambda x: sum(new_pairs[x]) / len(new_pairs[x]))
        ##self.logger.info("Action: %s \n", best_action)
        return best_action

    def genNewBeliefs(self, oldBeliefs, gamestate):
        ### Limitations
        # Doesn't account for other players on this team moving
        # very basic move logic
        # doesn't update position in gamestate
        # TODO: Idea for updating pos in gs: have it move to a position with the assumed probability it goes there
        # TODO: (see position distribution, if goes .8 it goes to a place, it moves there w/ prob .8)
        ####
        nb = [None] * len(oldBeliefs)
        for i in self.getOpponents(gamestate):
            nb[i] = self.positionMoveInfer(i, gamestate, oldBeliefs[i])
        return nb
