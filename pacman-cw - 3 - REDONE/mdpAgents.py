# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        self.discountFactor = 0.8
    

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        # !!!! Make this NOT available
        self.state = state

        
        corners = api.corners(state)
        self.width =  corners[2][1] + 1   # Number of rows int he grid
        self.length = corners[1][0] + 1   # Number of columns in the grid
        self.walls = api.walls(state)
        
        # Create map for Pacman to store rewards
        # Finite set of states S
        self.map = [ [ 0 for i in range(self.width) ] for j in range(self.length) ]
        self.utilities = [ [ 0 for i in range(self.width) ] for j in range(self.length) ]

        
        
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        self.updateMap(state)

        pacman = api.whereAmI(state)
        colP, rowP = pacman[0], pacman[1]

        self.valueIteration(state)
        bestAction = self.chooseBestAction(legal, colP, rowP)

        print "And chooses to go:"
        print bestAction

        
        return api.makeMove(bestAction, legal)


    def chooseBestAction(self, legal, col, row):
        north = (col, row + 1)
        south = (col, row - 1)
        east = (col + 1, row)
        west = (col - 1, row)

        legalMoves = []
        if Directions.NORTH in legal:
            legalMoves.append(north)
        if Directions.SOUTH in legal:
            legalMoves.append(south)
        if Directions.EAST in legal:
            legalMoves.append(east)
        if Directions.WEST in legal:
            legalMoves.append(west)

        bestAction = legal[0]
        maxUtility = -100000000000
        for a in legal:
            expectedOutcome = 0
            for snew in legalMoves:
                expectedOutcome += self.stateTransitionFunction(snew, (col, row), a, legalMoves) * self.utilities[snew[0]][snew[1]]
            if expectedOutcome > maxUtility:
                # print expectedOutcome
                maxUtility = expectedOutcome
                bestAction = a
        
        return bestAction
        


    def valueIteration(self, state):
        for j in range(self.length):    
            for i in range(self.width):
                self.utilities[j][i] = 0
        
        foodList = api.food(state)
        # Terminal state
        if len(foodList) == 1:
            food = foodList[0]
            # self.utilities[food[0]][food[1]] += 500 TRY THIS!!!
            self.map[food[0]][food[1]] += 800

        capsules = api.capsules(state)
        pacman = api.whereAmI(state)
        closestFood = foodList[0]
        minDistance = 1000
        for food in foodList:
            distance = util.manhattanDistance(pacman, food)
            if distance < minDistance:
                minDistance = distance
                closestFood = food
        self.map[closestFood[0]][closestFood[1]] += 200

        ghosts = api.ghosts(state)
        ghostsStates = api.ghostStatesWithTimes(state)

        if self.length != 7:
            closestGhostSt = ghostsStates[0]
            ghost1 = ghostsStates[0][0]
            ghost2 = ghostsStates[1][0]
            state1 = ghostsStates[0][1]
            state2 = ghostsStates[1][1]
            dist1 = util.manhattanDistance(pacman, ghost1)
            dist2 = util.manhattanDistance(pacman, ghost2)
            # if dist1 < dist2:
            #     if state1 > 0:
            #         self.map[int(ghost1[0])][int(ghost1[1])] += 2300
            #     elif state2 > 0:
            #         self.map[int(ghost2[0])][int(ghost2[1])] += 2300
            # else:
            #     if state2 > 0:
            #         self.map[int(ghost2[0])][int(ghost2[1])] += 2300
            #     elif state1 > 0:
            #         self.map[int(ghost1[0])][int(ghost1[1])] += 2300 # goes toward the ghost wtf


        iter = 0
        utilitiesHaveChanged = True
        while iter < 100:
            iter += 1
            utilitiesHaveChanged = False
            newUtilities = [ [ 0 for i in range(self.width) ] for j in range(self.length) ]
            for j in range(self.length):    
                for i in range(self.width):
                    if self.map[j][i] != "*":
                        maxUtility = self.getMaxActionUtility(j, i)[1]
                        newUtility = self.map[j][i] + self.discountFactor * float(maxUtility)
                        #give food closer to pacman greater utility value
                        # distToClosestFood = util.manhattanDistance((j, i), closestFood)
                        # if distToClosestFood < 
                            

                        #DANGER ZONE
                        for ghost in ghosts:
                            distance = util.manhattanDistance((j, i), ghost)
                            maxDistance = 0
                            minusPoints = 0
                            if self.length == 7:
                                maxDistance = 4
                                minusPoints = 200
                            else:
                                maxDistance = 3
                                minusPoints = 2000
                                # BEST SO FAR FOR MENDIUM: 8/25
                                # maxDistance = 3
                                # minusPoints = 1500 
                            if distance < maxDistance:
                                newUtility -= minusPoints
                        
                        newUtilities[j][i] = newUtility
                        if self.utilities[j][i] != newUtility:
                            utilitiesHaveChanged = True
            self.utilities = newUtilities
        # for utility in self.utilities:
        #     print int(utility[1])
        # print iter

            
    def getMaxActionUtility(self, j, i):
        north = (j, i + 1)
        south = (j, i - 1)
        east = (j + 1, i)
        west = (j - 1, i)

        legalActions = []
        legalMoves = []

        if north not in self.walls:
            legalActions.append(Directions.NORTH)
            legalMoves.append(north)
        if south not in self.walls:
            legalActions.append(Directions.SOUTH)
            legalMoves.append(south)
        if east not in self.walls:
            legalActions.append(Directions.EAST)
            legalMoves.append(east)
        if west not in self.walls:
            legalActions.append(Directions.WEST)
            legalMoves.append(west)

        legalMoves.append((j, i))

        maximumExpectedOutcome = -10000000000000
        bestAction = legalActions[0]
        for a in legalActions:
            expectedOutcome = 0
            for snew in legalMoves:
                expectedOutcome += self.stateTransitionFunction(snew, (j, i), a, legalMoves) * self.utilities[snew[0]][snew[1]]
            if expectedOutcome > maximumExpectedOutcome:
                # print expectedOutcome
                maximumExpectedOutcome = expectedOutcome
                bestAction = a
        # if maximumExpectedOutcome < 100:
        #     print maximumExpectedOutcome
        return (bestAction, maximumExpectedOutcome)


    def stateTransitionFunction(self, snew, scur, a, legalMoves):
        north = (scur[0], scur[1] + 1)
        south = (scur[0], scur[1] - 1)
        east = (scur[0] + 1, scur[1])
        west = (scur[0] - 1, scur[1])

        probability = 0
        if a == Directions.NORTH:
            if snew == north:
                probability += 0.8
            elif snew == east:
                probability += 0.1
            elif snew == west:
                probability += 0.1
            elif snew == scur:
                if Directions.EAST not in legalMoves:
                    probability += 0.1
                if Directions.WEST not in legalMoves:
                    probability += 0.1
        elif a == Directions.SOUTH:
            if snew == south:
                probability += 0.8
            elif snew == east:
                probability += 0.1
            elif snew == west:
                probability += 0.1
            elif snew == scur:
                if Directions.EAST not in legalMoves:
                    probability += 0.1
                if Directions.WEST not in legalMoves:
                    probability += 0.1
        elif a == Directions.EAST:
            if snew == east:
                probability += 0.8
            elif snew == north:
                probability += 0.1
            elif snew == south:
                probability += 0.1
            elif snew == scur:
                if Directions.NORTH not in legalMoves:
                    probability += 0.1
                if Directions.SOUTH not in legalMoves:
                    probability += 0.1
        elif a == Directions.WEST:
            if snew == west:
                probability += 0.8
            elif snew == north:
                probability += 0.1
            elif snew == south:
                probability += 0.1
            elif snew == scur:
                if Directions.NORTH not in legalMoves:
                    probability += 0.1
                if Directions.SOUTH not in legalMoves:
                    probability += 0.1
        return probability


    # Updates map for every step Pacman makes
    def updateMap(self, state):
        self.map = [ [ 0 for i in range(self.width) ] for j in range(self.length) ]
        # Initialize map using state
        for wall in self.walls:
            self.map[wall[0]][wall[1]] = "*"
        foodList = api.food(state)
        for food in foodList:
            self.map[food[0]][food[1]] = 20
        ghostList = api.ghosts(state)
        for ghost in ghostList:
            # self.map[int(ghost[0])][int(ghost[1])] = -10000
            if self.length == 7:
                self.map[int(ghost[0])][int(ghost[1])] = -1000
            else:
                self.map[int(ghost[0])][int(ghost[1])] = -1000
        capsules = api.capsules(state)
        for capsule in capsules:
            self.map[capsule[0]][capsule[1]] = 100
        # free spaces have value of 5 
        for j in range(self.length):
            for i in range(self.width):
                if self.map[j][i] == 0:
                    self.map[j][i] = 5


    

# PROBLEMS THAT CAN MAKE PACMAN BAD
#
# 1. In small grid, for example, Pacman gets stuck when going for food and gets eaten by ghost
# because utility for that state is best
# implement DANGER ZOME
# IMPLEMENT CAPSULES
# if 3,3 not food scade reward
# SEE IF PYTHON 2.7.5 WORKS
