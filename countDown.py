#
# countDown for GMTK game jam
#
# Compilation command "pyinstaller --onefile countDown.py"
#

VERSION = "0.16"

header = ("COUNTDOWN GAMEJAM - VERSION : " + VERSION)
print(header)

# Importing libraries
import pygame
import ctypes
import time
import copy

pygame.init()
pygame.font.init()

pygame.mixer.pre_init(44100, -16, 2, 512)#4096)
pygame.mixer.init()

nativeDisplaySize = (1920, 1080)
display = pygame.Surface(nativeDisplaySize)
FPS = 30
gfx = {}
tileSize = 135
tileImages = {
              "." : "empty",
              "@" : "MC-sprite-stand",
              "*" : "MC-sprite-dead",
              "%" : "crate-wooden",
              "a" : "building-blue-left",
              "b" : "building-blue-right",
              "c" : "building-blue-variant-1",
              "d" : "building-blue-variant-2",
              "e" : "building-blue",
              "f" : "building-door",
              "g" : "building-entry-left",
              "h" : "building-entry-middle",
              "i" : "building-entry-right",
              "j" : "building-window-1",
              "k" : "building-window-2",
              "A" : "buliding-teal-left",
              "B" : "buliding-teal-right",
              "C" : "buliding-teal-top-left",
              "D" : "buliding-teal-top-right",
              "E" : "buliding-teal-top",
              "F" : "buliding-teal",
              "0" : "floor-concrete-corner-2",
              "1" : "floor-concrete-corner-divide",
              "2" : "floor-concrete-divide-top",
              "3" : "floor-concrete-divide",
              "4" : "floor-concrete-left",
              "5" : "floor-concrete-right",
              "6" : "floor-concrete-top-1",
              "7" : "floor-concrete-top-2",
              "=" : "stairs-concrete-right",
              "+" : "stairs-concrete-left",
              "[" : "stairs-building-left",
              "]" : "stairs-building-right",
              "(" : "stairs-rail-left",
              ")" : "stairs-rail-right",
              ":" : "ladder",
              }
font = pygame.font.Font(".\\assets\\MonospaceRegular-6ZWg.ttf", 40)#'Comic Sans MS', 40)
fontBig = pygame.font.Font(".\\assets\\MonospaceRegular-6ZWg.ttf", 160)
showingText = False
dialogueQueue = []
currentDialogue = ""
pressingInteract = 0
alreadyMoved = False
moveDir = [0, 0]
records = []
cloudX = 0
stairs = ["=", "+", "[", "]", ":"]
standable = ["."] + stairs
won = False
levelNum = 0
allowedMoves = 0
debug = False
selX = 0
selY = 0
selZ = 0
tileSelX = 0
tileSelY = 0
tileSelDir = [0, 0]

def DepthDictInsert (dictionary, path, item):
    subDict = dictionary
    for key in path[:-1]:
        if key not in subDict:
            subDict[key] = {}
        subDict = subDict[key]
    subDict[path[-1]] = item

def DepthDictGet (dictionary, path):
    subItem = dictionary
    for key in path:
        if subItem:
            if (key not in subItem):
                subItem = None
            else:
                subItem = subItem[key]
    return subItem

