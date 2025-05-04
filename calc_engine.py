import pandas as pd
import json
import fitz  # PyMuPDF
import re
import rule_engine as ren

json_path = 'calctestdata.json'
json_path2 = 'calcTestdata2.json'
excel_path = "Rules.xlsx"
extracted_table_path = "Tables.xlsx"

#calculate formula
def formula_calc(formula, jdata):
    formulaString = formula.lower().replace(' ', '').replace('sum', '').replace(',', '+')
    print(formulaString)
    result = []
    for val in jdata:
        lval = {key.lower(): value for key, value in val.items()}
        try:
            result.append(eval(formulaString, {}, lval))
        except:
            print("")
    return(sum(result))
    
#parse json data to find req values
def parseJsonData(xpathString, foundval):
    xpathArr = xpathString.split('/')
    foundValLocal = foundval
    for x in xpathArr:
        if isinstance(foundValLocal, dict):
            foundValLocal = foundValLocal[x]
        elif isinstance(foundValLocal, list):
            for fval in foundValLocal:
                foundValLocal = fval[x]
        else:
            print(foundValLocal) 
    return foundValLocal

#search required values from extracted tables
def extract_table_value(search_row_name, search_column_name, table_df):
    search_col_name = search_column_name
    if (search_column_name == ""):
        search_col_name = 0
    else:
        search_col_name = search_column_name
    search_value = search_row_name
    try:
        match = table_df.apply(lambda col: col == search_value).any()
        matched_columns = ''.join(match[match].index.tolist())
        
        row = table_df[table_df[matched_columns] == search_value]
        if search_column_name == "":
            req_val = row.values[0][1]
        else:
            req_val = row[search_col_name].values[0]

        return req_val
    except :
        return ""

#main funtion for calc engine
def calc_engine_validation(row):
    opLabel = row['Ouput Label']
    opLanguage = row["Output Language"]
    ipValue = row["Input Value"]
    tables_df = pd.read_excel(extracted_table_path, sheet_name=None)
    with open(json_path, 'r') as f:
        values = json.load(f)
    if ('∑') in opLanguage:
        formulaText = opLanguage.replace('∑', '').replace('<', '').replace('>', '')
    else:
        formulaText = ipValue.replace('∑', '').replace('<', '').replace('>', '')
    parsedData = parseJsonData("plan/eligibilityClass/planDesign", values)
    calculatedFormula = formula_calc(formulaText, parsedData)
    flag = 'FAIL'
    before, sep, after = opLabel.partition(":")
    for i, tdf in enumerate(tables_df):
        pdf_total = extract_table_value(before, after, tables_df[tdf])
        if (calculatedFormula == pdf_total):
            flag = 'PASS'
    return flag