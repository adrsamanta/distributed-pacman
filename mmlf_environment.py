from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.framework.spaces import ActionSpace, StateSpace

from LearnBase import LearnerBase

from game_code import capture
from game_code.game import Directions


class MMLF_Agent(LearnerBase):
    def registerInitialState(self, gameState):
        LearnerBase.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        LearnerBase.registerInitialState(self, gameState)
        ##give new features to evaluate action so it can return


DEFAULT_CONFIG_DICT = {
    "enemy_hidden": False,
    "must_return_home": False
}


class MMLF_Environment(SingleAgentEnvironment):
    def __init__(self, *args, **kwargs):
        super(SingleAgentEnvironment, self).__init__(*args, **kwargs)

        self.environmentInfo = EnvironmentInfo(environmentName="Pacman",
                                               continuousStateSpace=True,
                                               discreteActionSpace=True)
        self.actionSpace = ActionSpace()
        self.actionSpace.addDiscreteDimension("move", [Directions.EAST, Directions.NORTH,
                                                       Directions.SOUTH, Directions.WEST,
                                                       Directions.STOP])

        self.stateSpace = StateSpace()
        for dim in LearnerBase.Features._fields:
            self.stateSpace.addContinuousDimension(dim, [(-2, 2)])

    def evaluateAction(self, actionObject):
        pass
