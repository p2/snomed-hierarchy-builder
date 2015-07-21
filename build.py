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

class Concept(object):
	def __init__(self, sct, label):
		self.snomed = sct
		self.label = label
		self.children = []
	
	def render(self, level=0):
		prefix = ''.join([_prefix for r in range(0, level)])
		
		line = _format.format(prefix, self.snomed, self.label)
		print(line)
		for child in self.children:
			child.render(level+1)


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

def build_tree(base_sct):
	tree = None
	root = load_tree(base_sct)
	results = find_results(root)
	if results is not None:
		leaves = []
		for result in results:
			snomed, uri, lbl, has_more = handle_result(result)
			
			# has child nodes, recurse
			if has_more and snomed is not None:
				leaves.append(build_tree(snomed))
			
			# no children, is either final leave or the root concept
			else:
				cpt = Concept(snomed or base_sct, lbl)
				if snomed is not None:
					leaves.append(cpt)
				else:
					assert tree is None
					tree = cpt
		tree.children = leaves
	return tree


if '__main__' == __name__:
	start_sct = input("Enter root SNOMED concept [254837009]: ")
	if start_sct is None or 0 == len(start_sct):
		start_sct = '254837009'
	
	print("Fetching SNOMED hierarchy for {}...".format(start_sct))
	tree = build_tree(start_sct)
	tree.render(level=2)
