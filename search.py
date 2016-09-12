# search.py
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    actions = []
    visited = set()
    if problem.isGoalState(problem.getStartState()):
        return []
    visited.add(problem.getStartState())
    for sucessor in problem.getSuccessors(problem.getStartState()):
        if sucessor not in visited:
            visited.add(sucessor[0])
            result = _recursiveDFS(problem, actions, visited, sucessor)
            if result:
                return result
    return []


def _recursiveDFS(problem, actions, visited, sucessor):
    cur_state, action, _ = sucessor
    actions.append(action)
    if problem.isGoalState(cur_state):
        return actions
    for child in problem.getSuccessors(cur_state):
        if child[0] not in visited:
            visited.add(child[0])
            result = _recursiveDFS(problem, actions, visited, child)
            if result:
                return result
    actions.pop()
    return []


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    #failed autograder when checked if state was goal state when generated, as opposed to expanded
    #despite the book saying that is the correct process
 
    #check if start at goal state
    if problem.isGoalState(problem.getStartState()):
        return []
    #set of visited states
    visited=set()
    #add the start state
    visited.add(problem.getStartState())
    toVisit=util.Queue()
    #push a dummy successor object, which represents the starting state
    toVisit.push([problem.getStartState(), [], 0])
    

    while not toVisit.isEmpty():
        #unpack the list
        cur_state, actions, cumCost= toVisit.pop()
        
        if problem.isGoalState(cur_state):
            #if actions == None:
            #    print("actions none")
            return actions
        
        for child in problem.getSuccessors(cur_state):
            #unpack the child tuple
            nextState, nextAction, cost = child
            if nextState in visited:
                continue
            else:
                visited.add(nextState)
                #make a list to represent the child, so the middle element can be changed
                #modify the elements as needed
                newActions=list(actions)
                newActions.append(nextAction)
                cumCost+=cost
                newChild=[nextState, newActions, cumCost]
#                if problem.isGoalState(nextState):
#                    return newActions
#                else:
                toVisit.push(newChild)
    return []



def uniformCostSearch(problem):
    """Search the node of least total cost first."""
   
    visited=set()
    #create priority q that gets priority from 3rd element in the item
    toVisit=util.PriorityQueueWithFunction(lambda i: i[2])

    toVisit.push([problem.getStartState(), [], 0])
    while not toVisit.isEmpty():
        #unpack the list
        curState, actions, cumCost= toVisit.pop()
        #if this state has already been visited (a path with lower cost was found) continue
        if curState in visited:
            continue
        elif problem.isGoalState(curState): #found the cheapest goal
            return actions
        else: #this is the lowest cost path to curState, so add it to visited
            visited.add(curState)

        for child in problem.getSuccessors(curState):
            #unpack the child tuple
            nextState, nextAction, cost = child
            if nextState in visited: 
                continue
            else:
                #make a list to represent the child, so the middle element can be changed
                #modify the elements as needed
                newActions=list(actions)
                newActions.append(nextAction)
                newChild=[nextState, newActions, cumCost+cost]
                toVisit.push(newChild)



def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    visited = set()
    #create priority q that gets priority from 4th element in the item
    toVisit = util.PriorityQueueWithFunction(lambda i: i[3])
    #store the total path cost to reach a node as the third element and the total path cost plus the heuristic cost in the 4th element
    toVisit.push([problem.getStartState(), [], 0, 0])
    while not toVisit.isEmpty():
        #unpack the list, can ignore the 4th element because it is only used to determine priority
        cur_state, actions, pathCost, _ = toVisit.pop()

        if cur_state not in visited:
            #check goal state when node is visited
            if problem.isGoalState(cur_state):
                return actions, cur_state #return the found goal as well
            else:
                visited.add(cur_state)
            
            for child in problem.getSuccessors(cur_state):
                nextState, nextAction, cost = child
                #check if child has been visited to avoid loops
                if nextState not in visited:
                    newActions = list(actions)
                    newActions.append(nextAction)
                    newChild = [nextState, newActions, pathCost + cost, pathCost + cost + heuristic(nextState, problem)]
                    toVisit.push(newChild)
    #failed to find path
    return None, None

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
