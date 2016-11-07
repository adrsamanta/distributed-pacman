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
# it does get hung sometimes (as does HLA, I believe) between actions
class HardwiredNPAgent(HardwiredAgent):
    def registerInitialState(self, gameState):
        HardwiredAgent.registerInitialState(self, gameState)
        HLA.chaseEnemy = HardwiredNPAgent.chasePacmanAction
        HLA.default = HLA.chaseEnemy


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
        epac = [e for e in self.getOpponents(gameState) if self.isPacman(gameState, e)]
        if not epac:
            # no enemy pacmen
            return self.goToBorder(gameState)
        target = min(epac, key=lambda x: self.getMyDistanceToEnemy(gameState, x))
        # dictionary where next positions are the keys, and the
        nextPosl = {game.Actions.getSuccessor(self.getMyPos(gameState), action): action for action in
                    gameState.getLegalActions(self.index)}
        bestPos = min(nextPosl.keys(), key=lambda x: self.getDistanceToEnemy(x, target))
        # TODO: Make this not stupidly run  into enemy ghosts
        return nextPosl[bestPos]  # return the action corresponding to bestpos

    def goToBorder(self, gameState):
        print "going to border"
        nextPosl = {game.Actions.getSuccessor(self.getMyPos(gameState), action): action for action in
                    gameState.getLegalActions(self.index)}
        teammatePos = self.getTeammatePositions(gameState)

        # don't stop in same position as teammate
        for pos in nextPosl.keys():
            if pos in teammatePos and nextPosl[pos] == game.Directions.STOP:
                del nextPosl[pos]

        def order(pos):
            if pos in self.data.borderDistances:
                return self.data.borderDistances[pos]

            elif pos in self.data.e_borderDistances:
                return self.data.e_borderDistances[pos] - 1
                # subtract 1, because aiming for 1 before enemy side
            else:
                # no idea where this is?
                # TODO: make sure this doesnt happen often
                return 1

        closest_pos = min(nextPosl.keys(), key=order)
        return nextPosl[closest_pos]