def LoadStructure (structureDefPath):
    # Load structure definition
    f = open((structureDefPath + "_structure.txt"), "r")
    structStr = str(f.read())
    f.close()
    structLines = structStr.split("\n")
    # Remove empty lines
    lineNum = 0
    while lineNum < len(structLines):
        if structLines[lineNum].split() == []:
            del structLines[lineNum]
        else:
            lineNum += 1
    # Parse and load
    structure = {}
    subFolders = []
    for line in structLines:
        # Calculate level of indentation for each line
        indentationLevel = 0
        while line[indentationLevel] == "\t":
            indentationLevel += 1
        if indentationLevel > len(subFolders):
            raise IndentationError(line)
        # If indentation decreases, reduce the depth of the folder
        while len(subFolders) > indentationLevel:
            del subFolders[-1]
        # fileFullName includes the extention, fileName doesn't.
        fileFullName = "".join(line.split())
        filePath = structureDefPath + "\\" + "\\".join(subFolders) + "\\"
        if "." in fileFullName:
            fileName, fileExtension = fileFullName.split(".")
        else:
            fileName = fileFullName
            fileExtension = ""
        # Check if this is a duplicated item
        if DepthDictGet(structure, (subFolders + [fileName])):
            raise KeyError("Duplicate File: " + str(subFolders + [fileName]))
        # Load in the correct file/folder and add it to the structure dictionary
        if fileExtension == "":
            # Load folder
            subFolders.append(fileFullName)
        elif fileExtension == "txt":
            # Load text file
            f = open((filePath + fileFullName), "r")
            text = str(f.read())
            f.close()
            DepthDictInsert(structure, (subFolders + [fileName]), text)
        elif fileExtension in ["bmp", "png"]:
            # Load image file
            image = pygame.image.load(filePath + fileFullName).convert_alpha()
            DepthDictInsert(structure, (subFolders + [fileName]), image)
        elif fileExtension in ["ogg", "wav"]:
            # Load sound file
            sound = pygame.mixer.Sound(filePath + fileFullName)
            DepthDictInsert(structure, (subFolders + [fileName]), sound)
    return structure

def LoadGraphics ():
    global gfx
    gfx = LoadStructure("assets\\")
    print("gfx = " + str(gfx))
    #input()

def GetDisplaySize ():
    displayModes = pygame.display.list_modes()
    displaysizew = int(displayModes[0][0] * 0.8)
    displaysizeh = int(displayModes[0][1] * 0.8)
    return (displaysizew, displaysizeh)

def SetupDisplay ():
    ctypes.windll.user32.SetProcessDPIAware()
    size = GetDisplaySize()
    screenScaled = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption(header)
    return screenScaled

def DrawText (text, size):
    lineHeight = 60
    textSurface = pygame.Surface(size, pygame.SRCALPHA)
    for i in text:
        lines = text.split("\n")
    lineNum = 0
    for line in lines:
        textLine = font.render(line, True, (0, 0, 255))
        textSurface.blit(textLine, (0, lineNum * lineHeight))
        lineNum += 1
    return textSurface

