import imposition
import imposition
import pypdf as pp

# Inputs (dummy, will be placed in a query in HTML/JS)
nPages = 64
layoutLogic = "A5"
layoutSheet = "A4"
sheetsPerSignature = 4
signatures = None
frontBack = True
folding = True
units = "metric"
inputs = "09thOctober.pdf"

# Read the input PDF to get nPages and layout format
reader = pp.PdfReader(inputs)
nPages = len(reader.pages)
for i, page in enumerate(reader.pages):
    box = page.mediabox
    width = float(box.width) #in pt
    height = float(box.height)
    # Conversion from pt to inch/mm or layout
    widthMM = width * 0.353
    heightMM = height * 0.353
    widthINCH = width * 0.014
    heightINCH = height * 0.014
layoutLogic = [int(widthMM), int(heightMM)]

# Calc dimension for starting and final pdf pages
dimL = imposition.dimensionCalc(layoutLogic)
dimSh = imposition.dimensionCalc(layoutSheet)

# Calc amount of signature and sheets
logicPages_perSheet, sign, sheets = imposition.bookLayout(dimL, dimSh, signatures, sheetsPerSignature, nPages, frontBack)

# Tot available
tot = sign * sheets * logicPages_perSheet
# Remaining
r = tot - nPages

# Create dummy pdf with the remaining blank pages to fit all the sheets
writer = pp.PdfWriter()
for p in reader.pages:
    writer.add_page(p)
for blank in range(1, r+1):
    writer.add_blank_page(width=min(dimL), height=max(dimL))

with open("middleman.pdf", 'wb') as f:
    writer.write(f)

newReader = pp.PdfReader("middleman.pdf", 'wb')

# Page order computation considering X sheets and X signatures
finalList = list()
for s in range(0, sign):
    st, end = imposition.firstSheet(sheets, logicPages_perSheet, s)
    intList = imposition.impPerSign(st, end, sheets, logicPages_perSheet, frontBack)
    finalList.append(intList)
print(finalList)

# Creation of final product to be printed
newWriter = pp.PdfWriter()
for s in range(0, sign):
    for p in finalList[s]:
       p = int(p)
       print(p)
       newWriter.add_page(newReader.pages[p-1])
with open("finalProd.pdf", 'wb') as f:
    newWriter.write(f)


    # next step: add each of the 4 pages in a single sheet (depending on format ofc)