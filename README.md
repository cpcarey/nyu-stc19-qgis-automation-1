# nyu-stc19-qgis-automation-1
QGIS scripts for automating spatiotemporal COVID-19 data cleaning

Script 1: `merge_paths.py`

This script takes all layers prefixed with "2020" and attempts to merge path
features. It will mark layers successfully merged with the suffix
`_auto_merged`.

Script 2: `prompt_description.py`

This script takes all layers marked with `_merged` in the name and will iterate
through displaying the features and prompting the user to enter the description
displayed. It will mark layers successfully modified with the suffix
`_described`.

Script 3: `delete_extra_features.py`

This script takes all layers marked with `_described` in the name and will
iterate through  and display and highlight the non-path features and prompt
the user to confirm the deletion of these non-path features. It will mark layers
successfully modified with the suffix `_cleaned`.