def Draw (screenScaled, records):
    global display
    level = records[-1]
    display.fill("#FF0000")
    clouds = gfx["sprites"]["bg-cloudy"]
    display.blit(clouds, ((cloudX) % clouds.get_width(), 0))
    display.blit(clouds, (((cloudX) % clouds.get_width()) - clouds.get_width(), 0))
    busStopX = -8
    busStopY = -8
    # Draw the game screen
    for i in range(len(level) - 1, -1, -1):
        if debug:
            if i == selZ:
                drawLayer = True
            else:
                drawLayer = False
        else:
            drawLayer = True
        for y in range(0, len(level[i])):
            for x in range(0, len(level[i][y])):
                if level[i][y][x] != ".":
                    if level[i][y][x] == "$":
                        busStopX = x
                        busStopY = y
                    else:
                        img = gfx["tiles"][tileImages[level[i][y][x]]].copy()
                        if drawLayer:
                            display.blit(img, (x * tileSize, y * tileSize))
                        else:
                            img.set_alpha(40)
                            display.blit(img, (x * tileSize, y * tileSize))
    # Draw busstop
    display.blit(gfx["sprites"]["bus-stop"], (busStopX * tileSize, busStopY * tileSize))
    display.blit(gfx["sprites"]["bus-stop-sign"], ((busStopX - 2) * tileSize, busStopY * tileSize))
    # Selector
    if debug:
        display.blit(gfx["tiles"]["MC-sprite-dead"], (selX * tileSize, selY * tileSize))
    # Draw textbox
    if showingText:
        # Draw background
        if currentDialogue[0] in gfx["illustrations"]:
            display.blit(gfx["illustrations"][currentDialogue[0]], (0, 0))
        # Text
        textBox = gfx["sprites"]["TextBox"].copy()
        textSurface = DrawText(currentDialogue[2], (900, 600))
        textBox.blit(textSurface, (540, 40))
        # Add button tip
        buttonTip = DrawText("Press space to continue...", (700, 80))
        textBox.blit(buttonTip, (textBox.get_width() - buttonTip.get_width() - 80, textBox.get_height() - buttonTip.get_height() - 80))
        # Add pfp
        pfpName = currentDialogue[1]
        if pfpName in gfx["cutsceneImages"]:
            textBox.blit(gfx["cutsceneImages"][pfpName], (80, 80))
        # Blit textbox onto screen
        display.blit(textBox, (((nativeDisplaySize[0] - textBox.get_width()) * 0.5), textBox.get_height() - 200))
    # Draw countdown
    if not showingText:
        movesRemaining = allowedMoves - (len(records) - 1)
        moveText = str(movesRemaining) + "/" + str(allowedMoves)
        #counter = DrawText(str(movesRemaining), (80, 80))
        counter = fontBig.render(moveText, True, (0, 0, 255))
        display.blit(counter, (((nativeDisplaySize[0]) * 0.5) - (counter.get_width() * 0.5), 100))
    # Scale and flip the display
    pixelScale = 1
    if (screenScaled.get_width() / nativeDisplaySize[0]) < (screenScaled.get_height() / nativeDisplaySize[1]):
        pixelScale = (screenScaled.get_height() / nativeDisplaySize[1])
    else:
        pixelScale = (screenScaled.get_width() / nativeDisplaySize[0])
    if not debug:
        screenScaled.blit(pygame.transform.scale(display, (nativeDisplaySize[0] * pixelScale, nativeDisplaySize[1] * pixelScale)), (0, 0))
    else:
        screenScaled.blit(pygame.transform.scale(display, (nativeDisplaySize[0] * pixelScale, nativeDisplaySize[1] * pixelScale * 0.5)), (0, nativeDisplaySize[1] * pixelScale * 0.5))
        # Draw tile select
        display.fill("#0000FF")
        x = 0
        y = 0
        for i in sorted(tileImages.keys()):
            display.blit(gfx["tiles"][tileImages[i]], (x * tileSize, y * tileSize))
            if x == tileSelX and y == tileSelY:
                pygame.draw.rect(display, "#FFFFFF", (x * tileSize, y * tileSize, tileSize, tileSize), 5)
            x += 1
            if x > 13:
                x = 0
                y += 1
        screenScaled.blit(pygame.transform.scale(display, (nativeDisplaySize[0] * pixelScale, nativeDisplaySize[1] * pixelScale * 0.5)), (0, 0))
    pygame.display.flip()

def ParseLevel (string):
    level = []
    layers = string.split("~")
    allowedMoves = int(layers[0])
    layers = layers[1:]
    for layer in layers:
        level.append([])
        lines = layer.split("\n")
        for line in lines:
            if list(line) != []:
                level[-1].append(list(line))
    return level, allowedMoves

def ForEachTile (level, tileFunc):
    for y in range(0, len(level[0])):
        for x in range(0, len(level[0][y])):
            tileFunc(level, x, y)

