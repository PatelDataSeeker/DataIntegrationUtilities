"""
Extract element tree schema from an XML file (e.g. CCDA).
Outputs the hierarchy as JSON. Generic utility for any XML.
"""
import xml.etree.ElementTree as ET
from collections import defaultdict
import json


def extract_tree_schema(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    schema = defaultdict(dict)

    def recursive_extract(element, current_schema):
        for child in element:
            if child.tag not in current_schema:
                current_schema[child.tag] = {}
            recursive_extract(child, current_schema[child.tag])

    schema[root.tag] = {}
    recursive_extract(root, schema[root.tag])
    return schema


if __name__ == "__main__":
    import sys
    xml_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\DP-Temp\example.xml"
    tree_schema = extract_tree_schema(xml_path)
    print(json.dumps(tree_schema, indent=4))
