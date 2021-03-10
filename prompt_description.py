"""
This PyQGIS script will iterate through all layers matching the name
"auto_merged" and:
    (1) Zoom to and display this layer
    (2) Prompt the user to type in the text description
    (3) Add the description to the existing path feature attribute
    (4) Mark the layer as "described"

Hitting cancel will exit the loop.

WARNING: This script modifies the original shapefiles. Maintain a separate copy
for restoration.
"""

import re
from qgis.PyQt import QtGui

ATTR_NAME = 'Name'
ATTR_DESCRIPTION = 'descriptio'
FIELD_INDEX_DESCRIPTION = 1
MERGED_FEATURE_NAME_PREFIX = '2020'

def change_description(layer, feature):
    """Prompts the user to input the description for the given path feature and
    layer. Persists given description if confirmed."""

    name = feature.attribute(ATTR_NAME)
    description = str(feature.attribute(ATTR_DESCRIPTION))
    dialog_title = 'Description for {}:'.format(name)

    dialog = QInputDialog()
    new_description, confirmed = QInputDialog.getText(
        dialog, dialog_title, 'Description: ', QLineEdit.Normal, description)

    if confirmed:
        feature.setAttribute(FIELD_INDEX_DESCRIPTION, new_description)
        layer.startEditing()
        layer.updateFeature(feature)
        if not re.match('_described', layer.name()):
            layer.setName('{}_described'.format(layer.name()))
        layer.commitChanges()
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

exit = False
for layer in qgis.core.QgsProject.instance().mapLayers().values():
    # Only prompts for layers matching the _merged name. Remove this
    # requirement if the layers have already been merged and contain a single
    # path feature with the name prefix "2020".
    if re.search('_merged', layer.name()) and not re.search('_described', layer.name()) and not exit:
        for feature in layer.getFeatures():
            name = feature.attribute(ATTR_NAME)
            if re.match(MERGED_FEATURE_NAME_PREFIX, name):
                select_layer(layer)
                if not change_description(layer, feature):
                    exit = True
                    break