def Tick (records):
    global dialogueQueue
    global currentDialogue
    global showingText
    global pressingInteract
    global alreadyMoved
    global moveDir
    global cloudX
    global won
    global levelNum
    global allowedMoves
    global debug
    global selX, selY, selZ
    global tileSelDir
    global tileSelX, tileSelY
    running = True
    cloudX += 1
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_RETURN]:
        pressingInteract += 1
    else:
        pressingInteract = 0

    # Allow player to navigate dialogue
    if pressingInteract == 1 and showingText:
        if len(dialogueQueue) == 0:
            showingText = False
        else:
            currentDialogue = dialogueQueue.pop(0)
    if len(dialogueQueue) > 0:
        if not showingText:
            showingText = True
            currentDialogue = dialogueQueue.pop(0)

    if debug:
        showingText = False
        dialogueQueue = []
        currentDialogue = []
    
    # Player movement
    moveWait = 4
    alreadyMoved = False
    if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
        moveDir = [max(0, moveDir[0]), 0]
        moveDir[0] += 1
    elif keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        moveDir = [min(0, moveDir[0]), 0]
        moveDir[0] -= 1
    elif keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
        moveDir = [0, min(0, moveDir[1])]
        moveDir[1] -= 1
    elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
        moveDir = [0, max(0, moveDir[1])]
        moveDir[1] += 1
    else:
        moveDir = [0, 0]
    # Debug
    if keys[pygame.K_LSHIFT] and keys[pygame.K_p]:
        debug = True
        print("DEBUG ON")
    if keys[pygame.K_LSHIFT] and keys[pygame.K_o]:
        debug = False
        print("DEBUG OFF")
    # Play undoing
    if not debug:
        if (pressingInteract % moveWait) == 1 and len(records) > 1:
            records.pop(-1)
    if debug:
        if keys[pygame.K_q]:
            print("LEVEL #" + str(levelNum) + " :")
            text = str(allowedMoves)
            for i in range(0, len(records[-1])):
                text += "\n~"
                for y in range(0, len(records[-1][i])):
                    text += "\n"
                    for x in range(0, len(records[-1][i][y])):
                        text += records[-1][i][y][x]
            print(text)
        if keys[pygame.K_1]:
            selZ = 0
            print("Z = 0")
        if keys[pygame.K_2]:
            selZ = 1
            print("Z = 1")
        if keys[pygame.K_3]:
            selZ = 2
            print("Z = 2")
        if keys[pygame.K_4]:
            selZ = 3
            print("Z = 3")
        # Nav tile select
        if keys[pygame.K_w]:
            tileSelDir[1] -= 1
        elif keys[pygame.K_s]:
            tileSelDir[1] += 1
        elif keys[pygame.K_a]:
            tileSelDir[0] -= 1
        elif keys[pygame.K_d]:
            tileSelDir[0] += 1
        else:
            tileSelDir = [0, 0]
        if tileSelDir[0] < 0 and (-tileSelDir[0] % moveWait) == 1:
            tileSelX -= 1
            tileSelX = max(0, tileSelX)
        if tileSelDir[0] > 0 and (tileSelDir[0] % moveWait) == 1:
            tileSelX += 1
            tileSelX = min(13, tileSelX)
        if tileSelDir[1] < 0 and (-tileSelDir[1] % moveWait) == 1:
            tileSelY -= 1
            tileSelY = max(0, tileSelY)
        if tileSelDir[1] > 0 and (tileSelDir[1] % moveWait) == 1:
            tileSelY += 1
            tileSelY = min(13, tileSelY)
        if pressingInteract > 0:
            if selY > -1 and selY < len(records[-1][0]) and selX > -1 and selX < len(records[-1][0][0]):
                keyIndex = tileSelX + (tileSelY * 14)
                key = sorted(tileImages.keys())[keyIndex]
                records[-1][selZ][selY][selX] = key
                print("TILE: " + str(records[-1][selZ][selY][selX]))

    # Update game state
    move = False
    if moveDir[0] > 0 and (moveDir[0] % moveWait) == 1:
        move = True
    if moveDir[0] < 0 and (-moveDir[0] % moveWait) == 1:
        move = True
    if moveDir[1] > 0 and (moveDir[1] % moveWait) == 1:
        move = True
    if moveDir[1] < 0 and (-moveDir[1] % moveWait) == 1:
        move = True
    if move:
        if debug:
            # DEBUG MODE
            
            if True:#pressingInteract == 0:
                if moveDir[0] > 0:
                    selX += 1
                elif moveDir[0] < 0:
                    selX -= 1
                elif moveDir[1] > 0:
                    selY += 1
                elif moveDir[1] < 0:
                    selY -= 1
