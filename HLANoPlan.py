from newTeam import HLA, HardwiredAgent
from game_code import game


def createTeam(firstIndex, secondIndex, isRed,
               first='HardwiredNPAgent', second='HardwiredNPAgent'):
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


# this agent is identical to the hardwired agent, except it doesn't expect to need
# to go home to gain points
class HardwiredNPAgent(HardwiredAgent):
    def registerInitialState(self, gameState):
        HardwiredAgent.registerInitialState(self, gameState)
        HLA.default = HLA.chaseEnemy
        HLA.chaseEnemy = self.chasePacmanAction

    def pickHighLevelAction(self, gameState):
        features = self.getFeatures(gameState)
        if self.offensive:
            print "offensive"
            if features['score'] >= 4 and self.getScaredMovesRemaining(gameState) == 0:
                return HLA.chaseEnemy
            elif self.getCapsules(gameState) and (features["distToNearestCapsule"] < 4 or features["score"] < 0):
                return HLA.eatCapsule
            else:
                return HLA.eatFood
        else:
            print "defensive"
            if self.getScaredMovesRemaining(gameState) == 0 and features["numEnemyPacmen"] > 0:
                return HLA.chaseEnemy
            elif self.getCapsules(gameState) and (features["distToNearestCapsule"] < 4 or features["score"] < 0):
                return HLA.eatCapsule
            else:
                return HLA.eatFood

    def isPacman(self, gameState, i):
        return gameState.getAgentState(i).isPacman

    def chasePacmanAction(self, gameState):
        print "Chasing pacman"
        epac = (e for e in self.getOpponents(gameState) if self.isPacman(gameState, e))
        target = min(epac, key=lambda x: self.getMyDistanceToEnemy(gameState, x))
        # dictionary where next positions are the keys, and the
        nextPosl = {game.Actions.getSuccessor(self.getMyPos(gameState), action): action for action in
                    gameState.getLegalActions(self.index)}
        bestPos = min(nextPosl.keys(), key=lambda x: self.getDistanceToEnemy(x, target))
        # TODO: Make this not stupidly run  into enemy ghosts
        return nextPosl[bestPos]  # return the action corresponding to bestpos
