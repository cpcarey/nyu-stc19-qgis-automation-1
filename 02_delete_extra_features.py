"""
02_delete_extra_features.py

This PyQGIS script will attempt to perform the following operation on shapefile
layers matching user-specified criteria:
    (1) Zoom to and display all non-path features
    (2) Prompt user to confirm deletion
    (3) Delete non-path features upon confirmation

Selecting "No" will end the layer iteration loop.

WARNING: This modifies local shapefiles in-place. Maintain a separate copy for
restoration.
"""

import re
from qgis.PyQt import QtGui

# Set this value to the prefix of the names of the layers to process.
LAYER_PREFIX_TO_MATCH = '2020'

# Set this value to any substring within the names of the layers to process,
# e.g. initials "IS" to process a single collector's layers.
LAYER_SUBSTRING_TO_MATCH = ''

# Set this value to the suffix of the names of the layers to process.
SUFFIX_CLEANABLE = '_merged'

# Set this value to the suffix to attach to names of processed layers to mark
# them as processed.
SUFFIX_CLEANED = '_cleaned'

def confirm_delete(layer):
    """Prompts the user to confirm if the displayed non-path features of the
    given layer should be deleted."""

    fids = [
        f.id()
        for f in layer.getFeatures()
        if not re.match('2020', f.attribute('Name'))
    ]
    layer.selectByIds(fids)

    description = ''
    for f in layer.getFeatures():
        if re.match('2020', f.attribute('Name')):
            description = f.attribute('descriptio')

    if not description:
        description = ''
    box = QMessageBox()
    response = QMessageBox.question(
            box, 'Delete all non-path features?', description)

    if response == QMessageBox.Yes:
        layer.startEditing()
        layer.deleteFeatures(fids)
        layer.commitChanges()
        if not re.match(SUFFIX_CLEANED, layer.name()):
            layer.setName(f'{layer.name()}{SUFFIX_CLEANED}')

        set_layer_visibility(layer, False)
        return True

    set_layer_visibility(layer, False)
    return False

def is_matching_layer(layer):
    """Returns true if the name of the given layer meets the criteria for
    processing."""
    return (
        re.match(LAYER_PREFIX_TO_MATCH, layer.name()) and
        re.match(f'.*{LAYER_SUBSTRING_TO_MATCH}.*', layer.name()) and
        re.search(SUFFIX_CLEANABLE, layer.name()) and
        not re.search(SUFFIX_CLEANED, layer.name()))

def select_layer(layer):
    set_layer_visibility(layer, True)
    qgis.utils.iface.layerTreeView().setCurrentLayer(layer)
    zoom_to_layer(layer)

def set_layer_visibility(layer, visible):
    qgis.core.QgsProject.instance().layerTreeRoot(
            ).findLayer(layer).setItemVisibilityChecked(visible)

def zoom_to_layer(layer):
    fids = [f.id() for f in layer.getFeatures()]
    canvas = iface.mapCanvas()
    canvas.zoomToFeatureIds(layer, fids)

for layer in qgis.core.QgsProject.instance().mapLayers().values():
    # Prompt the user for non-path feature deletion if the layer has been marked
    # with an entered description and has not been marked as cleaned already.
    if is_matching_layer(layer):
        select_layer(layer)
        # Exit the loop if a non-path feature deletion confirmation is rejected.
        if not confirm_delete(layer):
            break