##            else:
##                if selY > -1 and selY < len(records[-1][0]) and selX > -1 and selX < len(records[-1][0][0]):
##                    tileChar = records[-1][selZ][selY][selX]
##                    keyIndex = 0
##                    for i in range(0, len(tileImages.keys())):
##                        if sorted(tileImages.keys())[i] == tileChar:
##                            keyIndex = i
##                    if moveDir[0] > 0:
##                        keyIndex += 1
##                        if keyIndex >= len(tileImages.keys()):
##                            keyIndex = 0
##                        key = sorted(tileImages.keys())[keyIndex]
##                        records[-1][selZ][selY][selX] = key
##                    elif moveDir[0] < 0:
##                        keyIndex -= 1
##                        if keyIndex < 0:
##                            keyIndex = len(tileImages.keys()) - 1
##                        key = sorted(tileImages.keys())[keyIndex]
##                        records[-1][selZ][selY][selX] = key
##                    print("TILE: " + str(records[-1][selZ][selY][selX]))
        else:
            #print(records[-1][0])
            # Copy to create new level state
            records.append(copy.deepcopy(records[-1]))
            # Move
            if moveDir[0] > 0:
                ForEachTile(records[-1], Right)
            elif moveDir[0] < 0:
                ForEachTile(records[-1], Left)
            elif moveDir[1] > 0:
                ForEachTile(records[-1], Down)
            elif moveDir[1] < 0:
                ForEachTile(records[-1], Up)
            # Gravity
            preLevel = []
            while preLevel != records[-1]:
                preLevel = copy.deepcopy(records[-1])
                ForEachTile(records[-1], Gravity)
            # Winning
            won = False
            ForEachTile(records[-1], Win)
            if won:
                # load in next level
                levelNum += 1
                records[:], allowedMoves = GetCurrentLevel()
            # If nothing has changed, delete newest record
            if len(records) > 1 and records[-1] == records[-2]:
                records.pop(-1)
            # If player is out of moves, die
            if len(records) > allowedMoves:
                ForEachTile(records[-1], Die)
    return running

def Win(level, x, y):
    global won
    if x == 14 and level[0][y][x] == "@":
        won = True

def Die(level, x, y):
    if level[0][y][x] == "@":
        level[0][y][x] = "*"

def Down(level, x, y):
    global alreadyMoved
    if not alreadyMoved:
        if level[0][y][x] == "@":
            if level[1][y + 1][x] in standable:
                if level[0][y + 1][x] == "%":
                    if BoxDown(level, x, y + 1):
                        alreadyMoved = True
                        level[0][y + 1][x] = "@"
                        level[0][y][x] = "."
                        return True
                else:
                    alreadyMoved = True
                    level[0][y + 1][x] = "@"
                    level[0][y][x] = "."
                    return True
    return False

def Up(level, x, y):
    global alreadyMoved
    if not alreadyMoved:
        if level[0][y][x] == "@" and level[1][y][x] in stairs:
            if level[1][y - 1][x] in standable:
                if level[0][y - 1][x] == "%":
                    if BoxUp(level, x, y - 1):
                        alreadyMoved = True
                        level[0][y - 1][x] = "@"
                        level[0][y][x] = "."
                        return True
                else:
                    alreadyMoved = True
                    level[0][y - 1][x] = "@"
                    level[0][y][x] = "."
                    return True
    return False

def Right(level, x, y):
    global alreadyMoved
    if not alreadyMoved:
        if level[0][y][x] == "@":
            if level[1][y][x + 1] in standable:
                if level[0][y][x + 1] == "%":
                    if BoxRight(level, x + 1, y):
                        alreadyMoved = True
                        level[0][y][x + 1] = "@"
                        level[0][y][x] = "."
                        return True
                else:
                    alreadyMoved = True
                    level[0][y][x + 1] = "@"
                    level[0][y][x] = "."
                    return True
    return False

def Left(level, x, y):
    global alreadyMoved
    if not alreadyMoved:
        if level[0][y][x] == "@":
            if level[1][y][x - 1] in standable:
                if level[0][y][x - 1] == "%":
                    if BoxLeft(level, x - 1, y):
                        alreadyMoved = True
                        level[0][y][x - 1] = "@"
                        level[0][y][x] = "."
                        return True
                else:
                    alreadyMoved = True
                    level[0][y][x - 1] = "@"
                    level[0][y][x] = "."
                    return True
    return False

