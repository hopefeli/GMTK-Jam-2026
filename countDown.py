#
# countDown for GMTK game jam
#
# Compilation command "pyinstaller --onefile countDown.py"
#

VERSION = "0.10"

header = ("COUNTDOWN GAMEJAM - VERSION : " + VERSION)
print(header)

# Importing libraries
import pygame
import ctypes
import time
import copy

pygame.init()
pygame.font.init()

nativeDisplaySize = (1920, 1080)
display = pygame.Surface(nativeDisplaySize)
FPS = 30
gfx = {}
tileSize = 135
tileImages = {
              "." : "empty",
              "#" : "empty",
              "@" : "MC-sprite-stand",
              "B" : "crate-wooden",
              "0" : "floor-concrete-corner-2",
              "1" : "floor-concrete-corner-divide",
              "2" : "floor-concrete-divide-top",
              "3" : "floor-concrete-divide",
              "4" : "floor-concrete-left",
              "5" : "floor-concrete-right",
              "6" : "floor-concrete-top-1",
              "7" : "floor-concrete-top-2",
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
              "=" : "stairs-concrete",
              }
font = pygame.font.Font(".\\assets\\MonospaceRegular-6ZWg.ttf", 40)#'Comic Sans MS', 40)
showingText = False
dialogueQueue = []
currentDialogue = ""
pressingInteract = 0
alreadyMoved = False
moveDir = [0, 0]
records = []
cloudX = 0
standable = [".", "="]
stairs = ["=", "+"]
won = False
levelNum = 0

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
        elif fileExtension == "ogg":
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

def Draw (screenScaled, level):
    global display
    display.fill("#FF0000")
    clouds = gfx["sprites"]["bg-cloudy"]
    display.blit(clouds, ((cloudX) % clouds.get_width(), 0))
    display.blit(clouds, (((cloudX) % clouds.get_width()) - clouds.get_width(), 0))
    # Draw the game screen
    for i in range(len(level) - 1, -1, -1):
        for y in range(0, len(level[i])):
            for x in range(0, len(level[i][y])):
                if level[i][y][x] != ".":
                    display.blit(gfx["tiles"][tileImages[level[i][y][x]]], (x * tileSize, y * tileSize))
    # Draw textbox
    if showingText:
        # Draw background
        if currentDialogue[0] in gfx["illustrations"]:
            display.blit(gfx["illustrations"][currentDialogue[0]], (0, 0))
        # Text
        textBox = gfx["sprites"]["TextBox"].copy()
        textSurface = DrawText(currentDialogue[2], (900, 600))
        textBox.blit(textSurface, (620, 80))
        # Add button tip
        buttonTip = DrawText("Press space to continue...", (700, 80))
        textBox.blit(buttonTip, (textBox.get_width() - buttonTip.get_width() - 80, textBox.get_height() - buttonTip.get_height() - 80))
        # Add pfp
        pfpName = currentDialogue[1]
        if pfpName in gfx["cutsceneImages"]:
            textBox.blit(gfx["cutsceneImages"][pfpName], (80, 80))
        # Blit textbox onto screen
        display.blit(textBox, (((nativeDisplaySize[0] - textBox.get_width()) * 0.5), textBox.get_height() - 200))
    # Scale and flip the display
    pixelScale = 1
    if (screenScaled.get_width() / nativeDisplaySize[0]) < (screenScaled.get_height() / nativeDisplaySize[1]):
        pixelScale = (screenScaled.get_height() / nativeDisplaySize[1])
    else:
        pixelScale = (screenScaled.get_width() / nativeDisplaySize[0])
    screenScaled.blit(pygame.transform.scale(display, (nativeDisplaySize[0] * pixelScale, nativeDisplaySize[1] * pixelScale)), (0, 0))
    pygame.display.flip()

