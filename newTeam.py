# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

#TODO LIST:
"""
-add inference to state space search
    save return val of positionMoveInfer in State, use that as distrib. Might need to change mDistribs a lot, idk
-weight going home higher if near enemy ghost
-maybe weight running from ghosts higher
-Add short circuit in state space search, where if can eat food safely, eat the food always. there's not a better move there
-prune action sequences that takes us into many repeated positions when there isnt a significant increase in utility
"""

import random

import search
import util
from AgentExternals import TeamData, PacmanPosSearch
from BaseAgent import BaseAgent
from captureAgents import CaptureAgent
from game_code import game
from game_code.capture import SIGHT_RANGE


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='HardwiredAgent', second='HardwiredAgent'):
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


##########
# Agents #
##########

# class DummyAgent(CaptureAgent):
#     """
#     A Dummy agent to serve as an example of the necessary agent structure.
#     You should look at baselineTeam.py for more details about how to
#     create an agent as this is the bare minimum.
#     """
#
#     def registerInitialState(self, gameState):
#         """
#         This method handles the initial setup of the
#         agent to populate useful fields (such as what team
#         we're on).
#
#         A distanceCalculator instance caches the maze distances
#         between each pair of positions, so your agents can use:
#         self.distancer.getDistance(p1, p2)
#
#         IMPORTANT: This method may run for at most 15 seconds.
#         """
#
#         '''
#         Make sure you do not delete the following line. If you would like to
#         use Manhattan distances instead of maze distances in order to save
#         on initialization time, please take a look at
#         CaptureAgent.registerInitialState in captureAgents.py.
#         '''
#         CaptureAgent.registerInitialState(self, gameState)
#
#         '''
#         Your initialization code goes here, if you need any.
#         '''
#
#     def chooseAction(self, gameState):
#         """
#         Picks among actions randomly.
#         """
#         actions = gameState.getLegalActions(self.index)
#
#         '''
#         You should change this in your own agent.
#         '''
#
#         return random.choice(actions)


# NOTE this team performs rather poorly if you don't have to return home

class HLA:
    #due to dependency issues, set the members of HLA inside HardwiredAgent
    goHome = None
    runAway = None
    eatFood = None
    chaseEnemy = None
    eatCapsule = None
    default = None

    pass
    # set each of the HLAs to the method in HardwiredAgent that defines the behavior in that case
    # calling each of these should just require passing in the current object as the self parameter


