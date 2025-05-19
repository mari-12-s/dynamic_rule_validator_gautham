import operations as op
import re
from anytree import Node, RenderTree
import pandas as pd

def contains_arithmetic_operator(s):
    operators = ['+', '-', '*', '/', '∑']
    return any(operator in s for operator in operators)

def extract_unique_placeholders(template):
    seen = set()
    placeholders = []
    for match in re.findall(r"<[^>]+>", template):
        if match not in seen:
            placeholders.append(match)
            seen.add(match)
    return placeholders

def replace_with_unique_mapping(template, values):
    keys = extract_unique_placeholders(template)
    value_queue = list(values) if isinstance(values, str) else values
    mapping = {
        key: value_queue.pop(0) if value_queue else key
        for key in keys
    }
    return re.sub(r"<[^>]+>", lambda match: mapping[match.group(0)], template)

def normalize_text(text):
    clean_text = text.lower().replace(' ', '')
    return clean_text

def table_validator(row, json_data, tables_df):
    root = op.json_to_anytree(json_data)
    input_value = normalize_text(row["Input Value"])
    output_label = row["Output Label"]
    output_language = normalize_text(row["Output Language"])

    if pd.isna(row["Criteria"]) or str(row["Criteria"]).strip() == '':
        criteria = None
    else:
        criteria = normalize_text(row["Criteria"])

    rule_id = row["Rule No"]
    filter_string, immediate_root, xml_key_name = None, None, None
    filter_key_string, filter_value_string = None, None
    expected_values, expected_values_keys = None, None

    if criteria:
        filter_string, immediate_root, xml_key_name = criteria.split('|')
        if filter_string:
            filter_key_string, filter_value_string = filter_string.split('=')
        else:
            filter_key_string, filter_value_string = "", ""
        expected_values_keys = re.findall(r"<(.*?)>", xml_key_name) if xml_key_name else output_language
        expected_values = replace_with_unique_mapping(output_language, expected_values_keys) if expected_values_keys else output_language
    else:
        expected_values = output_language

    filtered_subtree = op.filter_subtree_to_next_root_child(root, "planName", "AIPlan1")
    before, _, after = output_label.partition(':')
    extracted_table_result = op.extract_req_value_from_tables(before, after, tables_df)

    if not contains_arithmetic_operator(output_language):
        expected_values = re.findall(r"<(.*?)>", xml_key_name) if xml_key_name else output_language
        if filter_key_string:
            fil_sub_tree = op.filter_subtree_by_key_value(filtered_subtree, filter_key_string, filter_value_string)
            final_tree_val = op.find_values_by_key(fil_sub_tree, ''.join(expected_values), immediate_root)
            final_tree_val = [str(list(set(final_tree_val)))]
        else:
            final_tree_val = op.find_values_by_key(filtered_subtree, ''.join(expected_values), immediate_root)
            final_tree_val = [str(list(set(final_tree_val)))]

    elif contains_arithmetic_operator(output_language):
        if filter_key_string:
            fil_sub_tree = op.filter_subtree_by_key_value(filtered_subtree, filter_key_string, filter_value_string)
            final_tree_val = op.find_values_by_key(fil_sub_tree, ''.join(expected_values).replace('∑', ''), immediate_root)
            final_tree_val = list(set(final_tree_val))
        else:
            final_tree_val = op.find_values_by_key(filtered_subtree, ''.join(expected_values),.replace('∑', ''), immediate_root)
            final_tree_val = list(set(final_tree_val))
            xml_keys, xml_parent = re.findall(r"<(.*?)>", criteria, criteria.split('|')[1])
            req_val_res_cal = {}
            for xml_key in xml_keys:
                req_val_res_cal.update({xml_key: sum(float(x) for x in op.find_values_by_key(filtered_subtree, xml_key, xml_parent) if x.strip() != '')})
            final_tree_val = eval(expected_values.replace('∑', ''), {}, req_val_res_cal)
            final_tree_val = [str(final_tree_val*100)] if '%' in output_label else [str(final_tree_val)]
    extracted_table_result = re.sub(r'[^a-zA-Z0-9.\-]', '', ''.join(extracted_table_result))
    final_tree_val = re.sub(r'[^a-zA-Z0-9.\]', '', ''.join(final_tree_val))
    try:
        extracted_table_result = round(float(extracted_table_result), 0)
        final_tree_val = round(float(final_tree_val), 0)
    except:
        print("value is string")
    if extracted_table_result == final_tree_val:
        print(f"{rule_id}: PASS")
        return "PASS"
    else:
        print(f"{rule_id}: FAIL")
        return "FAIL"