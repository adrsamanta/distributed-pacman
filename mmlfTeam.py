from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.framework.spaces import ActionSpace, StateSpace
import mmlf.framework.filesystem as mmlfs
from mmlf.agents.dyna_td_agent import DynaTDAgent as  dta

from LearnBase import LearnerBase

from game_code import capture
from game_code.game import Directions

mmlf_path = "C:\\Users\\alan.Blackbird\\Desktop\\Documents\\CS 6366\\distributed-pacman\\mmlf"


def createTeam(firstIndex, secondIndex, isRed, first="MMLFAgent", second='MMLFAgent'):
    a1 = MMLFAgent(firstIndex)
    a2 = MMLFAgent(secondIndex)
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


class MMLFAgent(LearnerBase):
    def registerInitialState(self, gameState):
        LearnerBase.registerInitialState(self, gameState)
        self.mmlfSetup()

    def mmlfSetup(self):
        bud = mmlfs.BaseUserDirectory(mmlf_path)
        config = {}
        config["configDict"] = dta.DEFAULT_CONFIG_DICT
        self.agent = dta(config=config, baseUserDir=bud)
        self.actionSpace = ActionSpace()
        self.actionSpace.addDiscreteDimension("move", [Directions.EAST, Directions.NORTH,
                                                       Directions.SOUTH, Directions.WEST,
                                                       Directions.STOP])
        stateSpace = StateSpace()
        for dim in self.Features._fields:
            stateSpace.addContinuousDimension(dim, [(-2, 2)])
        self.agent.setStateSpace(stateSpace)
        self.agent.setActionSpace(self.actionSpace)

    def chooseAction(self, gameState):
        LearnerBase.chooseAction(self, gameState)
        feat = self.getFeatures(gameState, self.data.mDistribs)
        self.agent.setState(feat)
        action = self.agent.getAction()["action"]  # yolo?
        if action not in gameState.getLegalActions(self.index):
            print "WHOOOOOPPPSSSS illegal action??"
            # what do?
        return action


DEFAULT_CONFIG_DICT = {
    "enemy_hidden": False,
    "must_return_home": False
}


# class MMLF_Environment(SingleAgentEnvironment):
#     def __init__(self, *args, **kwargs):
#         super(SingleAgentEnvironment, self).__init__(*args, **kwargs)
#
#         self.environmentInfo = EnvironmentInfo(environmentName="Pacman",
#                                                continuousStateSpace=True,
#                                                discreteActionSpace=True)
#         self.actionSpace = ActionSpace()
#         self.actionSpace.addDiscreteDimension("move", [Directions.EAST, Directions.NORTH,
#                                                        Directions.SOUTH, Directions.WEST,
#                                                        Directions.STOP])
#
#         self.stateSpace = StateSpace()
#         for dim in LearnerBase.Features._fields:
#             self.stateSpace.addContinuousDimension(dim, [(-2, 2)])
#
#     def evaluateAction(self, actionObject):
#         pass
