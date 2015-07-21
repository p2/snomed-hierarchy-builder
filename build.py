#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

_prefix = '-'
_format = '{}>  {}: {}'		# 3 placeholders: _prefix, snomed, label

_url = "http://schemes.caregraf.info/snomed/sparql"
_query = """
PREFIX cgkos: <http://datasets.caregraf.org/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT
	?s ?skos_prefLabel ?cgkos_numberSubordinates ?cgkos_isPrimitive
WHERE {{
	{{?s skos:prefLabel ?skos_prefLabel ; skos:broader <http://datasets.caregraf.org/snomed/{}> .
		OPTIONAL {{?s cgkos:numberSubordinates ?cgkos_numberSubordinates}} .
		OPTIONAL {{?s cgkos:isPrimitive ?cgkos_isPrimitive}}
	}}
	UNION {{
		<http://datasets.caregraf.org/snomed/{}> skos:prefLabel ?skos_prefLabel .
		OPTIONAL {{
			<http://datasets.caregraf.org/snomed/{}> cgkos:numberSubordinates ?cgkos_numberSubordinates
		}}
	}}
}}
ORDER BY ?skos_prefLabel
LIMIT 100
"""

def load_tree(base_sct):
	qry = _query.format(base_sct, base_sct, base_sct)
	
	ret = requests.get(_url, params={'query': qry.strip()}, headers={'Accept': 'application/json'})
	ret.raise_for_status()
	return ret.json()

def find_results(root):
	return root.get('results', {}).get('bindings')

def handle_result(result):
	uri = result.get('s', {}).get('value')
	parts = uri.split('/') if uri is not None else None
	snomed = parts[-1] if parts is not None else None
	lbl = result.get('skos_prefLabel', {}).get('value')
	has_more = int(result.get('cgkos_numberSubordinates', {}).get('value', 0)) > 0
	return snomed, uri, lbl, has_more

def build_tree(base_sct, indent=0):
	lines = []
	tree = load_tree(base_sct)
	results = find_results(tree)
	if results is not None:
		prefix = ''.join([_prefix for r in range(0, indent)])
		for result in results:
			snomed, uri, lbl, has_more = handle_result(result)
			if has_more and snomed is not None:
				lines.extend(build_tree(snomed, indent+1))
			
			# format and instert the line
			line = _format.format(prefix, snomed or base_sct, lbl)
			if snomed is not None:
				lines.append(_prefix+line)
			else:
				lines.insert(0, line)
	return lines


if '__main__' == __name__:
	start_sct = input("Enter root SNOMED concept [254837009]: ")
	if start_sct is None or 0 == len(start_sct):
		start_sct = '254837009'
	
	print("Fetching SNOMED hierarchy for {}...".format(start_sct))
	lines = build_tree(start_sct, indent=2)
	print("\n".join(lines))

