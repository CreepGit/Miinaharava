import pygame, time, random

# Class handy for Globals
class Settings:
    # Options
    gridSize = gridx, gridy = (30,25) #30,25.. 150 mines -> 20%
    mineCount = 150
    # Technical
    tileSize = 30
    screenSize = width, height = (gridx * tileSize + 1,gridy * tileSize + 31)
    frameRate = 15
    timerFrameRate = 15
    tileCount = gridy * gridx
    # Colors & Style
    colorClosed = (150,150,150)
    colorOpen = (192,198,198)
    colorOpenWin = (214,226,156)
    colorDefaultText = (0,0,0)
    colorFlag = (25,25,25)
    NumberSpecificColors = {
        1: (30, 73, 181),
        2: (53,153,30),
        3: (170,20,20),
        4: (60,47,140),
        5: (97,17,10),
        6: (204,148,18),
        7: (40,40,40),
        8: (0,0,0)
    }
    gameFont = "Comic Sans MS" # Font for tiles
    menuFont = "Lucida Bright"

class Tile:
    """Creates new tile object for storing information (like struct)"""
    def __init__(self, number = 0, mine = False):
        self.number = number
        self.isOpen = False
        self.hasFlag = False
        self.isMine = mine
    def __repr__(self):
        out = ""
        if self.isOpen:
            out += "o"
        if self.hasFlag:
            out += "f"
        return f"<{self.number}.{out}>"

