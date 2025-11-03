
class Part:
    def __init__(self, name, description, buffType, stat, value, cost):
        self.name = name
        self.desc = description
        self.buffType = buffType
        self.stat = stat
        self.value = value
        self.cost = cost

    def upgrade(self, player):
        #For when parts effect two or more stats
        if isinstance(self.stat, (list, tuple)) and isinstance(self.value, (list, tuple)):
            for s, v in zip(self.stat, self.value):
                currentValue = getattr(player, s)
                if isinstance(v, bool):
                    setattr(player, s, v)
                elif self.buffType == "+":
                    setattr(player, s, currentValue + v)
                elif self.buffType == "*":
                    setattr(player, s, currentValue * v)
            return
        
        currentValue = getattr(player, self.stat)
        if isinstance(self.value, bool):
              setattr(player, self.stat, self.value)
        elif self.buffType == "+":
                setattr(player, self.stat, currentValue + self.value)
        elif self.buffType == "*":
                setattr(player, self.stat, currentValue * self.value)

commonParts = [Part("Old Booster", "It may be old, but it gets the job done. Increases movement speed.", "+", "speed", 5, 10),
               Part("Mechanical Gear", "The gears move faster. Increases fire rate.", "+", "shotDelay", -20, 15),
               Part("Cooling System", "Prevents the heating system from overheating. Increases charging speed", "+", "chargingSpeed", -50, 20),
               Part("Wrench", "Helps for repairs. Heal after every level", "+", "regain", 3, 15),
               Part("Lucky Clover", "Reminds you of home. Increases chance of luck.", "+", "luck", 10, 25),
               Part("Blocker Data Sample", "Data of Blocker's weaknesses. Increases damage against Blockers", "+", "blockerWeak", True, 15),
               Part("Targeting System", "Helps to aim better. Increases damage for bullet.", "+", "bulletDamage", 1, 25),
               Part("Impenetrable Armor", "Protects the ship from collisions. Reduces collision damage.", "+", "reduction", -1, 20)]

rareParts = [Part("Warp Drive", "We're going beyond space. Greatly increases movement speed.", "+", "speed", 8, 30),
             Part("Pre-heated Ammunition", "Pre-heat weapons to prep for battle. Increased damage of weapons.", "+", "damage", 1, 40),
             #Part("Piercing Shot", "Pierce straight through their defenses. Bullets can pierce an enemy.", "+", "pierceUpgrade", "True", 40),   #Might not implement
             Part("Insert Token", "Insert coin. Prevents death once.", "+", "extraLife", 1, 60),
             Part("Heavy Plating", "Keeps the ship safe at a cost. Decreases damage taken, but reduces movement speed.", "+", ["reduction", "speed"], [-1, -2], 50),
             Part("Lucky Dice", "Let's go gambling! Greatly increases luck.", "+", "luck", 20, 70),
             Part("Jammer", "No signal needed. Increases enemy spawn times.", "+", "jammed", 500, 50),
             Part("Combustion Data Sample", "Data of Combustion's weaknesses. Hijack Combustion bullets.", "+", "combustionWeak", True, 40),
             Part("Basic Data Sample", "Data of Basic's weaknesses. Increases worth of Basics.", "+", "basicWeak", True, 70),   #Check if works
             ] 

legendaryParts = [Part("Legendary Booster", "Holy booster. Increases movement speed.", "+", "speed", 40, 0)
#                  Part("Nano Tech"),
#                  Part("Charger Horns"),
                  ]

#bossParts = [Part("Laser Pointer"),
#             Part("Charged Battery"),]

badParts = []
#b.	Legendary Parts
#i.	Nano Tech- Heals health for successful hit on an enemy. Greatly reduces shot cooldown.
#ii.	Charger Horns- When an enemy collides with the player, the enemy gets damaged as well. Reduces collision damage.
#c.	Boss Parts
#i.	Laser Pointer- Increases damage of Laser and duration
#ii.	Charged Battery- Increases recharge speed of Laser and charged shot for bullet.