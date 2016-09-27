from recordclass import recordclass

from AgentExternals import *
from BaseAgent import BaseAgent
from captureAgents import CaptureAgent


class LearnerBase(BaseAgent):
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

    def chooseAction(self, gameState):
        self.knownEnemies = {}  # enemy position, key is enemy index
        self.data.logFood(gameState)
        self.updatePosDist(gameState)

    # NOTE: POPULATION INITIATION DEPENDS ON THESE NOT MOVING AROUND
    Features = recordclass("Features", ["e_ghost_dist", "e_pac_dist", "food_dist", "capsule_dist", "score",
                                        "my_scared_moves", "enemy_scared_moves", "my_food", "home_dist", "enemy_food",
                                        "safe_path_to_home", "e_dist_to_food", "e_dist_to_capsule", "e_dist_to_home"])




    # features of the current position
    def getFeatures(self, gamestate, belief_distrib, normalize=False):
        # flesh with dummy values
        feat = LearnerBase.Features(*range(len(LearnerBase.Features._fields)))

        e_ghost_dists = []
        e_pac_dists = []
        e_food = []
        e_food_dist = []
        e_capsule_dist = []
        e_home_dist = []
        # do calculations that occur for each enemy
        for enemy in self.getOpponents(gamestate):
            # for each enemy, calculate the distance to them, then add that distance to the list corresponding to their mode
            dist = self.getMyDistanceToEnemy(gamestate, enemy, belief_distrib)
            if gamestate.getAgentState(enemy).isPacman:
                e_pac_dists.append(dist)
            else:
                e_ghost_dists.append(dist)
            e_food_dist.append(self.calcEnemyFoodDist(gamestate, enemy))
            e_capsule_dist.append(self.calcEnemyCapsuleDist(gamestate, enemy))

            e_home_dist.append(self.getEnemyDistToHome(gamestate, enemy))

            e_food.append(gamestate.getAgentState(enemy).numCarrying)

        feat.e_ghost_dist = e_ghost_dists
        feat.e_pac_dist = e_pac_dists
        feat.e_dist_to_food = e_food_dist
        feat.e_dist_to_capsule = e_capsule_dist
        feat.food_dist = self.calcFoodDist(gamestate)

        feat.capsule_dist = self.getDistToNearestCapsule(gamestate)
        feat.score = self.getScore(gamestate)
        feat.my_scared_moves = self.getScaredMovesRemaining(gamestate)
        feat.enemy_scared_moves = self.getScaredMovesRemaining(gamestate)  # TODO: factor this out into above loop?
        feat.my_food = self.getFoodEatenBySelf(gamestate)
        feat.enemy_food = e_food

        if self.onMySide(self.getMyPos(gamestate)):
            feat.safe_path_to_home = 1
            feat.home_dist = 0
        else:
            path_home = self.pathToHome(gamestate, belief_distrib)
            if path_home:
                feat.safe_path_to_home = 1
                feat.home_dist = len(path_home)
            else:
                # no safe path home
                feat.safe_path_to_home = 0
                feat.home_dist = -1  # set to -1 to indicate bad value

        if normalize:
            max_f = 0
            l_type = type([])
            for f in feat:
                if type(f) == l_type:
                    tmp_max = max(f)
                    if tmp_max > max_f:
                        max_f = tmp_max

                else:
                    if f > max_f:
                        max_f = f

            # normalize to 2 for now

            norm_const = max_f / 2.
            for i, f in enumerate(feat):
                if type(f) == l_type:
                    feat[i] = [n / norm_const for n in f]
                else:
                    feat[i] = f / norm_const
        return feat