class App:
    """Starts minesweeper app"""
    def __init__(self):
        self.screen = pygame.display.set_mode(Settings.screenSize)
        self.exiting = False
        self.grid = None
        self.timer = False
        self.time = 0
        self.flags = 0
        self.locked = False
        self.won = False
        pygame.display.set_caption(
            f"Minesweeper xy{Settings.gridSize} mines({Settings.mineCount}, {round(Settings.mineCount/Settings.tileCount*100,1)}%)")
        pygame.font.init()
        self.fontObject = pygame.font.SysFont(Settings.gameFont, 24)
        self.menuFontObject = pygame.font.SysFont(Settings.menuFont, 16)
        #
        self.draw()
        self.loop()

    def update(self):
        """Function that runs every frame of the game"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click(event.pos[0],event.pos[1],event.button)

    def loop(self):
        """Main loop of the function, calls update once every frame"""
        while True:
            self.update()
            if self.exiting:
                break
            # Can draw the timer multiple times per frame
            for x in range(max(1,int( Settings.timerFrameRate / Settings.frameRate ))):
                time.sleep(1 / Settings.timerFrameRate)
                self.drawTime()

    def close(self):
        """Calls for the closing of the App"""
        pygame.quit()
        self.exiting = True
        print("Quit app")

    def getNear(self, x, y):
        """Get x,y values for every nearby tile"""
        out = []
        for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
            if x + dx > Settings.gridx - 1:
                continue
            if x + dx < 0:
                continue
            if y + dy > Settings.gridy - 1:
                continue
            if y + dy < 0:
                continue
            out.append((x + dx,y + dy))
        return out

    def generate(self,x = -100, y = -100):
        """Generates a grid of mines and numbers. x,y = clear position"""
        # Starts timer
        self.timer = True
        self.time = time.time()

        if Settings.mineCount > Settings.tileCount:
            raise ValueError("Minecount cannot exceed tilecount.")
        # Set spots that are possible spots for mines
        allowMine = set([i for i in range(Settings.tileCount)])
        # Prevent mines spawning in starting area
        ln = Settings.gridx
        startIndex = ln * y + x
        for dIntex in (-ln-1, -ln, -ln+1, -1, 0, +1, ln-1, ln, ln+1):
            if dIntex + startIndex in allowMine:
                allowMine.remove(dIntex + startIndex)
        mineIndex = set()
        for _ in range(Settings.mineCount):
            chosen = random.choice(tuple(allowMine))
            allowMine.remove(chosen)
            mineIndex.add(chosen)
        mines = []
        for y in range(Settings.gridy):
            line = []
            for x in range(Settings.gridx):
                index = x + y * Settings.gridx
                if index in mineIndex:
                    line.append(True)
                else:
                    line.append(False)
            mines.append(line)
        
        out = []
        for y in range(Settings.gridy):
            line = []
            for x in range(Settings.gridx):
                if mines[y][x] == True:
                    line.append(Tile(number=-1,mine=True))
                else:
                    bombs = 0
                    for spotx, spoty in self.getNear(x,y):
                        if mines[spoty][spotx] == True:
                            bombs += 1
                    line.append(Tile(number=bombs))
            out.append(line)
        return out

    def drawTime(self):
        """Draws the timer only, useful if game framerate is much lower than the timer's"""
        if self.timer:
            nowTime = time.time()
        else:
            try:
                nowTime = self.lastTime
            except AttributeError:
                nowTime = 0.0
        fullMins = int((nowTime - self.time)//60)
        seconds = (nowTime - self.time)%60
        pygame.draw.rect(self.screen, Settings.colorClosed, (Settings.width - 80,1,79,29))
        textSurface = self.menuFontObject.render("{:3}:{:04}".format(fullMins,round(seconds,1)), True, Settings.colorDefaultText)
        self.screen.blit(textSurface, (Settings.width - 75,5))
        pygame.display.update((Settings.width - 80, 0, 100, 29))
        self.lastTime = nowTime

    def draw(self):
        """Draws the game on the screen"""
        self.screen.fill((50,50,50))
        # Menu
            # Restart button
        pygame.draw.rect(self.screen, Settings.colorClosed, (1,1,100,29))
        textSurface = self.menuFontObject.render("RESTART", True, Settings.colorDefaultText)
        self.screen.blit(textSurface, (11,5))
            # Timer
        self.drawTime()
            # Bomb Counter
        pygame.draw.rect(self.screen, Settings.colorClosed, (Settings.width - 130,1,49,29))
        textSurface = self.menuFontObject.render("{:5}".format(Settings.mineCount - self.flags), True, Settings.colorDefaultText)
        self.screen.blit(textSurface, (Settings.width - 130,5))
        # Grid
        ts = Settings.tileSize
        for y in range(Settings.gridy):
            for x in range(Settings.gridx):
                if self.grid == None:
                    tile = Tile()
                else:
                    tile = self.get(x,y)
                color = Settings.colorClosed
                if tile.isOpen:
                    color = Settings.colorOpen
                    if self.won:
                        color = Settings.colorOpenWin
                pygame.draw.rect(self.screen, color, (1 + x * ts,31 + y * ts,ts-1,ts-1))
                # Draw tile text over the tiles
                if tile.isOpen or self.locked:
                    textColor = Settings.colorDefaultText
                    # Set number specific colors if it exists
                    if tile.number in Settings.NumberSpecificColors.keys():
                        textColor = Settings.NumberSpecificColors[tile.number]
                    if tile.isMine:
                        textSurface = self.fontObject.render("X", True, textColor)
                        self.screen.blit(textSurface, (1 + x * ts + 5, 31 + y * ts - 3))
                    elif tile.number == 0:
                        pass # Dont draw number if value is 0
                    else:
                        textSurface = self.fontObject.render(str(tile.number), True, textColor)
                        self.screen.blit(textSurface, (1 + x * ts + 8, 31 + y * ts - 3))
                elif tile.hasFlag: # Is closed and has a flag
                    textSurface = self.fontObject.render("F", True, Settings.colorFlag)
                    self.screen.blit(textSurface, (1 + x * ts + 8, 31 + y * ts - 3))
                    
        #
        pygame.display.update()

    def click(self, screenX, screenY, button):
        """Processes where on the screen the user pressed and sends the info onto another function"""
        # If click is outside of the screen, skip it
        if screenX > Settings.width - 3:
            return
        if screenY > Settings.height - 3:
            return
        if screenY > 31:
            x = int(screenX // 30)
            y = int((screenY - 30) // 30)
            self.gridClick(x, y, button)
        else:
            self.menuClick(screenX)

    def gridClick(self, gridX, gridY, button):
        """Processes clicks on grid positions"""
        if self.grid == None:
            if button != 1:
                return # Non-left click does nothing without grid
            self.grid = self.generate(x = gridX,y = gridY)
        tile = self.get(gridX, gridY)
        if self.locked: 
            pass # Prevent left and rightclick when locked
        elif button == 1 and tile.hasFlag == False:
            tile.isOpen = True
            if tile.isMine:
                self.lose()
            elif tile.number == 0:
                self.wideOpen(gridX, gridY)
            self.draw()
            self.checkWin()
        elif button == 3 and not tile.isOpen:
            if tile.hasFlag:
                tile.hasFlag = False
                self.flags -= 1
            else:
                tile.hasFlag = True
                self.flags += 1
            self.draw()
    
    def menuClick(self, x):
        """Clicks on the top menu"""
        if x > 0 and x < 100:
            self.restart()

    def lose(self):
        """Function to call when you click a mine. Locks the gameboard"""
        self.locked = True
        self.timer = False
    
    def checkWin(self):
        """Test if you won the game."""
        for line in self.grid:
            for tile in line:
                # If there are any number tiles that are closed
                # Cancel win
                if not tile.isOpen and not tile.isMine:
                    return
        else:
            self.win()

    def win(self):
        """Function to call on win of the game, time for celebration!"""
        print("You won!")
        self.timer = False
        self.locked = True
        self.won = True
        self.draw()

    def restart(self):
        """Restarts the game, sets variables back to defaults"""
        print("RESTARTING THE GAME...")
        # Setting grid to none calls generator again on a click
        self.grid = None
        self.timer = False
        self.flags = 0
        self.locked = False
        self.won = False
        self.draw()

    def get(self, x, y):
        """Gets the grid tile at x,y position (function is only here so code is more readable)"""
        return self.grid[y][x]

    def wideOpen(self, x, y):
        """Behaviour for opening (or chain opening) empty (or 0) tiles"""
        self.get(x,y).isOpen = True
        for spotx, spoty in self.getNear(x, y):
            spotTile = self.get(spotx,spoty)
            if spotTile.hasFlag:
                spotTile.hasFlag = False
                self.flags -= 1
            if spotTile.number == 0 and not spotTile.isOpen:
                self.wideOpen(spotx, spoty)
            spotTile.isOpen = True

App()

