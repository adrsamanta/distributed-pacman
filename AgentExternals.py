import game
import search
import util

class TeamData:
    RedData=None
    BlueData=None
    def __init__(self, gameState, team, opps, agent):
        self.team=team
        self.mAgent=agent
        self.offensive = True
        self.mDistribs=[None]*gameState.getNumAgents()
        #opps=self.team[0].getOpponents(gameState)
        for i in range(gameState.getNumAgents()):
            if i in opps:
                dist=util.Counter()
                oppPos=gameState.getInitialAgentPosition(i)
                dist[oppPos]=1.0
                self.mDistribs[i]=dist
            else:
                self.mDistribs[i]=None
        #should be all legal positions
        self.legalPositions = gameState.data.layout.walls.asList(key = False)
        self.defendFoodGrid=[]



        self.borderDistances={}
        grid = gameState.getWalls()
        # since board size is even, but 0 indexed, width/2 is the boarder column on blue, so update halfway to match
        if not self.mAgent.red:
            halfway = (agent.getFood(gameState).width / 2)
            range_x = range(halfway)
        else:
            halfway = (agent.getFood(gameState).width / 2) -1
            range_x = range(halfway, grid.width)
        self.borderPositions = [(halfway, y) for y in range(agent.getFood(gameState).height) if
                                not gameState.hasWall(halfway, y)]
        for x in range_x:
            for y in range(grid.height):
                if not grid[x][y]:
                    self.borderDistances[(x, y)] = min(
                        self.mAgent.getMazeDistance((x, y), borderPos) for borderPos in self.borderPositions)

                    #self.consideredStates = {}
        #track what food each agent is
        self.food_targets={}

    #set my current food target as this food
    def set_food_target(self, agent, target):
        self.food_targets[agent]=target

    #get the food target of the given teammate
    def get_food_target(self, agent):
        if agent in self.food_targets:
            return self.food_targets[agent]
        else:
            return None

    #remove the food target of the given agent
    def reset_food_target(self, agent):
        if agent in self.food_targets:
            self.food_targets.pop(agent)

    def logFood(self, gameState):
        self.defendFoodGrid.append(self.mAgent.getFoodYouAreDefending(gameState))

    def getOffensive(self):
        self.offensive = not self.offensive
        return self.offensive

#class that implements SearchProblem from search.py
#getCostOfActions method not implemented because it doesn't make sense for this class as most actions don't have cost
class PacmanPosSearch(search.SearchProblem):
    def __init__(self, start_state, goal_states, gamestate, exclusion_zones):
        self.start = start_state
        self.goals = goal_states
        self.walls = gamestate.getWalls()
        self.ez = exclusion_zones


    def isGoalState(self, state):
        return state in self.goals

    def getSuccessors(self, state):
        #create a config representing current game state
        curr = game.Configuration(state, game.Directions.STOP) #set curr direction to stop, shouldn't be needed
        successors = []
        legal_actions = game.Actions.getPossibleActions(curr, self.walls)
        #for each legal action, create a state rep of it and add it to successors
        for action in legal_actions:
            next_state = game.Actions.getSuccessor(state, action)
            if next_state not in self.ez:
                #see documentation on getSuccessors for details
                successors.append((next_state, action, 1))

        return successors

    def getStartState(self):
        return self.start
