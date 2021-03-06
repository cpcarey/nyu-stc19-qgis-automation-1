"""
This PyQGIS script iterates through all layers with a name matching "_described"
and:
    (1) Zooms to and displays all non-path features
    (2) Prompts user to confirm deletion
    (3) Deletes non-path features upon confirmation

Selecting "No" will end the layer iteration loop.

WARNING: This modifies local shapefiles. Maintain a separate copy for
restoration.
"""

import re
from qgis.PyQt import QtGui

SUFFIX_CLEANED = '_cleaned'
SUFFIX_DESCRIBED = '_described'

def confirm_delete(layer):
    """Prompts the user to confirm if the displayed non-path features of the
    given layer should be deleted."""

    fids = [
        f.id()
        for f in layer.getFeatures()
        if not re.match('2020', f.attribute('Name'))
    ]
    layer.selectByIds(fids)

    box = QMessageBox()
    response = QMessageBox.question(box, '', 'Delete all non-path features?')

    if response == QMessageBox.Yes:
        layer.startEditing()
        layer.deleteFeatures(fids)
        layer.commitChanges()
        if not re.match(SUFFIX_CLEANED, layer.name()):
            layer.setName('{}{}'.format(layer.name(), SUFFIX_CLEANED))

        set_layer_visibility(layer, False)
        return True

    set_layer_visibility(layer, False)
    return False

def select_layer(layer):
    set_layer_visibility(layer, True)
    qgis.utils.iface.layerTreeView().setCurrentLayer(layer)
    zoom_to_layer(layer)

def set_layer_visibility(layer, visible):
    qgis.core.QgsProject.instance().layerTreeRoot().findLayer(layer).setItemVisibilityChecked(visible)

def zoom_to_layer(layer):
    fids = [f.id() for f in layer.getFeatures()]
    canvas = iface.mapCanvas()
    canvas.zoomToFeatureIds(layer, fids)

for layer in qgis.core.QgsProject.instance().mapLayers().values():
    # Prompt the user for non-path feature deletion if the layer has been marked
    # with an entered description and has not been marked as cleaned already.
    if re.search(SUFFIX_DESCRIBED, layer.name()) and not re.search(SUFFIX_CLEANED, layer.name()):
        select_layer(layer)
        # Exit the loop if a non-path feature deletion confirmation is rejected.
        if not confirm_delete(layer):
            break
