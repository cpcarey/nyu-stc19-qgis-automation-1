"""
01_merge_paths.py

This PyQGIS script will attempt to perform the following operation on shapefile
layers matching user-specified criteria:
    (1) Merge all likely path polygon features within a single multi-polygon
    (2) Commit marked changes
    (3) Output successes and failures

Prerequisites:
    - Requires the layers in shapefile format
    - Requires the layers to be added (but not required to be selected)

How path-features are detected:

The script operates by assuming that path features are multi-polygons containing
a small number of polygons (controlled by MAX_POLYGONS_IN_PATH_FEATURE_POLYGON).
This is because non-path features are almost always multi-polygons representing
text with an individual polygon for each character. Put another way, path
features are groups of few polygons and non-path features are groups of lots of
polygons. This assumption may not hold if for layers with minimal text
displayed. The most common number of polygons in a path feature is a
multi-polygon; each trajectory line is typically a single polygon within a
multi-polygon even if when there are multi-polygons.

It is uncommon for path feature multi-polygons to contain two polygons and
rare to contain three or four. If this is the case, there usually is another
single polygon multi-polygon path feature with an identical timestamp. Timestamp
matching is used to improve the likelihood of identifying a multiple polygon
multi-polygon as a path feature correctly (instead of as text).

For multiple polygon multi-polygon path features without other
path features to check the timestamp for, the script will mark the layers as
failed with zero identified path features. The user will then need to maark
this multi-polygon as the path feature manually.

Difference from previous merge_paths.py.

The previous merge_path.py script combined path feature polygons into a
single polygon multi-polygon by taking the spatial union of the polygons. This
script merges path feature polygons into a multiple polygon multi-polygon
without combining polygons into a single polygon.

WARNING: This modifies local shapefiles in-place. Maintain a separate copy for
restoration.
"""

import re
layer = qgis.utils.iface.activeLayer()

# Set this value to the prefix of the names of the layers to process.
LAYER_PREFIX_TO_MATCH = '2020'

# Set this value to any substring within the names of the layers to process,
# e.g. initials "IS" to process a single collector's layers.
LAYER_SUBSTRING_TO_MATCH = ''

# The maximum number of polygons within a multi-polygon to be considered a
# 
MAXIMUM_POLYGONS_IN_PATH_FEATURE_POLYGON = 4

def get_multiple_polygons_as_multi_polygon(polygons):
    """Returns the given polygons as a multi-polygon."""
    wkts = [p.asWkt().replace('PolygonZ ', '') for p in polygons]
    wkt = f'MultiPolygonZ ({",".join(wkts)})'
    return QgsGeometry.fromWkt(wkt)

def get_as_polygons(multi_polygon):
    """Returns polygons within the given multi-polygon."""
    wkt = multi_polygon.asWkt()

    # Remove MultiPolygonZ.
    wkt = re.sub('MultiPolygonZ \(', '', wkt)[0:-1]
    # Remove beginning and ending parentheses.
    wkt = wkt[2:-2]

    # Divide into individual polygons.
    polygon_wkts = wkt.split(')),((')
    # Put back into wkt form.
    polygon_wkts = [f'PolygonZ (({pw}))' for pw in polygon_wkts]
    # Convert wkt form to Polygon geometries.
    polygons = [QgsGeometry.fromWkt(pw) for pw in polygon_wkts]
    return polygons

def merge_path_in_layer(layer):
    """Attempts to find the polygons in the given layer that represent a path
    which should be merged into a single multi-polygon. Returns whether path
    features were merged."""

    # Most path features consist of a single polygon. Use this to identify
    # likely path features.
    features = [f for f in layer.getFeatures()]
    path_features = [
            f for f in features if len(f.geometry().asMultiPolygon()) == 1]
    path_feature_set = set(path_features)

    # Other path features might exist with two or three polygons, but they'll
    # also have an identical timestamp to the single polygon path feature.
    path_feature_timestamps = set(
            [f.attribute('timestamp') for f in path_features])
    print([t for t in path_feature_timestamps])
    for f in features:
        if f not in path_feature_set:
            count = len(f.geometry().asMultiPolygon())
            if (count > 0 and count < 4 and
                    f.attribute('timestamp') in path_feature_timestamps):
                path_features.append(f)

    # Skip this layer if there aren't enough identified path features to merge.
    if len(path_features) < 1:
        print(f'    Failed to edit: contained {len(path_features)} features')
        return False

    # Collect all multi-polygons as polygons so that overlapping polygons can
    # be merged.
    geometries = [f.geometry() for f in path_features]
    polygon_lists = [get_as_polygons(g) for g in geometries]
    # Flatten list of polygon lists into polygons.
    polygons = [p for pl in polygon_lists for p in pl]

    multi_polygon_merged = get_multiple_polygons_as_multi_polygon(polygons)

    # Replace first path feature with the merged geometry and set the name.
    path_feature = qgis.core.QgsFeature(path_features[0])
    path_feature.setGeometry(multi_polygon_merged)
    path_feature.setAttribute(0, layer.name())

    # Commit changes to the layer and shapefile. Delete other path features.
    layer.startEditing()
    layer.updateFeature(path_feature)
    for path_feature in path_features[1:]:
        layer.deleteFeature(path_feature.id())
    layer.setName(f'{layer.name()}_auto_merged')
    layer.commitChanges()

    # Display number of polygons merged to user for debugging purposes.
    print(f'    Found {len(features)} features')
    print(f'    Found {len(path_features)} path multi-polygons')
    print(f'    Merged {len(polygons)} path polygons')
    return True

success_count = 0
fail_count = 0

# Attempt to find and merge path features in all relevant layers. Mark and
# output the number of successful and failed merges.
for layer in qgis.core.QgsProject.instance().mapLayers().values():
    if (re.match(LAYER_PREFIX_TO_MATCH, layer.name()) and
        re.match(f'.*{LAYER_SUBSTRING_TO_MATCH}.*', layer.name()) and
        not re.search('auto_merged', layer.name())):
        print(f'Editing layer: {layer.name()}')
        if merge_path_in_layer(layer):
            success_count += 1
        else:
            fail_count += 1

print(f'{success_count} successfully converted')
print(f'{fail_count} failed to convert')
