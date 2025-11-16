
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
                print(f" -> {self.stat}: {currentValue} -> {currentValue + self.value}")
        elif self.buffType == "*":
                setattr(player, self.stat, currentValue * self.value)
                print(f" -> {self.stat}: {currentValue} -> {currentValue * self.value}")

commonParts = [Part("Old Booster", "It may be old, but it gets the job done. Increases movement speed.", "+", "speed", 5, 5),
               Part("Mechanical Gear", "The gears move faster. Increases fire rate.", "+", "shotDelay", -20, 15),
               Part("Cooling System", "Prevents the heating system from overheating. Increases charging speed", "+", "chargingSpeed", -50, 15),
               Part("Wrench", "Helps for repairs. Heal after every level", "+", "regain", 3, 10),
               Part("Lucky Clover", "Reminds you of home. Increases chance of luck.", "+", "luck", 10, 25),
               Part("Blocker Data Sample", "Data of Blocker's weaknesses. Increases damage against Blockers", "+", "blockerWeak", True, 10),
               Part("Targeting System", "Helps to aim better. Increases damage for bullet.", "+", "bulletDamage", 1, 25),
               Part("Impenetrable Armor", "Protects the ship from collisions. Reduces collision damage.", "+", "reduction", -1, 20),
               Part("Trackers", "Allows for long range tracking. Increases movement speed of missiles.", "+", "missileSpeed", 3, 15),       #works
               Part("Lead Missiles", "Lead tipped missiles. Increases damage of missiles.", "+", "missileDamage", 1, 25),                   #Works
               Part("Shooter Data Sample", "Data of Shooter's weaknesses. Shooter has a chance to not shoot.", "+", "shooterWeak", True, 15),       #Works
               ]

rareParts = [Part("Warp Drive", "We're going beyond space. Greatly increases movement speed.", "+", "speed", 8, 15),
             Part("Pre-heated Ammunition", "Pre-heat weapons to prep for battle. Increased damage of weapons.", "+", "damage", 1, 40),
             #Part("Piercing Shot", "Pierce straight through their defenses. Bullets can pierce an enemy.", "+", "pierceUpgrade", "True", 40),   #Might not implement
             Part("Insert Token", "Insert coin. Prevents death once.", "+", "extraLife", 1, 50),
             Part("Heavy Plating", "Keeps the ship safe at a cost. Decreases damage taken, but reduces movement speed.", "+", ["reduction", "speed"], [-1, -2], 30),
             Part("Lucky Dice", "Let's go gambling! Greatly increases luck.", "+", "luck", 20, 60),
             Part("Jammer", "No signal needed. Increases enemy spawn times.", "+", "jammed", 500, 50),
             Part("Combustion Data Sample", "Data of Combustion's weaknesses. Hijack Combustion bullets.", "+", "combustionWeak", True, 40),
             Part("Basic Data Sample", "Data of Basic's weaknesses. Increases worth of Basics.", "+", "basicWeak", True, 60),
             Part("Atomic Destabilizer", "Your very being feels unstable. Increases immunity frames.", "+", "immuneFrames", 300, 50),           #works
             Part("Charger Data Sample", "Data of Charger's weaknesses. Decreases Charger's movement speed.", "+", "chargerWeak", True, 40),            #Works
             Part("Quad Launcher", "Double the power. Adds another set of missiles per shot.", "+", ["dualLauncher", "missileDamage"], [True, -1], 35),      #Works
             Part("Extra 3D Printer", "Now you can print all sorts of things. Decreases missile cooldown.", "+", "missileCooldown", -300, 60),      #Works
             ] 

legendaryParts = [Part("Warp Speed Booster", "We're going into overdrive with this one. Increases movement speed.", "+", "speed", 20, 50),
                  Part("Nano Tech", "Advanced machinery that uses scrap to repair the ship. Gain health when killing enemies.", "+", ["lifesteal", "regain"], [True, 1], 100),      #Works
                  Part("Charger Horns", "Stolen horns of a Charger. When enemies collide with you, they take damage as well. Reduces collision damage.", "+", ["thorns", "thornsDamage", "reduction"], [True, 3, -3], 80),
                  Part("Secret Intel", "TOP SECRET INFO. Has information on every enemy, including their boss.", "+", "damage", 3, 150),
                  ]

bossParts = [Part("Laser Pointer", "Stolen laser of the Defender. Doubles laser damage.", "*", "laserDamage", 2, 0),
             Part("Charged Battery", "Stolen battery of the Defender. Increases charging speed of lasers and bullets.", "+", ["chargingSpeed", "laserChargeSpeed"], [-150, -300], 0 ),
             ]

#badParts = []