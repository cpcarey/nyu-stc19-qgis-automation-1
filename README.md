# nyu-stc19-qgis-automation-1
QGIS scripts for automating spatiotemporal COVID-19 data cleaning

## Running the Scripts ##

There are three QGIS Python scripts that should be executed through the Python Console (Plugins > Python Console): (1) `merge_paths.py`, (2) `prompt_description.py`, (3) `delete_extra_features.py`.

These can be run by opening the editor (Python Console > Show Editor), opening the three scripts (Python Console Editor > Open Script... ) and executing them as needed (Python Console Editor > Run Script).

These scripts are applied to .shp layers which are loaded into QGIS. Applying these scripts to batches of layers is recommended in the case of script failure. Loading an OpenStreetMap layer underneath the DETER .shp layers is also recommended in order to provide geographic context.


## Scripts ##

### Script Summaries ###

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

### Script Details ###

#### Script 1: Merging Paths ####

The `merge_paths.py` script iterates through all layers labelled with a specified prefix (e.g. 2020). For each layer, it identifies the vector features representing the trajectories and/or events associated with the record for that layer, and performs a spatial merge to combine them into a single vector feature.

This identification is performed automatically. Vector features are identified as path features if they are a multi-polygon consisting of a single polygon. This is based on the assumption that the remaining non-path features are text annotations which consist of multi-polygons containing more than one polygon.

After the spatial merge, the layer is marked as modified automatically by appending the suffix `_auto_merged` to its name. The script outputs the layers automatically merged and how many failed to merge (if any). The user can then perform the path feature merge operation manually and mark the layer as merged by appending the suffix `_merged` to its name.

The subsequent scripts will only process layers with the suffix `_merged` (this includes layers with the suffix `_auto_merged`. The `merge_paths.py` script will only process layers that do not have the suffix `_merged`, so it can be run as many times as needed without affecting merged layers.

#### Script 2: Entering Description ####

The `prompt_description.py` script iterates through all layers labelled with the suffix `_merged`. For each layer, the layer is displayed and the user is prompted to enter the text description for the shown layer into an input box. If the user clicks OK, the entered text will be set as the value for the description attribute of the merged path vector feature in the layer, and the layer will be marked by appending the suffix `_described` to its name. The script will then advance to the next eligible layer. If the user clicks Cancel, the layer is not modified and the script terminates. 

#### Script 3: Delete Extra Features ####

The `delete_extra_features.py` script iterates through all layers labelled with the suffix `_described`. For each layer, the layer is displayed and the non-path vector features are selected and highlighted. The user is prompted to confirm the deletion of these selected features. If the user clicks OK, the selected non-path vector features are removed from the layer, and the layer is marked by appending the suffix `_cleaned` to its name. The script will then advance to the next eligible layer. If the user clicks Cancel, the layer is not modified and the script terminates.
