# Inputs:
# 1. number of total pages
# 2. dimension of sheet
# 3. dimension of logic page
# 4. amount of signature OR amount of sheets per signature
# 5. Front and back [boolean]
# 6. Metric or imperial system
# 7. Folding (booklet) / no folding

# Imports
import numpy as np

# Translation from "A0" etc to dimension in MM and take care of INCH in case imperial are selected
def dimensionCalc(layout):  # 
    paperMM = {"A0": [841, 1189], 
            "A1": [594, 841], 
            "A2": [420, 594], 
            "A3": [297, 420], 
            "A4": [210, 297], 
            "A5": [148, 210], 
            "A6": [105, 148], 
            "A7": [74, 105], 
            "B0": [1000, 1414],
            "B1": [707, 1000],
            "B2": [500, 707],
            "B3": [353, 500],
            "B4": [250, 353],
            "B5": [176, 250],
            "B6": [125, 176],
            "B7": [88, 125],
            "B8": [62, 88],
            "Letter": [216, 279],
            "Legal": [216, 356],
            "Tabloid": [279, 432],
            "Ledger": [432, 279]
            }
    if type(layout) is  str:
        dim = paperMM[layout]
    else:
        dim = layout
    return dim
# Return: dim

# Calculate sheets per signature and signature needed 
def bookLayout(dimLog, dimShe, sign, sheets, totPages, back):
    areaLog = dimLog[0] * dimLog[1]
    areaShe = dimShe[0] * dimShe[1]
    logicPages_perSheet = int(np.floor(areaShe / areaLog))
    if back:
        logicPages_perSheet = logicPages_perSheet * 2
    if sign is not None:
        sheets = int(np.ceil(totPages / logicPages_perSheet / sign))
    elif sheets is not None:
        sign = int(np.ceil(totPages / logicPages_perSheet / sheets))
    return logicPages_perSheet, sign, sheets
# Return: logicPages_perSheet, sign, sheets

# Check how those pages are fit inside the main sheet (vertical or horizontal)
def orientation(dimLogic, dimSheet):
    horiz = np.floor(dimSheet[0]/dimLogic[0])
    vert = np.floor(dimSheet[1]/dimLogic[1])
    if horiz >= vert:
        orientation = "landscape" # place the logical pages horizontally
    else:
        orientation = "portrait" # place the logical pages vertically
    return orientation
# Return: orientation

# Imposition per signature
def impPerSign(start, end, sheetsPerSignature, logicPages_perSheet, back):
    ls = list()
    for iteration in range(0, sheetsPerSignature): # 0, 1, 2, 3
        if back:
            frontLeft = end - logicPages_perSheet/2 * iteration 
            frontRight = start + logicPages_perSheet/2 * iteration
        else:
            frontLeft = end - logicPages_perSheet * iteration 
            frontRight = start + logicPages_perSheet * iteration
        backLeft = frontRight + 1
        backRight = frontLeft - 1
        ls.append(frontLeft)
        ls.append(frontRight)
        ls.append(backLeft)
        ls.append(backRight)
    return ls
# Return: array

# Calculate "start" and "end" depending on n° signatures and n° sheets per signature
def firstSheet(sheets, logicPages_perSheet, iteration):
    start = 1 + logicPages_perSheet * sheets * iteration # signIndex = 1 ... sign
    end = logicPages_perSheet * sheets + logicPages_perSheet * sheets * iteration
    return start, end
# Return: start, end