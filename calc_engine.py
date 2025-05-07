import pandas as pd
import json
from itertools import chain
import pdfplumber

json_path = 'calctestdata.json'
identifier = "planDesignName"
condition_identifier = "coverageTier"
identifierArr = []

#calculate formula
def formula_calculation(formula_string, json_data):
    formula = formula_string.lower().replace(' ', '').replace(',', '+').replace('x', '*')
    result = []
    identifierArr = []
    condition_identifier_arr = []
    for val in json_data:
        lval = {key.lower(): value for key, value in val.items()}

        identifierArr.append(lval[identifier.lower()])
        condition_identifier_arr.append(lval[condition_identifier.lower()])

        try:
            result.append(eval(formula, {}, lval))
        except:
            print("")
    identifierArr_local = identifierArr
    return (float(sum(result))), ', '.join(identifierArr_local), list(dict.fromkeys(condition_identifier_arr))

def extract_req_json(xpathtext, inputjson):
    text = xpathtext
    xpathArr2 = text.split('/')
    ip_json = inputjson
    res = []
    res2 = {}
    latest_key = ""
    for x in xpathArr2:
        list_ind = x
        if isinstance(ip_json, dict):
            res = ip_json[list_ind]
            ip_json = ip_json[list_ind]
            latest_key = list_ind
        else:
            for a in ip_json:
                res.append(a[list_ind])
                ip_json = list(chain.from_iterable(res))
            latest_key = list_ind
        res3 = {x: res}
        res = []
        res2.update(res3)
    return res2[latest_key]

#search required values from extracted tables
def extract_table_value(search_row_name, search_column_name, table_df):
    search_value = search_row_name
    try:
        match = table_df.apply(lambda col: col == search_value).any()
        matched_columns = ''.join(match[match].index.tolist())
        
        row = table_df[table_df[matched_columns] == search_value]
        if search_column_name == "":
            req_val = row.values[0][1]
        else:
            req_val = row[search_column_name].values[0]

        return float(req_val)
    except :
        return ""
############# extract table and store in excel logic############
def extract_tables_from_pdf(input_pdf_name, output_excel_name):
    pdf_path = 'output.pdf'
    output_excel = 'Tables.xlsx'

    with pdfplumber.open(pdf_path) as pdf, pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            for table_index, table in enumerate(tables):
                if not table:
                    continue
                df = pd.DataFrame(table)

                sheet_name = f"page{page_num+1}_table{table_index+1}"

                sheet_name = sheet_name[:31]

                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
        print(f"All Tables saved to {output_excel}")
    return(output_excel)
############# extract table and store in excel logic############

#main funtion for calc engine
def calc_engine_validation(row, extracted_table_path):
    op_label = row['Ouput Label']
    op_language = row["Output Language"]
    ip_value = row["Input Value"]
    tables_df = pd.read_excel(extracted_table_path, sheet_name=None)
    with open(json_path, 'r') as f:
        ip_json_value = json.load(f)
    if ('∑') in op_language:
        formula_text = op_language.replace('∑', '').replace('<', '').replace('>', '')
    else:
        formula_text = ip_value.replace('∑', '').replace('<', '').replace('>', '')
    extract_req_json_data = extract_req_json("plan/eligibilityClass/planDesign", ip_json_value)
    flag = []
    flag_final = []
    extracted_table_values_arr = []
    calc_engine_result_values_arr = []
    for erjd in extract_req_json_data:
        formula_result, identify, condition_identify = formula_calculation(formula_text, erjd)
        before, sep, after = op_label.partition(":")
        
        for i, tdf in enumerate(tables_df):
            
            if(len(condition_identify) > 1):
                flag.append("SKIPPED")
                condition_identify = []
                flag_final.append({identify: "SKIPPED"})
                break

            extracted_table_result = extract_table_value(before, after, tables_df[tdf])
            
            if (formula_result == extracted_table_result):
                flag.append('PASS')
                flag_final.append({identify: "PASS"})
            elif ((formula_result != extracted_table_result) and (extracted_table_result != "")):
                flag.append('FAIL')
                flag_final.append({identify: "FAIL"})
            if (extracted_table_result != ""):
                extracted_table_values_arr.append(extracted_table_result)

        calc_engine_result_values_arr.append(formula_result)
    print("Extracted Table Value List: ", extracted_table_values_arr)
    print("Calc Engine Result Value List: ", calc_engine_result_values_arr)
    print("FLAG: ", {op_label: flag_final})
    if 'FAIL' in flag:
        flag = 'FAIL'
    elif (('PASS' in flag) and ('FAIL' not in flag)):
        flag = 'PASS'
    else:
        flag = 'SKIPPED'
    # flag = 'FAIL' if 'FAIL' in flag else 'PASS'
    return flag, flag_final