class HardwiredAgent(BaseAgent):

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
        #set the members of HLA to the HardwiredAgent methods
        HLA.goHome = HardwiredAgent.pathToHome
        HLA.runAway = None
        HLA.eatFood = HardwiredAgent.eatFoodAction
        HLA.chaseEnemy = HardwiredAgent.chasePacmanAction
        HLA.eatCapsule = HardwiredAgent.eatCapsuleAction
        HLA.default = HardwiredAgent.pathToHome
        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)
        #set up data repository
        if self.red:
            if not TeamData.RedData:
                TeamData.RedData=TeamData(gameState, self.getTeam(gameState), self.getOpponents(gameState), self)
            self.data=TeamData.RedData

        else:
            if not TeamData.BlueData:
                TeamData.BlueData=TeamData(gameState, self.getTeam(gameState), self.getOpponents(gameState), self)
            self.data=TeamData.BlueData

        self.legalPositions=self.data.legalPositions
        self.offensive = self.data.getOffensive()

        #set up distribution list that will hold belief distributions for agents

    def chooseAction(self, gameState):
        #print(pos)

        #get a list of actions
        #update belieft distribution about enemy positions
        #is anyone scared
        #food far away from know enemies
        #food close to enemies but near capsule
        #if theres one action:  update belief distribution and take that action
        #
        #else calculate utility function for each action
        #
        #startTime=time()
        self.knownEnemies={} #enemy position, key is enemy index
        self.data.logFood(gameState)
        self.updatePosDist(gameState)
        if self.getScaredMovesRemaining(gameState)>2:
            self.offensive=True
        elif self.getScaredMovesRemaining(gameState)==1:
            self.offensive=self.data.getOffensive()
        #print "infer time: ", time()-startTime
        self.displayDistributionsOverPositions(self.data.mDistribs)
        self.data.reset_food_target(self.index)
        bestAction = self.actionSearch(gameState)

        # bestAction, utility= self.actionSearch(self.index, gameState)
        # newPos=game.Actions.getSuccessor(self.getMyPos(gameState), bestAction)
        # currFeatures=self.getFeatures(gameState)
        # nextGameState=gameState.generateSuccessor(self.index, bestAction)
        # nextFeatures=self.getFeatures(nextGameState)
        # currWeight=self.getWeights(currFeatures, gameState)
        # nextWeight=self.getWeights(nextFeatures, nextGameState)
        #
        # print "offensive?", self.offensive
        # if not self.offensive:
        #     print "currWeights=", currWeight
        #     print "currFeatures=", currFeatures
        #     #print "nextWeights=", nextWeight
        #     print "curUtility: "
        #     currUtility=self.Utility(gameState, currFeatures, True)
        #     print "\nnextUtil"
        #     nextUtility=self.Utility(nextGameState, nextFeatures, True)
        #     print "currUtility", currUtility
        #     print "nextUtility", nextUtility
        #     enemyPac=[i for i in self.getOpponents(gameState) if gameState.getAgentState(i).isPacman]
        #     if len(enemyPac)>0:
        #         enemyPac=enemyPac[0]
        #         print "closer to enemy pacman?", self.getDistanceToEnemy(gameState, enemyPac)>self.getDistanceToEnemy(nextGameState, enemyPac)
        #     print "\n"

        # for i in self.getOpponents(gameState):
        #
        #     if i in self.knownEnemies and self.knownEnemies[i]==newPos:
        #         self._setKnownPosDist(i, gameState.getInitialAgentPosition(i))
        #     elif i in self.knownEnemies and \
        #                     self.getMazeDistance(newPos, self.knownEnemies[i])<self.getMazeDistance(self.getMyPos(gameState), self.knownEnemies[i])\
        #                     and not gameState.getAgentState(i).isPacman:
        #         print "moved toward enemy"
        #         print "newpos=", newPos
        #         print "utility=", utility
        if gameState.data.timeleft < 1000:
            # raw_input("Action="+bestAction)
            # print "\n"
            pass
        print "Action="+bestAction
        print "\n"
        return bestAction
        # return random.choice(gameState.getLegalActions(self.index))
        #return self.offensiveReflex(gameState)

    def pickHighLevelAction(self, gameState):
        features=self.getFeatures(gameState)


        if self.offensive:
            print "offensive"
            if features["foodEatenBySelf"]>4 or (features["score"]<0 and features["foodEatenBySelf"]+features["score"]>=0):
                return HLA.goHome
            elif max(features["enemyPacmanFood"])>features["score"]>0 and self.getScaredMovesRemaining(gameState)==0:
                return HLA.chaseEnemy
            elif self.getCapsules(gameState) and (features["distToNearestCapsule"]<4 or features["score"]+features["foodEatenBySelf"]<0):
                return HLA.eatCapsule
            else:
                return HLA.eatFood
        else:
            print "defensive"
            if max(features["enemyPacmanFood"])>=1 and self.getScaredMovesRemaining(gameState)==0:
                #TODO: fix scared moves remaining timer
                return HLA.chaseEnemy
            elif self.getCapsules(gameState) and (
                    features["distToNearestCapsule"] < 4 or features["score"] + features["foodEatenBySelf"] < 0):
                return HLA.eatCapsule
            elif features["foodEatenBySelf"] > 4 or (
                    features["score"] < 0 and features["foodEatenBySelf"] + features["score"] >= 0):
                return HLA.goHome
            else:
                return HLA.eatFood
            #TODO: add shadow enemy action

        # if features["distToEnemyGhost"]<3 and not gameState.getAgentState(self.index).isPacman:
        #     #need to run
        #     return

    def actionSearch(self, gameState):
        #lock in hla, then find best way to accomplish that given the positions of the enemy ghosts
        hla = self.pickHighLevelAction(gameState)

        #hla is a method in this class, call it, providing self as the implicit parameter
        return hla(self, gameState)

    #called when the agent should procede home
    def pathToHome(self, gamestate, beliefs):
        print "Going home"
        #find shortest path to home
        #generate exclusion zones around the enemies, find shortest path that doesn't go through an exclusion zone

        #options for exclusion zones:

            #if distance from pos to self>distance from pos to enemy
            #distance from pos to self==distance from pos to enemy

        ez = self.genExclusionZones(gamestate)

        goHomeProb = PacmanPosSearch(self.getMyPos(gamestate), self.data.borderPositions, gamestate, ez)


        def heuristic(state, problem):
            if state in self.data.borderDistances:
                return self.data.borderDistances[state]
            else:
                return 0


        path, _ = search.astar(goHomeProb, heuristic)
        if not path:
            #relax the exclusion zones to only be where the enemy is
            ghp2 = PacmanPosSearch(self.getMyPos(gamestate), self.data.borderPositions, gamestate, list(self.knownEnemies.values()))
            path, _ = search.astar(ghp2, heuristic)
            if not path:
                #still no path home, probably screwed, just stop and pray
                path=[game.Directions.STOP] #just wait, because can't go anywhere
            #hollup
            pass
        return path[0] #return the first action in the path



    #called when the agent should chase the enemy pacman
    #precondition: At least 1 enemy is a pacman
    def chasePacmanAction(self, gameState):
        print "Chasing pacman"
        #just make it blindly chase the enemy for now, work on more intelligent chasing later
        #
        # target = None
        # this fails if we only know the position of the enemy ghost. Easier to just chase the more full enemy pacman
        # if len(self.knownEnemies)==1:
        #     #only 1 enemy has known position, chase that one
        #     target = self.knownEnemies.keys()[0]


        # else:

        target = max(self.getOpponents(gameState), key = lambda x : self.getFoodEatenByEnemyAgent(gameState, x))
        #dictionary where next positions are the keys, and the
        nextPosl = {game.Actions.getSuccessor(self.getMyPos(gameState), action) : action for action in gameState.getLegalActions(self.index)}
        bestPos = min(nextPosl.keys(), key=lambda x: self.getDistanceToEnemy(x, target))
        #TODO: Make this not stupidly run  into enemy ghosts
        return nextPosl[bestPos] #return the action corresponding to bestpos




    #called when the agent should attempt to eat a capsule
    def eatCapsuleAction(self, gamestate):
        print "Eating capsule"
        ez = self.genExclusionZones(gamestate)
        prob = PacmanPosSearch(self.getMyPos(gamestate), self.getCapsules(gamestate), gamestate, ez)
        #TODO: add a heuristic using dist to nearest capsule
        path, _ = search.astar(prob) #use a-star, null heuristic
        if not path:
            #hollup
            HLA.default(self, gamestate)
            pass
        return path[0]
        #TODO: consider adding option to abandon this choice if it's shitty

    #called when the agent should find some food to eat and eat it
    def eatFoodAction(self, gamestate):
        print "Eating some dope ass food"
        ez = self.genExclusionZones(gamestate)
        teammate_targets=set()
        for teammate in self.getTeam(gamestate):
            if teammate!=self.index:
                teammate_targets.add(self.data.get_food_target(teammate))

        goals = [pos for pos in self.getFood(gamestate).asList() if pos not in teammate_targets]

        prob = PacmanPosSearch(self.getMyPos(gamestate), goals, gamestate, ez)

        path, target = search.astar(prob)
        self.data.set_food_target(self.index, target)
        if path == None:
            #no good food to eat, just go home
            return HLA.default(self, gamestate)
        else:
            return path[0]


    def Utility(self, gameState, features, debug=False):

        #features = self.getFeatures(gameState)
        weights = self.getWeights(features, gameState)
        if len(features)!=len(weights):
            print("AWKO TACO")
            print weights.keys()
            print("numEne")
            for key in features.keys():
                if key not in weights:
                    print key
        utility = 0
        for feature, feature_value in features.items():

            if not feature_value or not weights[feature]:
                continue
            if debug:
                print "feature=", feature, "feature value=", feature_value
                print "old utility=", utility
            if isinstance(feature_value,list):
                if feature=="distToEnemyPacman":
                    for i in range(len(feature_value)):
                        if not feature_value[i]:
                            print "featurevalue[i] was 0", feature, feature_value
                            #we ate a pacman, add utility for this
                            utility+=6*weights[feature]
                            continue
                        utility+=6./feature_value[i] * weights[feature]
                else:
                    for i in range(len(feature_value)):
                        utility += feature_value[i] * weights[feature]
            elif feature=="foodDist":
                utility+=5./feature_value*weights[feature]
            elif feature=="distToNearestCapsule":
                utility+=4./feature_value*weights[feature]
            elif feature=="distToEnemyGhost":
                utility+=6./feature_value * weights[feature]
            elif feature=="distToHome":
                utility+=4./feature_value*weights[feature]
            elif feature=="distToNearestTeammate":
                utility+=2./feature_value*weights[feature]
            else:
                if feature.lower().find("dist")!=-1:
                    print feature, "not captured for special"
                utility += feature_value * weights[feature]
            if debug:
                print "new utility=", utility
        return utility

    #weight on a -5 to 5 scale
    def getWeights(self, features, gameState):
        def getEnemyGhostDistanceDistrib(distance):

            if 0<=distance <=2:
                return -7
            elif 2<distance<=4:
                return -1
            elif 4<distance<=6:
                return -.2
            else:
                return 0

        def getDistToHomeDistrib(weights2):
            if weights2["foodEatenBySelf"]==0:
                return 0
            if features["scaredEnemyMovesRemaining"]>(features["distToHome"]+3):
                return 0
            elif self.getScore(gameState)<0:
                #we losing
                if features["foodEatenBySelf"]>2:

                    return -4
                elif features["foodEatenBySelf"]>0:
                    return -2
            elif self.getScore(gameState)>4:
                return -.75*features["foodEatenBySelf"]
            elif features["foodEatenBySelf"]>3:
                return -1.5*features["foodEatenBySelf"]
            else:
                return -1*features["foodEatenBySelf"]

        weights = util.Counter()
        weights["foodDist"] = 3 if self.offensive else 1
        weights["distToNearestCapsule"]= 1 if features["distToEnemyGhost"]>3 else 2
        weights["numEnemyPacmen"] = 0
        weights["distToEnemyPacman"] = 0 if features["numEnemyPacmen"]==0 else 2 if self.offensive else 4 if features["distToEnemyPacman"] > features["scaredMovesRemaining"] else -3
        if features["scaredMovesRemaining"] ==0 and weights["distToEnemyPacman"]>0:
            if not self.offensive:
                weights["foodDist"]=0
                weights["distToNearestCapsule"]=0
            if 5>features["enemyPacmanFood"]>=3:
                weights["distToEnemyPacman"]+=2
            elif features["distToEnemyPacman"]>=5:
                weights["distToEnemyPacman"]+=3
                weights["foodDist"]-=1
        weights["numEnemyGhost"] = 0
        weights["distToEnemyGhost"] = 0 if not gameState.getAgentState(self.index).isPacman else 1 \
                    if 0< features["scaredEnemyMovesRemaining"] <= features["distToEnemyGhost"] else getEnemyGhostDistanceDistrib(features["distToEnemyGhost"])
        weights["score"] = .5
        weights["movesRemaining"] = 0
        weights["scaredMovesRemaining"] = 0
        weights["scaredEnemyMovesRemaining"]=.5
        weights["foodEatenBySelf"] = 5 if self.offensive else 0 if weights["distToEnemyPacman"]>0 else 4
        weights["enemyPacmanFood"] = 0

        weights["distToNearestTeammate"] = -2
        #weights["distToHome"] = max(-1*features["foodEatenBySelf"], -5) if features["distToHome"] < features["movesRemaining"] else -5 #Tweak value later
        weights["distToHome"] = getDistToHomeDistrib(weights)
        if not self.offensive and features["numEnemyPacmen"]>0:
            weights["distToHome"]+=1
        if weights["distToHome"]<-3:
            weights["foodDist"]=0
            weights["foodEatenBySelf"]=0
            weights["distToNearestCapsule"]=0
        elif weights["distToHome"]<=-2:
            weights["foodDist"]-=1
            weights["foodEatenBySelf"]-=1

        return weights


    def getFeatures(self, gameState):
        features=util.Counter()
        myPos= self.getMyPos(gameState)
        enemies=[gameState.getAgentState(i) for i in self.getOpponents(gameState)]


        foodList=self.getFood(gameState).asList()

        if len(foodList):
            minDist=self.getMazeDistance(myPos, foodList[0])
            for pos in foodList:
                dist=self.getMazeDistance(myPos, pos)
                if dist<minDist:
                    minDist=dist
                    if dist==1:
                        break
            features["foodDist"]=minDist
        else:
            features["foodDist"]=0
        features["numEnemyPacmen"]=0
        features["distToEnemyPacman"]=[]
        features["numEnemyGhost"]=0
        features["distToEnemyGhost"]=50000
        for i, enemy in zip(self.getOpponents(gameState), enemies):
            if enemy.isPacman:
                features["numEnemyPacmen"]+=1
                features["distToEnemyPacman"].append(self.getMyDistanceToEnemy(gameState, i))

            else:
                features["numEnemyGhost"]+=1
                features["distToEnemyGhost"] = min(self.getMyDistanceToEnemy(gameState, i),
                                                   features["distToEnemyGhost"])

        features["score"]=self.getScore(gameState)
        features["movesRemaining"]=gameState.data.timeleft

        features["distToNearestCapsule"]=self.getDistToNearestCapsule(gameState)
        features["scaredMovesRemaining"]=self.getScaredMovesRemaining(gameState)
        features["scaredEnemyMovesRemaining"] = self.getEnemyAgentScaredMovesRemaining(gameState)
        features["foodEatenBySelf"]=self.getFoodEatenBySelf(gameState)
        features["enemyPacmanFood"]=[]
        for i in self.getOpponents(gameState):
            features["enemyPacmanFood"].append(self.getFoodEatenByEnemyAgent(gameState, i))
        features["distToHome"]=self.getDistanceToHomeSide(gameState)
        features["distToNearestTeammate"] = self.getDistToNearestTeammate(gameState)

        return features






    ###### BEGIN OFFENSIVE CODE ##########
    # def offensiveReflex(self, gameState):
    #     actions = gameState.getLegalActions(self.index)
    #     values = [self.evaluate(gameState, a) for a in actions]
    #     # print 'eval time for agent %d: %.4f' % (self.index, time() - start)
    #
    #     maxValue = max(values)
    #     bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    #
    #     foodLeft = len(self.getFood(gameState).asList())
    #
    #     if foodLeft <= 2:
    #       bestDist = 9999
    #       for action in actions:
    #         successor = self.getSuccessor(gameState, action)
    #         pos2 = successor.getAgentPosition(self.index)
    #         dist = self.getMazeDistance(self.start,pos2)
    #         if dist < bestDist:
    #           bestAction = action
    #           bestDist = dist
    #       return bestAction
    #
    #     return random.choice(bestActions)
    #
    # def getSuccessor(self, gameState, action):
    #     """
    #     Finds the next successor which is a grid position (location tuple).
    #     """
    #     successor = gameState.generateSuccessor(self.index, action)
    #     pos = successor.getAgentState(self.index).getPosition()
    #     if pos != util.nearestPoint(pos):
    #       # Only half a grid position was covered
    #       return successor.generateSuccessor(self.index, action)
    #     else:
    #       return successor
    #
    # def evaluate(self, gameState, action):
    #     """
    #     Computes a linear combination of features and feature weights
    #     """
    #     features = self.getFeatures(gameState, action)
    #     weights = self.getWeights(gameState, action)
    #     return features * weights
    #
    # def getFeatures(self, gameState, action):
    #     features = util.Counter()
    #     successor = self.getSuccessor(gameState, action)
    #     foodList = self.getFood(successor).asList()
    #     features['successorScore'] = -len(foodList)#self.getScore(successor)
    #
    #     # Compute distance to the nearest food
    #
    #     if len(foodList) > 0: # This should always be True,  but better safe than sorry
    #       myPos = successor.getAgentState(self.index).getPosition()
    #       minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    #       features['distanceToFood'] = minDistance
    #     return features
    #
    # def getWeights(self, gameState, action):
    #     return {'successorScore': 100, 'distanceToFood': -1}
    #
    # ############END OFFENSIVE REFLEX CODE#################





    ############END OFFENSIVE REFLEX CODE#################


    #turns a list of actions originating at the current position into a list of positions
    def actionsToPos(self, actions, gamestate):
        positions = [self.getMyPos(gamestate)]
        for action in actions:
            positions.append(game.Actions.getSuccessor(positions[-1], action))

        return positions