def BoxUp(level, x, y):
    if level[1][y - 1][x] in standable:
        if level[0][y - 1][x] == "%":
            if BoxUp(level, x, y - 1):
                level[0][y - 1][x] = "%"
                level[0][y][x] = "."
                return True
        else:
            level[0][y - 1][x] = "%"
            level[0][y][x] = "."
            return True
    return False

def BoxDown(level, x, y):
    if level[1][y + 1][x] in standable:
        if level[0][y + 1][x] == "%":
            if BoxDown(level, x, y + 1):
                level[0][y + 1][x] = "%"
                level[0][y][x] = "."
                return True
        else:
            level[0][y + 1][x] = "%"
            level[0][y][x] = "."
            return True
    return False

def BoxLeft(level, x, y):
    if level[1][y][x - 1] in standable:
        if level[0][y][x - 1] == "%":
            if BoxLeft(level, x - 1, y):
                level[0][y][x - 1] = "%"
                level[0][y][x] = "."
                return True
        else:
            level[0][y][x - 1] = "%"
            level[0][y][x] = "."
            return True
    return False

def BoxRight(level, x, y):
    if level[1][y][x + 1] in standable:
        if level[0][y][x + 1] == "%":
            if BoxRight(level, x + 1, y):
                level[0][y][x + 1] = "%"
                level[0][y][x] = "."
                return True
        else:
            level[0][y][x + 1] = "%"
            level[0][y][x] = "."
            return True
    return False

def Gravity(level, x, y):
    if level[0][y][x] == "@" and level[1][y][x] == ".":
        if level[0][y + 1][x] == "." and level[1][y + 1][x] == ".":
            level[0][y + 1][x] = "@"
            level[0][y][x] = "."
    if level[0][y][x] == "%" and level[1][y][x] == ".":
        if level[0][y + 1][x] == "." and level[1][y + 1][x] == ".":
            level[0][y + 1][x] = "%"
            level[0][y][x] = "."

def FormatChunk (currentchunk, lineCutoff):
    # Add linebreaks
    lineText = ""
    lines = []
    charIndex = 0
    while charIndex < len(currentchunk):
        if currentchunk[charIndex] == "`":
            lines.append(lineText)
            lineText = ""
        elif len(lineText) >= lineCutoff:
            # If the line is too long,
            # back up to the previouse word and break there
            backupIndex = 1
            while backupIndex < len(lineText) and lineText[-backupIndex] not in [" ", "`", "#"]:
                backupIndex += 1
            charIndex -= backupIndex
            lines.append(lineText[:-backupIndex])
            lineText = ""
        else:
            lineText += currentchunk[charIndex]
        charIndex += 1
    lines.append(lineText)
    # Rejoin lines into a string
    currentchunk = "\n" + "\n".join(lines)
    return currentchunk

def GetCurrentLevel():
    level, allowedMoves = ParseLevel(gfx["levels"]["level" + str(levelNum)])
    records = [level]
    return records, allowedMoves

def PrepDialogue (fileName):
    global dialogueQueue
    dialogue = gfx["dialogue"][fileName]
    lines = dialogue.split("\n")
    for line in lines:
        if line.split() != []:
            blank = "".join(line.split("-")[0].split())
            pfp, text = line.split("-")[1].split(":")
            pfp = "".join(pfp.split())
            cleanText = FormatChunk(text, 40)
            dialogueQueue.append([blank, pfp, cleanText])

def MainLoop ():
    global allowedMoves
    screenScaled = SetupDisplay()
    lastFrame = time.perf_counter()
    running = True
    LoadGraphics()
    records, allowedMoves = GetCurrentLevel()
    PrepDialogue("start")
    pygame.mixer.Channel(1).play(gfx["audio"]["titletrack"], -1)
##    dialogueQueue.append("Hello there! Blahblahblahblah")
##    dialogueQueue.append("Have you ever been to the moon?\nI have.")
##    dialogueQueue.append("Ham and cheese omlete")
    while (running):
        while time.perf_counter() - lastFrame < (1 / FPS):
            pass#print(time.perf_counter() - lastFrame)
        lastFrame = time.perf_counter()
        Draw(screenScaled, records)
        running = Tick(records)
        
    pygame.quit()
    print("Game ended.")

MainLoop()