def ParseLevel (string):
    level = []
    layers = string.split("~")
    for layer in layers:
        level.append([])
        lines = layer.split("\n")
        for line in lines:
            if list(line) != []:
                level[-1].append(list(line))
    return level

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
    # Play undoing
    if (pressingInteract % moveWait) == 1 and len(records) > 1:
        records.pop(-1)
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
            records[:] = GetCurrentLevel()
        # If nothing has changed, delete newest record
        if len(records) > 1 and records[-1] == records[-2]:
            records.pop(-1)
    return running

def Win(level, x, y):
    global won
    if x == 14 and level[0][y][x] == "@":
        won = True

def Down(level, x, y):
    global alreadyMoved
    if not alreadyMoved:
        if level[0][y][x] == "@":
            if level[1][y + 1][x] in standable:
                if level[0][y + 1][x] == "B":
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
                if level[0][y - 1][x] == "B":
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
                if level[0][y][x + 1] == "B":
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
                if level[0][y][x - 1] == "B":
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
        if level[0][y - 1][x] == "B":
            if BoxUp(level, x, y - 1):
                level[0][y - 1][x] = "B"
                level[0][y][x] = "."
                return True
        else:
            level[0][y - 1][x] = "B"
            level[0][y][x] = "."
            return True
    return False

def BoxDown(level, x, y):
    if level[1][y + 1][x] in standable:
        if level[0][y + 1][x] == "B":
            if BoxUp(level, x, y + 1):
                level[0][y + 1][x] = "B"
                level[0][y][x] = "."
                return True
        else:
            level[0][y + 1][x] = "B"
            level[0][y][x] = "."
            return True
    return False

def BoxLeft(level, x, y):
    if level[1][y][x - 1] in standable:
        if level[0][y][x - 1] == "B":
            if BoxLeft(level, x - 1, y):
                level[0][y][x - 1] = "B"
                level[0][y][x] = "."
                return True
        else:
            level[0][y][x - 1] = "B"
            level[0][y][x] = "."
            return True
    return False

def BoxRight(level, x, y):
    if level[1][y][x + 1] in standable:
        if level[0][y][x + 1] == "B":
            if BoxRight(level, x + 1, y):
                level[0][y][x + 1] = "B"
                level[0][y][x] = "."
                return True
        else:
            level[0][y][x + 1] = "B"
            level[0][y][x] = "."
            return True
    return False

def Gravity(level, x, y):
    if level[0][y][x] == "@" and level[1][y][x] == ".":
        if level[0][y + 1][x] == "." and level[1][y + 1][x] == ".":
            level[0][y + 1][x] = "@"
            level[0][y][x] = "."
    if level[0][y][x] == "B" and level[1][y][x] == ".":
        if level[0][y + 1][x] == "." and level[1][y + 1][x] == ".":
            level[0][y + 1][x] = "B"
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
    records = [ParseLevel(gfx["levels"]["level" + str(levelNum)])]
    return records

def PrepDialogue (fileName):
    global dialogueQueue
    dialogue = gfx["dialogue"][fileName]
    lines = dialogue.split("\n")
    for line in lines:
        if line.split() != []:
            blank = "".join(line.split("-")[0].split())
            pfp, text = line.split("-")[1].split(":")
            pfp = "".join(pfp.split())
            cleanText = FormatChunk(text, 32)
            dialogueQueue.append([blank, pfp, cleanText])

def MainLoop ():
    screenScaled = SetupDisplay()
    lastFrame = time.perf_counter()
    running = True
    LoadGraphics()
    records = GetCurrentLevel()
    PrepDialogue("start")
##    dialogueQueue.append("Hello there! Blahblahblahblah")
##    dialogueQueue.append("Have you ever been to the moon?\nI have.")
##    dialogueQueue.append("Ham and cheese omlete")
    while (running):
        while time.perf_counter() - lastFrame < (1 / FPS):
            pass#print(time.perf_counter() - lastFrame)
        lastFrame = time.perf_counter()
        Draw(screenScaled, records[-1])
        running = Tick(records)
        
    pygame.quit()
    print("Game ended.")

MainLoop()
