from functions import *
from pypdf import PdfReader, PdfWriter

sheets_per_signature = 4
back = True
sheet_type = "A4"
oS = "landscape"
desiredDisposition = None
filepath = "09thOctober.pdf"
signature = None

# Step 1: read the original PDF and perform some calculations
writer = PdfWriter()
oL, nPages_logic, dimension_logic = logicDetails(filepath)
pages_per_side, pages_per_sheet, signatures, sheets_per_signature = bookLayout(
    signature, sheets_per_signature, nPages_logic, back, dimension_logic, sheet_type, oL, oS, desiredDisposition)
tot_available = signatures * sheets_per_signature * pages_per_sheet
remainder = tot_available - nPages_logic
pagesPDF = int(tot_available / pages_per_side)
dim_oriented_s = dimensionCalc(sheet_type, oS)

# Step 2: depending on results, perform the imposition process
pdfOrder, pages_per_sheet = imp(signatures, sheets_per_signature, tot_available, True, dimension_logic, sheet_type, oL, oS, desiredDisposition)

# Step 3: create the dummy PDF
fillAndReshuffle(filepath, remainder, dimension_logic, pdfOrder, "resh.pdf")
reshuffled = PdfReader("resh.pdf")

# Step 4: Add blank pages with the dim_pt as many pages_PDFfinal and paste the original imposed pages
for sh in range(pagesPDF): 
    blank = writer.add_blank_page(width=dim_oriented_s[0], height=dim_oriented_s[1])
    desiredDisposition = opt_orientation(dimension_logic, dim_oriented_s)
    if desiredDisposition == "hor":
        offset_x = dim_oriented_s[0]/pages_per_side
        offset_y = 0
    else:
        offset_y = dim_oriented_s[1]/pages_per_side
        offset_x = 0
    p = []
    for tot in range(0, tot_available):
        p = p + [reshuffled.pages[tot]]

for sh in range(0, pagesPDF):
    i = sh*pages_per_side 
    blank = writer.add_blank_page(width=dim_oriented_s[0], height=dim_oriented_s[1])
    for n in range(0, pages_per_side):
        print(i)
        if desiredDisposition == "hor":
            p_rescaled = p[i].scale_to(dim_oriented_s[0]/pages_per_sheet, dim_oriented_s[1])
        else:
            p_rescaled = p[i].scale_to(dim_oriented_s[0], dim_oriented_s[1]/pages_per_sheet)
        blank.merge_translated_page(p[i], offset_x*n, offset_y*n)
        i = i + 1

with open ("final.pdf", 'wb') as f:
    writer.write(f)



# Farle tutte al centro (perché dove sono i margini dipende dall'imposition che faccio qui), e POI successivamente imporre offset_x: per la prima pagina 0, per la seconda pagina "dim_oriented_s[0]-dimensione_logic_x"


# Future develops: add possibility to select "hor + ver" in case for example I want 4 pages inside a single sheet and they must be displaced 2 x 2
