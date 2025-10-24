
class Part:
    def __init__(self, name, description, buffType, stat, value, cost):
        self.name = name
        self.desc = description
        self.buffType = buffType
        self.stat = stat
        self.value = value
        self.cost = cost

    def upgrade(self, player):
        currentValue = getattr(player, self.stat)
        if isinstance(self.value, bool):
              setattr(player, self.stat, self.value)
        elif self.buffType == "+":
                setattr(player, self.stat, currentValue + self.value)
        elif self.buffType == "*":
                setattr(player, self.stat, currentValue * self.value)

commonParts = [Part("Old Booster", "It may be old, but it gets the job done. Increases movement speed.", "+", "speed", 5, 10),
               Part("Mechanical Gear", "The gears move faster. Increases fire rate.", "+", "shotDelay", -20, 10),
               Part("Cooling System", "Prevents the heating system from overheating. Increases charging speed", "+", "chargingSpeed", -50, 10),
               Part("Wrench", "Helps for repairs. Heal after every level", "+", "regain", 3, 10),
               Part("Lucky Clover", "Reminds you of home. Increases chance of getting rarer items.", "+", "luck", 10, 10),      #Needs to implemented
               Part("Blocker Data Sample", "Data of Blocker's weaknesses. Increases damage against Blockers", "+", "blockerWeak", True, 10),
               Part("Targeting System", "Helps to aim better. Increases damage for bullet.", "+", "damage", 1, 10),
               Part("Impenetrable Armor", "Protects the ship from collisions. Reduces collision damage.", "+", "reduction", -1, 10)]
rareParts = []
legendaryParts = []
bossParts = []
badParts = []
