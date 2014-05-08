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
    self.in_driver = ogr.GetDriverByName('ESRI Shapefile')
    self.out_driver = ogr.GetDriverByName('ESRI Shapefile')

    # Read files
    self.shape_hennepin = self.in_driver.Open(self.source_shape_hennepin, 0)
    self.shape_anoka = self.in_driver.Open(self.source_shape_anoka, 0)
    if self.shape_hennepin is None or self.shape_anoka is None:
      self.error('Could not find a necessary shapefile')
      sys.exit(1)

    # Get actual layers
    self.hennepin = self.shape_hennepin.GetLayer()
    self.anoka = self.shape_anoka.GetLayer()

    # Get layer definitions
    self.hennepin_definition = self.hennepin.GetLayerDefn()
    self.anoka_definition = self.anoka.GetLayerDefn()

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


  def parse_int(self, s):
    """
    Parse integer.
    """
    try:
      return int(s) if s is not None else None
    except ValueError:
      return None


  def get_counts(self):
    """
    Get feature count.
    """
    self.hennepin_count = self.hennepin.GetFeatureCount()
    self.anoka_count = self.anoka.GetFeatureCount()


  def define_combined(self):
    """
    Adds field definitions to shapes.  We know Anoka has the fields we want.
    http://www.datafinder.org/metadata/ParcelsCurrent.html#Entity_and_Attribute_Information
    """
    self.out('- Creating combined layer.\n')

    # Create layer to write to, remove if already there
    if not os.path.exists(os.path.dirname(self.source_shape_combined)):
      os.makedirs(os.path.dirname(self.source_shape_combined))
    if os.path.exists(self.source_shape_combined):
      self.out_driver.DeleteDataSource(self.source_shape_combined)

    self.shape_combined = self.out_driver.CreateDataSource(self.source_shape_combined)
    self.combined = self.shape_combined.CreateLayer('metro_parcels', geom_type = ogr.wkbPolygon)

    # Create field definition from anoka
    for i in range(0, self.anoka_definition.GetFieldCount()):
      field = self.anoka_definition.GetFieldDefn(i)
      self.combined.CreateField(field)

    self.combined_definition = self.combined.GetLayerDefn()


  def hennepin_translation(self, old, new):
    """
    Translation layer for each feature for Hennepin.  We have to basically
    manually translate.

    http://www.hennepin.us/~/media/hennepinus/your-government/open-government/taxable-parcels.pdf
    """

    """
    (not used)
    PID_TEXT (String | 80 | 0)
    FEATURECOD (Real | 11 | 0)
    STATE_CD (Real | 11 | 0)
    TORRENS_TY (String | 80 | 0)
    CONDO_NO (String | 80 | 0)
    MUNIC_CD (String | 80 | 0)
    MULTI_ADDR (String | 80 | 0)
    MAILING_MU (String | 80 | 0)
    SEWER_DIST (String | 80 | 0)
    TIF_PROJEC (String | 80 | 0)
    PROPERTY_S (String | 80 | 0)
    FORFEIT_LA (String | 80 | 0)
    CO_OP_IND (String | 80 | 0)
    CONTIG_IND (String | 80 | 0)
    HMSTD_CD1 (String | 80 | 0)
    PROPERTY_1 (String | 80 | 0)
    PROPERTY_2 (String | 80 | 0)
    EST_LAND_1 (Real | 11 | 0)
    EST_BLDG_1 (Real | 11 | 0)
    PROPERTY_3 (String | 80 | 0)
    EST_LAND_2 (Real | 11 | 0)
    EST_BLDG_2 (Real | 11 | 0)
    PROPERTY_4 (String | 80 | 0)
    EST_LAND_3 (Real | 11 | 0)
    EST_BLDG_3 (Real | 11 | 0)
    ABBREV_ADD (String | 80 | 0)
    ADDITION_N (String | 80 | 0)
    METES_BNDS (String | 80 | 0)
    METES_BN_1 (String | 80 | 0)
    METES_BN_2 (String | 80 | 0)
    METES_BN_3 (String | 80 | 0)
    MORE_METES (String | 80 | 0)
    ABSTR_TORR (String | 80 | 0)
    SALE_CODE (String | 80 | 0)
    SALE_CODE_ (String | 80 | 0)
    Shape_Leng (Real | 24 | 15)
    """

    # If there is not a conversion below the field, it means there is not
    # an eqivalent in Hennepin

    # COUNTY_ID (String | 3 | 0)
    new.SetField('COUNTY_ID', '27')
    # PIN (String | 17 | 0)
    new.SetField('PIN', old.GetField('PID'))
    # BLDG_NUM (String | 10 | 0)
    new.SetField('BLDG_NUM', '%s%s' % (
      str(int(old.GetField('HOUSE_NO'))) if old.GetField('HOUSE_NO') is not None else '',
      ' ' + str(old.GetField('FRAC_HOUSE')) if old.GetField('FRAC_HOUSE') is not None else ''))
    # PREFIX_DIR (String | 2 | 0)
    # PREFIXTYPE (String | 6 | 0)
    # STREETNAME (String | 40 | 0)
    new.SetField('STREETNAME', old.GetField('STREET_NM'))
    # STREETTYPE (String | 4 | 0)
    # SUFFIX_DIR (String | 2 | 0)
    # UNIT_INFO (String | 12 | 0)
    # CITY (String | 30 | 0)
    new.SetField('CITY', old.GetField('MUNIC_NM'))
    # CITY_USPS (String | 30 | 0)
    new.SetField('CITY_USPS', old.GetField('MAILING__1'))
    # ZIP (String | 5 | 0)
    new.SetField('ZIP', old.GetField('ZIP_CD'))
    # ZIP4 (String | 4 | 0)
    # PLAT_NAME (String | 50 | 0)
    # BLOCK (String | 5 | 0)
    new.SetField('BLOCK', old.GetField('BLOCK'))
    # LOT (String | 5 | 0)
    new.SetField('LOT', old.GetField('LOT'))
    # ACRES_POLY (Real | 11 | 2) (convert from square meters to acres)
    new.SetField('ACRES_POLY', float(old.GetField('Shape_area')) * 0.000247105
      if old.GetField('Shape_area') is not None else None)
    # ACRES_DEED (Real | 11 | 2) (convert from square feet to acres)
    new.SetField('ACRES_DEED', float(old.GetField('PARCEL_ARE')) * 0.0000229568
      if old.GetField('PARCEL_ARE') is not None else None)
    # USE1_DESC (String | 100 | 0)
    new.SetField('USE1_DESC', old.GetField('PROPERTY_T'))
    # USE2_DESC (String | 100 | 0)
    # USE3_DESC (String | 100 | 0)
    # USE4_DESC (String | 100 | 0)
    # MULTI_USES (String | 1 | 0)
    # LANDMARK (String | 100 | 0)
    # OWNER_NAME (String | 50 | 0)
    new.SetField('OWNER_NAME', old.GetField('OWNER_NM'))
    # OWNER_MORE (String | 50 | 0)
    # OWN_ADD_L1 (String | 40 | 0)
    # OWN_ADD_L2 (String | 40 | 0)
    # OWN_ADD_L3 (String | 40 | 0)
    # TAX_NAME (String | 40 | 0)
    new.SetField('TAX_NAME', old.GetField('TAXPAYER_N'))
    # TAX_ADD_L1 (String | 40 | 0)
    new.SetField('TAX_ADD_L1', old.GetField('TAXPAYER_1'))
    # TAX_ADD_L2 (String | 40 | 0)
    new.SetField('TAX_ADD_L2', old.GetField('TAXPAYER_2'))
    # TAX_ADD_L3 (String | 40 | 0)
    new.SetField('TAX_ADD_L3', old.GetField('TAXPAYER_3'))
    # HOMESTEAD (String | 1 | 0)
    new.SetField('HOMESTEAD', 'Y' if old.GetField('HMSTD_CD1_') == 'HOMESTEAD' else (
      'N' if old.GetField('HMSTD_CD1_') == 'NON-HOMESTEAD' else None
    ))
    # EMV_LAND (Real | 11 | 0)
    new.SetField('EMV_LAND', old.GetField('EST_LAND_M'))
    # EMV_BLDG (Real | 11 | 0)
    new.SetField('EMV_BLDG', old.GetField('EST_BLDG_M'))
    # EMV_TOTAL (Real | 11 | 0)
    new.SetField('EMV_TOTAL', old.GetField('MKT_VAL_TO'))
    # TAX_CAPAC (Real | 11 | 0)
    new.SetField('TAX_CAPAC', old.GetField('NET_TAX_CA'))
    # TOTAL_TAX (Real | 11 | 0)
    new.SetField('TOTAL_TAX', old.GetField('TAX_TOT'))
    # SPEC_ASSES (Real | 11 | 0)
    # TAX_EXEMPT (String | 1 | 0)
    # XUSE1_DESC (String | 100 | 0)
    # XUSE2_DESC (String | 100 | 0)
    # XUSE3_DESC (String | 100 | 0)
    # XUSE4_DESC (String | 100 | 0)
    # DWELL_TYPE (String | 30 | 0)
    # HOME_STYLE (String | 30 | 0)
    # FIN_SQ_FT (Real | 11 | 0)
    # GARAGE (String | 1 | 0)
    # GARAGESQFT (String | 11 | 0)
    # BASEMENT (String | 1 | 0)
    # HEATING (String | 30 | 0)
    # COOLING (String | 30 | 0)
    # YEAR_BUILT (Integer | 4 | 0)
    new.SetField('YEAR_BUILT', self.parse_int(old.GetField('BUILD_YR'))
      if old.GetField('BUILD_YR') is not None else None)
    # NUM_UNITS (String | 6 | 0)
    # SALE_DATE (Date | 10 | 0)
    new.SetField('SALE_DATE', '%s-%s-01' %
      (old.GetField('SALE_DATE')[0:4], old.GetField('SALE_DATE')[4:6])
      if old.GetField('SALE_DATE') is not None else None)
    # SALE_VALUE (Real | 11 | 0)
    new.SetField('SALE_VALUE', old.GetField('SALE_PRICE'))
    # SCHOOL_DST (String | 6 | 0)
    new.SetField('SCHOOL_DST', old.GetField('SCHOOL_DIS'))
    # WSHD_DIST (String | 50 | 0)
    new.SetField('WSHD_DIST', old.GetField('WATERSHED_'))
    # GREEN_ACRE (String | 1 | 0)
    # OPEN_SPACE (String | 1 | 0)
    # AG_PRESERV (String | 1 | 0)
    # AGPRE_ENRD (Date | 10 | 0)
    # AGPRE_EXPD (Date | 10 | 0)
    # PARC_CODE (Integer | 2 | 0)

    #print new.ExportToJson()
    return new



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
    layer = getattr(self, layer_name)
    layer_count = getattr(self, '%s_count' % (layer_name))
    layer_translation = getattr(self, '%s_translation' % (layer_name))

    # Progress bar
    widgets = ['- Combining %s features of %s: ' % (layer_count, layer_name), progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    progress = progressbar.ProgressBar(widgets = widgets, maxval = layer_count).start()
    completed = 0

    # Add features to the ouput Layer
    for i in range(0, layer_count):
      existing_feature = layer.GetFeature(i)
      combined_feature = ogr.Feature(self.combined_definition)

      # Translate
      combined_feature = layer_translation(existing_feature, combined_feature)

      # Set geometry
      combined_feature.SetGeometry(existing_feature.GetGeometryRef())

      # Add new feature to output Layer
      self.combined.CreateFeature(combined_feature)

      # Save changes
      self.combined.SyncToDisk()

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


  def output_field_definitions(self, layer_name):
    """
    Outputs field definition for each reference.
    """
    self.out('- Outputting layer definition for %s:\n' % (layer_name))
    layer = getattr(self, layer_name)
    layer_definition = getattr(self, '%s_definition' % (layer_name))

    # Figure out number of fields
    field_count = layer_definition.GetFieldCount()

    # Add field values from input Layer
    for i in range(0, field_count):
      field_definition = layer_definition.GetFieldDefn(i)
      field_code = field_definition.GetType()
      self.out('%s (%s | %s | %s)\n' % (
        field_definition.GetNameRef(),
        field_definition.GetFieldTypeName(field_code),
        field_definition.GetWidth(),
        field_definition.GetPrecision()
      ))


  def process(self):
    """
    Main execution handler.
    """
    self.argparser = argparse.ArgumentParser(description = self.description, formatter_class = argparse.RawDescriptionHelpFormatter,)

    # Option to output file definition
    self.argparser.add_argument(
      '-f', '--field-definition',
      help = 'Output field definition for reference for translating.',
      default = None
    )

    # Parse options
    self.args = self.argparser.parse_args()

    # Output field defintion if so
    if self.args.field_definition not in [None, '', 0]:
      self.output_field_definitions(self.args.field_definition)
      return

    # Figure out totals
    self.get_counts()

    # Set up shape to write to
    self.define_combined()

    # Combine sources
    self.combine('anoka')
    self.combine('hennepin')

    # Spatial reference stuff
    self.make_spatial_reference()

    # Close out thing
    self.close()


# Handle execution
if __name__ == '__main__':
  mp = MetroParcels()
