from constraint import *
import random
import numpy as np
import matplotlib.pyplot as plt


# Corpus setup
with open("corpus.txt") as file:
    corpus = [line.rstrip() for line in file]

frequencies = {}

# Word frequencies
def createDictionary():
    with open("WordScores.txt", 'r') as file:
        lines = file.readlines()
    for line in lines:
        key, value = line.strip().split(':')
        frequencies[key.strip()] = value.strip() 

# Create the Dictionary of all words with their frequencies
createDictionary()

# Heurisitc Based on Word and Letter Frequency to calculate total word utility
def wordSorter(word):
    utility = 0
    try:
        utility = frequencies[word]
    except:
        utility = 0
    return utility

# a class representing a single letter in wordle which has a letter, a position, and a color
class WordleLetter:
    # constructor
    def __init__(self, letter, position, color) :
        self.letter = letter
        if position > 5 or position < 1:
            raise TypeError("postion must be an integer between 1 and 5, inclusive")
        else: 
            self.position = position
        if not (color == "GREEN" or color == "YELLOW" or color == "GRAY" or color == "GREY"):
            raise TypeError("color must be a string of 'GREEN', 'YELLOW' or 'GREY'")
        else:
            self.color = color

    # convert a given tuple to a WordleLetter
    @staticmethod
    def toWordleLetter(letter, position, color):
        return WordleLetter(letter, position, color)
    
    # adds a Green Constraint to a given CSP, a green contrains a variable to one letter in one location
    def addGreenConstraint(self, problem):
        problem.addConstraint(lambda x: x == self.letter, [self.position])
    
    # adds a Green Constraint to a given CSP, a grey contrains eliminates a value from the solution space
    def addGreyConstraint(self, problem):
        problem.addConstraint(NotInSetConstraint([self.letter]))

    # adds a Yellow Constraint to a given CSP, a yellow contrains requires a value to be in the solution space but not at the location it is currently at
    def addYellowConstraint(self, problem):
        problem.addConstraint(SomeInSetConstraint([self.letter]))
        problem.addConstraint(lambda x: x != self.letter, [self.position])

# a class representing a wordle problem which contains a list of WordleLetters
class WordleProblem:
    # constructor
    def __init__(self, letters=None):
        self.letters = letters
        
    def toWordleProblem(string) :
        substrings = []
        counting = False
        current_substring = ""
        wordleLetters = []
            
        for c in string:
            if c == "(":
                counting = True
            elif c == ")" and counting:
                substrings.append(current_substring)
                current_substring = ""
                counting = False
            elif counting:
                current_substring += c
        
        for i in range(len(substrings)):
            sammpletuple = tuple(map(str, substrings[i].split(', ')))
            letter = sammpletuple[0]
            position = int(sammpletuple[1])
            color = sammpletuple[2]
            wl = WordleLetter.toWordleLetter(letter, position, color)
            wordleLetters.append(wl)
        return WordleProblem(wordleLetters)
    
    def isSolved(self):
        solved = True
        for wl in self.letters:
            if wl.color != "GREEN":
                solved = False
                break
        return solved
    

    def concatenate(self):
        word = ""
        for wl in self.letters:
            word += wl.letter
        return word

    # Does a given WordleLetter repeat in this Wordle 
    def doubleLetter(self, letter):
        for wl in self.letters:
            if wl.letter == letter.letter and (wl.color == "YELLOW" or wl.color == "GREEN"):
                return True

# a class for solving a WordleProblems as Constraint Satisfaction Problems
class Solver:

    #Constructor, values are initated to defaults
    # 5 variables representing each of the 5 spaces initialized to a domain of the alphabet
    def __init__(self):
        self.problem = Problem(BacktrackingSolver())
        domain = list("abcdefghijklmnopqrstuvwxyz")
        self.problem.addVariable(1, domain)
        self.problem.addVariable(2, domain)
        self.problem.addVariable(3, domain)
        self.problem.addVariable(4, domain)
        self.problem.addVariable(5, domain)
        self.wordleProblem = WordleProblem()

    # Allows a human user to input guesses and solve a Wordle puzzle
    def solveWordle(self):
        solved = False
        print("Make your first guess for the Wordle. If you're stuck on what to guess, 'adieu' contains 4/5 vowels. \nNext report back the result of your guess as a WordleProblem")
        print("A WordleProblem is a list of 5 tuples in the format (Letter, Position, Color) \nfor example, a green letter 's' in the first position would look like (s, 1, GREEN). \nEnter all 5 letters of the current state of your wordle. The Letter should be in lowercase, the color should be in uppercase")

        while not solved:
            print("Report back guess result")
            guess = input()
            self.wordleProblem = WordleProblem.toWordleProblem(guess)
            wordleLetters = self.wordleProblem.letters
            for wl in wordleLetters:
                if wl.color == "GREEN":
                    wl.addGreenConstraint(self.problem)
                if wl.color == "GREY" and not self.wordleProblem.doubleLetter(wl):
                    wl.addGreyConstraint(self.problem)
                if wl.color == "YELLOW":
                    wl.addYellowConstraint(self.problem)
                    
            dict = self.problem.getSolutions()
            
            allSolutions = []
            
            validSolutions = []
            
            for d in dict:
                word = ""
                # ensure order
                word += d[1]
                word += d[2]
                word += d[3]
                word += d[4]
                word += d[5]
                allSolutions.append(word)
                
            # return only valid solutions, ordered by frequency
            for word in allSolutions:
                if (word in corpus):
                    validSolutions.append(word)
            
            # order the valid solutions by utility
            validSolutions.sort(reverse=True, key=wordSorter)

            # display the valid solutions
            print("Valid Solutions")
            for word in validSolutions:
                print(word)

            # terminate if no valid solutions are possible
            if len(validSolutions) == 0:
                print("No valid words found!")
                break

            # terminate if the wordle is solved
            solved = self.wordleProblem.isSolved()

        if solved:
            print("Solution Found!: " + self.wordleProblem.concatenate())

