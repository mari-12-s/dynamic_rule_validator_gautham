import pandas as pd
import json
import fitz  # PyMuPDF
import re
import rule_engine as ren

json_path = 'calctestdata.json'
json_path2 = 'calcTestdata2.json'
excel_path = "Rules.xlsx"
excel_path2 = "Tables.xlsx"

def formula_calc(formula, jdata):
    formulaString = formula.lower().replace(' ', '').replace('sum', '')
    #print(formulaString)
    result = []
    for val in jdata:
        lval = {key.lower(): value for key, value in val.items()}
        try:
            result.append(eval(formulaString, {}, lval))
        except:
            print("")
    #print(sum(result))
    return(sum(result))
    

def parseJsonData(xpathString, foundval):
    xpathArr = xpathString.split('/')
    foundValLocal = foundval
    for x in xpathArr:
        if isinstance(foundValLocal, dict):
            keyText = (next(iter(foundValLocal)))
            foundValLocal = foundValLocal[x]
        elif isinstance(foundValLocal, list):
            for fval in foundValLocal:
                foundValLocal = fval[x]
        else:
            print(foundValLocal) 
    return foundValLocal

def extract_table_value(search_row_name, search_col_name, table_df):
    search_value = search_row_name #'Total Claim Cost'
    try:
        match = table_df.apply(lambda col: col == search_value).any()
        matched_columns = ''.join(match[match].index.tolist())
        
        row = table_df[table_df[matched_columns] == search_value]
        
        req_val = row[search_col_name].values[0] #row["SPS"].values[0]

        #print(req_val)

        return req_val
    except :
        return ""

# def read_json_ind_val(json_path):
#     my_object = json.load(open(json_path, 'r'))
#     result = []
#     for objct in my_object.get("planDesign"):
#         i = 1
#         result.append(objct.get("monthlyClaimCost"))
#         i = i+1
#     return sum(result)
#######################################################################
# def calc_engine_validations():
#     tables_df = pd.read_excel(excel_path2, sheet_name=None)
#     with open(json_path, 'r') as f:
#         values = json.load(f)
#     rules_df = ren.load_rules(excel_path)
#     results = ['PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS']
#     for index, row in rules_df.iterrows():
        # print(index)
        #input_val = row.get('Input Value')
        # expected = row['Output Language']
        # expected2 = row['Ouput Label']
        #jdata = parseJsonData("plan/eligibilityClass/planDesign", values)

        # if ('∑') in expected:
        #     formulaText = expected.replace('∑', '').replace('<', '').replace('>', '')
        #     #1
        #     parsedData = parseJsonData("plan/eligibilityClass/planDesign", values)
        #     #2
        #     calculatedFormula = formula_calc(formulaText, parsedData)
        #     #3
        #     flag = 'FAIL'
        #     for i, tdf in enumerate(tables_df):
        #         pdf_total = extract_table_value(expected2, "SPS", tables_df[tdf])
        #         if (calculatedFormula == pdf_total):
        #             flag = 'PASS'
                #4

                #prin("Table Vaule: ", pdf_total)
                #prin("Are values matching: ", pdf_total == calculateFormula)
                #calc_total = read_json_ind_val(json_path)
                # if (pdf_total == calc_total):
                #     prin(True)
                #     testpassed = True
                # elif (i+1 == len(df) and (not testpassed)):
                #     prin(False)
                # prin(i)
                #prin(testpassed)
            #prin("Final Result: ", calculateFormula(expected, jdata))
            #find_total(row['Output Label'])
            #exp = expected.lower().replace('SUM', '').replace(' ', '')
            #pdf_total = find_total(exp, "SPS", df[dfs])
            #for i, dfs in enumerate(df):
             # pdf_total = find_total("Total Claim Cost 3", "SPS", df[dfs])
                # calc_total = read_json_ind_val(json_path)
                # if (pdf_total == calc_total):
                #     prin(True)
                #     testpassed = True
                # elif (i+1 == len(df) and (not testpassed)):
                #     prin(False)
                #prin(i)
                #prin(testpassed)
    #         print(index)
    #         print(flag)
    #         results.append(flag)
    #     else:
    #         'No Calculation'
    # print(results)
    # return results
    # rules_df['Result'] = results
    # rules_df.to_excel("rule_results.xlsx", index=False)
#######################################################################
    
def calc_engine_validation(row):
    expected = row['Output Language']
    expected2 = row['Ouput Label']
    tables_df = pd.read_excel(excel_path2, sheet_name=None)
    with open(json_path, 'r') as f:
        values = json.load(f)
    #rules_df = ren.load_rules(excel_path)
    results = ""
    #jdata = parseJsonData("plan/eligibilityClass/planDesign", values)

    if ('∑') in expected:
        formulaText = expected.replace('∑', '').replace('<', '').replace('>', '')
        #1
        parsedData = parseJsonData("plan/eligibilityClass/planDesign", values)
        #2
        calculatedFormula = formula_calc(formulaText, parsedData)
        #3
        flag = 'FAIL'
        for i, tdf in enumerate(tables_df):
            pdf_total = extract_table_value(expected2, "SPS", tables_df[tdf])
            if (calculatedFormula == pdf_total):
                flag = 'PASS'
        #print(flag)
        return flag
    else:
        'No Calculation'
    print(results)
    return results
    
# if __name__ == "__main__":
#     main()