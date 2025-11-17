import random

class EventManager:
    def __init__(self):
        self.currentEvent = None

    def triggerRandomEvent(self):
        possibleEvents = ["freeCommonPart",             #Gives a random common part
                          "unknownEnemies",             #Hides the enemies in a level
                          "extraEnemies",               #Increases enemies in level
                          "asteroidsFalling",           #Asteroids fall during the level
                          "unknownRewards"]             #Hides the level rewards
        self.currentEvent = random.choice(possibleEvents)

