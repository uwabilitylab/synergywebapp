import pandas as pd

def CSVreader(csvfile):
#    if csvfile.endswith(".csv"):
#        new = pd.read_csv(csvfile)
#    if csvfile.endswith(".xlsx"):
#        new = pd.read_excel(csvfile)

    new = pd.read_excel(open(csvfile, 'rb'), sheetname='P001__Shoe_Dyn_Knee_Rep_l_2.39')

    return new
