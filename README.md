SNOMED Hierarchy Builder
========================

Quick and dirty script to build a hierarchy of a SNOMED concept's leaf nodes.
Run `python3 build.py` and enter a desired SNOMED concept, or just press enter to use _254837009_, which is _Malignant tumor of breast_.

This script uses the SPARQL endpoint at http://schemes.caregraf.info/snomed/sparql to receive JSON results and recurses into result sets until no child nodes are found.
Hence the script may run for a while until anything is shown on console.

Customization
-------------

At the top of the script there is:

- `_prefix`: An increasing number of this character/string will be inserted to denote hierarchy
- `_format`: A format string with 3 placeholders for the prefix, snomed code and snomed label
