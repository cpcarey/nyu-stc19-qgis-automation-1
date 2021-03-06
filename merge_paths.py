import re
layer = qgis.utils.iface.activeLayer()

"""
This PyQGIS script will attempt to:
    (1) Merge all likely path features in all loaded COVID-19 data layers
    (2) Commit marked changes
    (3) Output successes and failures

WARNING: This may incorrectly identify and merge path features. Maintain
a copy of the original COVID-19 shapefiles for restoration.
"""

def collect_vertices(geometry):
    """Returns all vertices within the given geometry as a list."""
    vertices = []
    vertices_iter = geometry.vertices()
    while vertices_iter.hasNext():
        vertices.append(vertices_iter.next())
    return vertices

def get_as_multi_polygon(polygon):
    """Returns the given polygon as a multi-polygon."""
    wkt = polygon.asWkt()
    wkt = re.sub('PolygonZ ', 'MultiPolygonZ (', wkt) + ')'
    return QgsGeometry.fromWkt(wkt)

def get_as_polygon(multi_polygon):
    """Returns the given multi-polygon as a polygon. The given multi-polygon
    must only contain a single polygon."""
    wkt = multi_polygon.asWkt()
    wkt = re.sub('MultiPolygonZ \(', 'PolygonZ ', wkt)[0:-1]
    return QgsGeometry.fromWkt(wkt)

def merge_path_in_layer(layer):
    """Attempts to find the geometries in the given layer that represent a path
    which should be merged. Returns whether path features were merged."""

    # Most path features consist of a single polygon. Use this to identify
    # likely path features.
    path_features = [f for f in layer.getFeatures() if len(f.geometry().asMultiPolygon()) == 1]

    # Skip this layer if there aren't enough identified path features to merge.
    if len(path_features) < 2:
        print('    Failed to edit: contained {} features'.format(len(path_features)))
        return False

    # Collect all multi-polygons as polygons so that they can merged.
    geometries = [f.geometry() for f in path_features]
    polygons = [get_as_polygon(g) for g in geometries]

    # Merge all of the polygons and convert back into a multi-polygon.
    polygon_combined = polygons[0]
    index = 1
    while index < len(polygons):
        polygon_combined = polygon_combined.combine(polygons[index])
        index += 1
    multi_polygon_combined = get_as_multi_polygon(polygon_combined)

    # Count the vertices in order to display information to user later.
    vertices_lists = [collect_vertices(g) for g in geometries]
    vertices_combined = collect_vertices(multi_polygon_combined)

    # Replace first path feature with the merged geometry and set the name.
    path_feature = qgis.core.QgsFeature(path_features[0])
    path_feature.setGeometry(multi_polygon_combined)
    path_feature.setAttribute(0, layer.name())

    # Commit changes to the layer and shapefile. Delete other path features.
    layer.startEditing()
    layer.updateFeature(path_feature)
    for path_feature in path_features[1:]:
        layer.deleteFeature(path_feature.id())
    layer.setName('{}_auto_merged'.format(layer.name()))
    layer.commitChanges()

    # Display number of vertices merged to user for debugging purposes.
    s = '    Combined {}'.format(len(vertices_lists[0]))
    index = 1
    while index < len(vertices_lists):
        s += ', {}'.format(len(vertices_lists[index]))
        index += 1
    s += ' to {} vertices'.format(len(vertices_combined))
    print(s)
    return True

success_count = 0
fail_count = 0

# Attempt to find and merge path features in all relevant layers. Mark and
# output the number of successful and failed merges.
for layer in qgis.core.QgsProject.instance().mapLayers().values():
    if re.match('2020', layer.name()) and not re.search('auto_merged', layer.name()):
        print('Editing layer: {}'.format(layer.name()))
        if merge_path_in_layer(layer):
            success_count += 1
        else:
            fail_count += 1

print('{} successfully converted'.format(success_count))
print('{} failed to convert'.format(fail_count))
