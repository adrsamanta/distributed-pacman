from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from capture import GameState, SIGHT_RANGE
from collections import namedtuple
from time import time

def createTeam(firstIndex, secondIndex, isRed,
               first='TestAgent', second='TestAgent'):
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

class TestAgent(CaptureAgent):
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

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)


    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        myState = gameState.getAgentState(self.index)

        otherState=gameState.getAgentState(self.getOpponents(gameState)[0])
        pos = otherState.getPosition()
        #print('TestAgent: ',pos)

        '''
        You should change this in your own agent.
        '''

        return random.choice(actions)