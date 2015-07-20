#bunch of random games in python
import random

def GuessTheNumber():
    guessesTaken = 0
    print "Pick the base for the range"
    base = int(raw_input())
    print "Pick the highest number for the range"
    ceiling = int(raw_input())

    numToGuess = random.randint(base, ceiling)
    print "I am thinking of a number between " + str(base) + " and " + str(ceiling)
    while True:    
        print "What's your guess?"
        guess = int(raw_input())
        guessesTaken = guessesTaken + 1
        if guess < numToGuess:
            print "Your guess is too low"
        elif guess > numToGuess:
            print "Your guess is too high"
        else:
            print "You're correct! You got it in " + str(guessesTaken) + " guesses!"
            return
    return

def GameToPlay():
    print "Let's play a game, which game would you like to play:"
    print "Guess the Number"
    gameSelected = raw_input()
    if gameSelected.lower() == "Guess the Number".lower():
        GuessTheNumber()
    else:
        print "The game you have selected is not valid"
    return

print "Hello World! What is your name?"
userName = raw_input()
print "Welcome to Python " + userName
while True:
    GameToPlay()
    print "Want to play another game? Y/N"
    answer = raw_input()
    if answer.lower() == "n":
        break
print "Goodbye " + userName



    

