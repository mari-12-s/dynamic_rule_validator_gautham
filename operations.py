from anyTree import Node, RenderTree, PreOrderIter
import pandas as pd
import re
import pdfplumber

#convert JSON to anytree
def json_to_anytree(data, parent=None, name="root"):
    name = name.lower()
    if isinstance(data, dict):
        node = Node(name, parent=parent)
        for k, v in data.items():
            json_to_anytree(v, node, k)
    elif isinstance(data, list):
        node = Node(name, parent=parent)
        for i, item in enumerate(data):
            json_to_anytree(item, node, f"{name}[{i}]")
    else:
        node = Node(f"{name}: {data}", parent=parent)
    return node

#find values in tree
def find_values_by_key(root, key, parent_key):
    key = re.sub(r"[ <>]", '', key)
    matches = []
    for node in PreOrderIter(root):
        if ":" in node.name:
            node_key, node_value = node.name.split(": ", 1)
            if node_key.strip().lower() == key.lower():
                if parent_key is None:
                    matches.append(node_value)
                else:
                    if '/' in parent_key:
                        gp_name, parent_name = parent_key.split('/')
                        if parent_name.lower() in node.parent.name and gp_name.lower() in node.parent.parent.name:
                            matches.append(node_value)
                    else:
                        if parent_key.lower() in node.parent.name:
                            matches.append(node_value)
    return matches

def extract_table_from_pdf(op_label, ip_pdf, search_header):
    extracted_tables = []
    with pdfplumber.open(ip_pdf) as pdf:
        first_page = None
        last_page = None
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if search_header in text:
                if first_page is None:
                    first_page = page_num
                last_page = page_num
            else:
                continue
            if first_page is None:
                return None, None, [] #Text not found
        print(f"first page and last page for searched document: {first_page} and {last_page}")
        for i in range(first_page, last_page):
            page = pdf.pages[i]
            text = page.extract_text()
            if op_label in text:
                tables_loc = page.extract_tables
                for table_index, table_loc in enumerate(tables_loc):
                    t = pd.DataFrame(tables_loc)
                    extracted_tables.append(t)
    return extracted_tables

def extract_req_value_from_tables(search_row_name, search_column_name, ext_tables):
    print(f"search_row_name: {search_row_name} and search_column_name: {search_column_name}")
    results = []
    for i, ext_table in enumerate(ext_tables):
        if (ext_table.asType(str).apply(lambda x: x.str.contains(search_row_name, case=False, na=False)).any().any()):
            if not search_column_name:
                row_matches = (ext_table == search_row_name)
                if row_matches.any().any():
                    res = row_matches.stack()
                    locat = res[res].index.tolist()
                    row_index, _ = locat[0]
                    results.append(ext_table.iloc[row_index, 1])
            else:
                row_matches = (ext_table == search_row_name)
                col_matches = (ext_table == search_column_name)
                row_index, col_index = "", ""
                if row_matches.any().any():
                    res = row_matches.stack()
                    locat = res[res].index.tolist()
                    row_index, _ = locat[0]
                if col_matches.any().any():
                    res = col_matches.stack()
                    locat = res[res].index.tolist()
                    _, col_index = locat[0]
                if row_index and col_index:
                    results.append(ext_table.iloc[row_index, col_index])
    return results

#filter or find first sub tree
def filter_subtree_to_next_root_child(root_node, key, value):
    target_key = key.lower()
    target_value = value.lower()
    for node in PreOrderIter(root_node):
        if":" in node.name:
            node_key, node_val = node.name.split(": ", 1)
            if node_key.lower() == target_key and node_val.lower == target_value:
                path = node.path
                if len(path) > 2:
                    return path[4] #as per current JSON structure
                else:
                    return root_node
                
def filter_subtree_by_key_value(root, key, value):
    target_key = key.lower()
    if value is None:
        found_subtrees = []
        for node in PreOrderIter(root):
            if target_key in node.name:
                found_subtrees.append(node.parent)
            else:
                continue
        return found_subtrees
    else:
        target_value = value.lower()
        for node in PreOrderIter(root):
            if ":" in node.name:
                node_key, node_val = node.name.split(": ", 1)
                if value is not None:
                    if node_key.lower() == target_key and node_val.lower() == target_value:
                        return node.parent
                    else:
                        continue