# A class for testing a Solver
class testSolver:

    # Constructor, specify number of games to test
    def __init__(self, numGames):
        self.solver = Solver()
        self.numGames = numGames
        self.testData = random.sample(corpus, numGames) 

    # Given a guess and the correct string, responds with a list of WordleLetters represented as a String
    def response(self, correct, guess):
        response = ""
        for i in range(5):
            current = "("
            previousLetters = guess[0:i+1]
            c = correct[i]
            g = guess[i]
            if c == g:
                current += g
                current += ", "
                current += str(i + 1)
                current += ", "
                current += "GREEN"
                current += "), "
            # compare instances in your guess to instances in correct
            #elif g not in correct or (g in previousLetters):
            elif g not in correct or (previousLetters.count(g) > correct.count(g)):
                current += g
                current += ", "
                current += str(i + 1)
                current += ", "
                current += "GREY"
                current += "), "
            elif g in correct and c != g:
                current += g
                current += ", "
                current += str(i + 1)
                current += ", "
                current += "YELLOW"
                current += "), "
            response += current
        return response
    
    # Uses CSP to solve a singular Wordle puzzle given the correct word
    def solveWorldle(self, correct):
        solved = False
        previousValidSolutions = []
        attempts = 0
        while not solved:
                attempts += 1
                # Pick our guess based on what was learned last round 
                # (top of the list ordered by heuristic)

                try:
                    guess = self.response(correct, previousValidSolutions[0])
                except:
                    guess = self.response(correct, "adieu")

                print("Guess results: " + guess)

                # convert string to wordle problem
                self.solver.wordleProblem = WordleProblem.toWordleProblem(guess)
                wordleLetters = self.solver.wordleProblem.letters

                # update problem contraints
                for wl in wordleLetters:
                    if wl.color == "GREEN":
                        wl.addGreenConstraint(self.solver.problem)
                    if wl.color == "GREY" and not self.solver.wordleProblem.doubleLetter(wl):
                        wl.addGreyConstraint(self.solver.problem)
                    if wl.color == "YELLOW":
                        wl.addYellowConstraint(self.solver.problem)

                # organizing solutions into one list
                dict = self.solver.problem.getSolutions()
                
                allSolutions = []

                validSolutions = []
                
                for d in dict:
                    word = ""
                    # ensure order
                    word += d[1]
                    word += d[2]
                    word += d[3]
                    word += d[4]
                    word += d[5]
                    allSolutions.append(word)

                # consider only valid solutions    
                for word in allSolutions:
                    if (word in corpus):
                        validSolutions.append(word)
                        
                # order the valid solutions by utility
                validSolutions.sort(reverse=True, key=wordSorter)
                
                # display the valid solutions
                print("Valid Solutions")
                for word in validSolutions:
                    print(word)
                
                # terminate if the wordle is solved 
                solved = self.solver.wordleProblem.isSolved()
                if solved:
                    break

                # terminate if no valid solutions are possible or max attempts have been exceeded
                if len(validSolutions) == 0 or attempts > 6:
                    attempts = -1
                    print("Failed. Answer was: " + correct)
                    break 

                # order valid solutions according to heuristic and set to the possible gusses for the next round
                previousValidSolutions = validSolutions

        if solved:
            print("Solution: " + self.solver.wordleProblem.concatenate() + " found in: " + str(attempts) + " attempt(s)")
        return attempts


    # runs a specified number of games and returns a dictionary of occurences for how many attempts the solver took
    def AISolver(self):
        occurences = {-1: 0,
                      1 : 0, 
                      2 : 0, 
                      3 : 0, 
                      4 : 0, 
                      5 : 0, 
                      6 : 0}
        for i in range(len(self.testData)):
            print("Attempting to Solve Game " + str(i + 1))
            self.solver = Solver()
            correct = self.testData[i]
            round = self.solveWorldle(correct)
            occurences[round] = occurences[round] + 1
        return occurences

# Run the Solver (Human input)
WordleSolver = Solver()
# uncomment to run human solver
#WordleSolver.solveWordle()

# Run the Tester (Automatic AI solver) change parameter to alter number of test puzzles
tester = testSolver(20)
occurences = tester.AISolver()
plt.bar(*zip(*occurences.items()))
plt.xlabel("Number of Guesses")
plt.ylabel("Number of Occurences")
plt.show()