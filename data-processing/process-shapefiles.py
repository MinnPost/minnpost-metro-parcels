"""
Process shapefiles.
"""


import logging, os, sys, argparse
import progressbar
from osgeo import ogr, osr


class MetroParcels():
  """
  Class to handle execution
  """

  description = """
  Processes and combines shapefiles.
"""

  script_path = os.path.dirname(os.path.realpath(__file__))
  source_shape_hennepin = os.path.join(script_path, '../data/reprojected_4326-shps/hennepin-parcels.shp')
  source_shape_anoka = os.path.join(script_path, '../data/reprojected_4326-shps/anoka-parcels.shp')
  source_shape_dakota = os.path.join(script_path, '../data/reprojected_4326-shps/dakota-parcels.shp')
  source_shape_combined = os.path.join(script_path, '../data/combined-shp/metro-combined.shp')


  def __init__(self):
    """
    Constructor.
    """
    self.driver = ogr.GetDriverByName('ESRI Shapefile')

    # Read files
    self.shape_hennepin = self.driver.Open(self.source_shape_hennepin, 0)
    self.shape_anoka = self.driver.Open(self.source_shape_anoka, 0)
    if self.shape_hennepin is None or self.shape_anoka is None:
      self.error('Could not find a necessary shapefile')
      sys.exit(1)

    # Get actual layers
    self.hennepin = self.shape_hennepin.GetLayer()
    self.anoka = self.shape_anoka.GetLayer()

    # Get layer definitions
    self.hennepin_definition = self.hennepin.GetLayerDefn()
    self.anoka_definition = self.anoka.GetLayerDefn()

    # Create layer to write to, remove if already there
    if not os.path.exists(os.path.dirname(self.source_shape_combined)):
      os.makedirs(os.path.dirname(self.source_shape_combined))
    if os.path.exists(self.source_shape_combined):
      self.driver.DeleteDataSource(self.source_shape_combined)

    self.shape_combined = self.driver.CreateDataSource(self.source_shape_combined)
    self.combined = self.shape_combined.CreateLayer('metro_parcels', geom_type = ogr.wkbPolygon)

    # Start pocessing
    self.process()


  def close(self):
    """
    Close out data sources
    """
    self.shape_hennepin.Destroy()
    self.shape_anoka.Destroy()
    self.shape_combined.Destroy()


  def out(self, message):
    """
    Wrapper around stdout
    """
    sys.stdout.write(message)


  def error(self, message):
    """
    Wrapper around stderror
    """
    sys.stderr.write(message)


  def get_counts(self):
    """
    Get feature count.
    """
    self.hennepin_count = self.hennepin.GetFeatureCount()
    self.out('- Found %s features in %s.\n' % (self.hennepin_count, 'Hennepin'))
    self.anoka_count = self.anoka.GetFeatureCount()
    self.out('- Found %s features in %s.\n' % (self.anoka_count, 'Anoka'))


  def define_combined(self):
    """
    Adds field definitions to shapes.  We know Anoka has the fields we want.
    http://www.datafinder.org/metadata/ParcelsCurrent.html#Entity_and_Attribute_Information
    """
    self.out('- Setting up fields for combined layer.\n')
    for i in range(0, self.anoka_definition.GetFieldCount()):
      field = self.anoka_definition.GetFieldDefn(i)
      self.combined.CreateField(field)

    self.combined_definition = self.combined.GetLayerDefn()


  def anoka_translation(self, old, new):
    """
    Translation layer for each feature for Anoka.
    """
    # Figure out number of fields
    field_count = self.combined_definition.GetFieldCount()

    # Add field values from input Layer
    for i in range(0, field_count):
      new.SetField(self.combined_definition.GetFieldDefn(i).GetNameRef(), old.GetField(i))

    return new


  def combine(self, layer_name):
    """
    Combine layer.
    """
    layer_ = getattr(self, layer_name)
    layer_count = getattr(self, '%s_count' % (layer_name))
    layer_translation = getattr(self, '%s_translation' % (layer_name))

    # Progress bar
    widgets = ['- Combining %s: ' % (layer_name), progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    progress = progressbar.ProgressBar(widgets = widgets, maxval = layer_count).start()
    completed = 0

    # Add features to the ouput Layer
    for i in range(0, layer_count):
      existing_feature = layer_.GetFeature(i)
      combined_feature = ogr.Feature(self.combined_definition)

      # Translate
      combined_feature = layer_translation(existing_feature, combined_feature)

      # Set geometry
      combined_feature.SetGeometry(existing_feature.GetGeometryRef())

      # Add new feature to output Layer
      self.combined.CreateFeature(combined_feature)

      # Update progress
      completed = completed + 1
      progress.update(completed)

    # Stop progress bar
    progress.finish()


  def make_spatial_reference(self):
    """
    Export out the spatial reference file.
    """
    self.out('- Making spatial reference.\n')
    self.spatial_reference = osr.SpatialReference()
    self.spatial_reference.ImportFromEPSG(4326)
    self.spatial_reference.MorphToESRI()
    file = open(self.source_shape_combined.replace('.shp', '.prj'), 'w')
    file.write(self.spatial_reference.ExportToWkt())
    file.close()


  def process(self):
    """
    Main execution handler.
    """
    self.argparser = argparse.ArgumentParser(description = self.description, formatter_class = argparse.RawDescriptionHelpFormatter,)

    # Parse options
    self.args = self.argparser.parse_args()

    # Figure out totals
    self.get_counts()

    # Set up shape to write to
    self.define_combined()

    # Add anoka
    self.combine('anoka')

    # Spatial reference stuff
    self.make_spatial_reference()

    # Close out thing
    self.close()


# Handle execution
if __name__ == '__main__':
  mp = MetroParcels()
