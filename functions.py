# Imports
import numpy as np
import pypdf as pp

# Translation from "A0" etc to dimension in MM and take care of INCH in case imperial are selected
def dimensionCalc(layout, o):  # 
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
        dim = paperMM[layout] # now convert it to pt
        dim = [dim[0]/0.353, dim[1]/0.353]
    else:
        dim = [layout[0]/0.353, layout[1]/0.353]
    if o == "landscape":
        if dim[0] > dim[1]:
            dim_o = [dim[0], dim[1]]
        else:
            dim_o = [dim[1], dim[0]]
    else:
        if dim[0] > dim[1]:
            dim_o = [dim[1], dim[0]]
        else:
            dim_o = [dim[0], dim[1]]
    return dim_o
# Return: dim

# Check how those pages are fit inside the main sheet (vertical or horizontal) - optimization
def opt_orientation(dimLogic, dimSheet):
    horiz = np.floor(dimSheet[0]/dimLogic[0])
    vert = np.floor(dimSheet[1]/dimLogic[1])
    if horiz >= 1 and vert >= 1:
        if horiz >= vert:
            o_orientation = "hor" # place the logical pages horizontally
        else:
            o_orientation = "ver" # place the logical pages vertically
        return o_orientation
    else:
        print("No layout is possible with this configuration.")
# Return: o_orientation

# Calculate sheets per signature and signature needed 
def bookLayout(sign, sheets, totPages, back, layoutL, layoutS, oL, oS, layout):
    orientedL = dimensionCalc(layoutL, oL)
    orientedS = dimensionCalc(layoutS, oS)
    if layout is None:
        layout = opt_orientation(orientedL, orientedS) # calculate the optimal way to place the pages
    if layout == "hor":
        nL_side = orientedS[0]/orientedL[0] # number of logic pages per front of sheet
    else:
        nL_side = orientedS[1]/orientedL[1]
    nL_side = int(np.floor(nL_side))
    nL_sheet = nL_side
    # If "front and back" is chosen as option:
    if back:
        nL_sheet = nL_side * 2
    if sign is not None:
        sheets = int(np.ceil(totPages / nL_sheet / sign))
    elif sheets is not None:
        sign = int(np.ceil(totPages / nL_sheet / sheets))
    return nL_side, nL_sheet, sign, sheets
# Return: nL, sign, sheets

# Final calculation for all signatures and sheets
def imp(signatures, sheets, totPages, frontBack, layoutL, layoutS, oL, oS, layout): # "layout" is optional
    nL_side, nL_sheet, signatures, sheets = bookLayout(signatures, sheets, totPages, frontBack, layoutL, layoutS, oL, oS, layout) 
    st = 1
    end = nL_sheet * sheets
    pdfOrder = []
    for s in range(0, signatures):
        for A in range(0, sheets):
            if frontBack:
                fl = int(end - nL_sheet/2*A)
                fr = int(st + nL_sheet/2*A)
                bl = fr + 1
                br = fl - 1
                pdfOrder = pdfOrder + [fl, fr, bl, br]
            else:
                fl = int(end - nL_sheet*A)
                fr = int(st + nL_sheet*A)
                pdfOrder = pdfOrder + [fl, fr] 
        st = end + 1
        end = end + nL_sheet*sheets
    return pdfOrder, nL_side

# Read the input PDF to get nPages and layout format
def logicDetails(filepath):
    reader = pp.PdfReader(filepath)
    nPages = len(reader.pages)
    for i, page in enumerate(reader.pages):
        box = page.mediabox
        width = float(box.width) #in pt
        height = float(box.height)
        # Conversion from pt to inch/mm or layout
        widthMM = width * 0.353
        heightMM = height * 0.353
    dLogic = [int(widthMM), int(heightMM)]
    # compute the current disposition of the original PDF (was it provided in landscape or portrait?)
    if dLogic[0] > dLogic[1]: 
        oL = "landscape"
    else:
        oL = "portrait"
    return oL, nPages, dLogic

# Create dummy pdf with the remainder blank pages to fill all the sheets
def fillAndReshuffle(filepath, remainder, logicDim, pdfOrder, middleman_path):
    reader = pp.PdfReader(filepath)
    writer = pp.PdfWriter()
    width_pt = logicDim[0] / 0.353 # writer wants it to be in pt instead of MM
    height_pt = logicDim[1] / 0.353
    for p in reader.pages:
        writer.add_page(p)
    for _ in range(1, remainder + 1):
        writer.add_blank_page(width=width_pt, height=height_pt)
    # Shuffle the pages depending on the pdfOrder variable
    shuffled = pp.PdfWriter()
    for index in pdfOrder: # starting from 1
        shuffled.add_page(writer.pages[index-1]) # staring from 0
        
    with open(middleman_path, 'wb') as res:
        shuffled.write(res)
