#
# countDown for GMTK game jam
#
# Compilation command "pyinstaller --onefile countDown.py"
#

# Importing libraries
import pygame
import ctypes
import time

pygame.init()

nativeDisplaySize = (1920, 1080)
display = pygame.Surface(nativeDisplaySize)
FPS = 30
gfx = {}
tileSize = 135
tileImages = {
              "." : "empty",
              "#" : "floor0"
              }

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
        elif fileExtension == "bmp":
            # Load image file
            image = pygame.image.load(filePath + fileFullName)
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
    return screenScaled

def Draw (screenScaled, level):
    global display
    display.fill("#FF0000")
    # Draw the game screen
    for y in range(0, len(level)):
        for x in range(0, len(level[0])):
            display.blit(gfx["tiles"][tileImages[level[y][x]]], (x * tileSize, y * tileSize))
            
    # Scale and flip the display
    pixelScale = 1
    if (screenScaled.get_width() / nativeDisplaySize[0]) < (screenScaled.get_height() / nativeDisplaySize[1]):
        pixelScale = (screenScaled.get_height() / nativeDisplaySize[1])
    else:
        pixelScale = (screenScaled.get_width() / nativeDisplaySize[0])
    print(pixelScale)
    screenScaled.blit(pygame.transform.scale(display, (nativeDisplaySize[0] * pixelScale, nativeDisplaySize[1] * pixelScale)), (0, 0))
    pygame.display.flip()

def ParseLevel (string):
    level = []
    lines = string.split("\n")
    for line in lines:
        level.append(list(line))
    print(level)
    return level

def MainLoop ():
    screenScaled = SetupDisplay()
    lastFrame = time.perf_counter()
    running = True
    LoadGraphics()
    level = ParseLevel(gfx["levels"]["level0"])
    while (running):
        while time.perf_counter() - lastFrame < (1 / FPS):
            pass
        lastFrame = time.perf_counter()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        Draw(screenScaled, level)
    pygame.quit()
    print("Game ended.")

MainLoop()
