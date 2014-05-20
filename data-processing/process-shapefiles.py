"""
Process shapefiles.

County ID numbers:
http://www.sos.state.mn.us/index.aspx?page=1630
"""


import logging, os, sys, argparse
import progressbar
import numpy
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
  source_shape_ramsey = os.path.join(script_path, '../data/reprojected_4326-shps/ramsey-parcels.shp')
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
    self.shape_ramsey = self.in_driver.Open(self.source_shape_ramsey, 0)
    if self.shape_hennepin is None or self.shape_anoka is None or self.shape_ramsey is None:
      self.error('Could not find a necessary shapefile')
      sys.exit(1)

    # Get actual layers
    self.hennepin = self.shape_hennepin.GetLayer()
    self.anoka = self.shape_anoka.GetLayer()
    self.ramsey = self.shape_ramsey.GetLayer()

    # Get layer definitions (no need to do this more than once)
    self.hennepin_definition = self.hennepin.GetLayerDefn()
    self.anoka_definition = self.anoka.GetLayerDefn()
    self.ramsey_definition = self.ramsey.GetLayerDefn()

    # Start pocessing
    self.process()


  def close(self):
    """
    Close out data sources
    """
    self.shape_hennepin.Destroy()
    self.shape_anoka.Destroy()
    self.shape_ramsey.Destroy()
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


  def parse_float(self, s):
    """
    Parse float.
    """
    try:
      return float(s) if s is not None else None
    except ValueError:
      return None


  def parse_num(self, s):
    """
    Parse number.
    """
    try:
      return int(s) if s is not None else None
    except ValueError:
      try:
        return float(s) if s is not None else None
      except ValueError:
        return None


  def get_counts(self):
    """
    Get feature count.
    """
    self.hennepin_count = self.hennepin.GetFeatureCount()
    self.anoka_count = self.anoka.GetFeatureCount()
    self.ramsey_count = self.ramsey.GetFeatureCount()


  def define_combined(self, remove_old = True, create_fields = True):
    """
    Adds field definitions to shapes.  We know Anoka has the fields we want.
    http://www.datafinder.org/metadata/ParcelsCurrent.html#Entity_and_Attribute_Information
    """
    self.out('- Creating combined layer.\n')

    # Create layer to write to
    if not os.path.exists(os.path.dirname(self.source_shape_combined)):
      os.makedirs(os.path.dirname(self.source_shape_combined))
    if os.path.exists(self.source_shape_combined) and remove_old:
      self.out_driver.DeleteDataSource(self.source_shape_combined)

    # Open or create combined
    if os.path.exists(self.source_shape_combined):
      self.shape_combined = self.out_driver.Open(self.source_shape_combined, 1)
      self.combined = self.shape_combined.GetLayer()
    else:
      self.shape_combined = self.out_driver.CreateDataSource(self.source_shape_combined)
      self.combined = self.shape_combined.CreateLayer('metro_parcels', geom_type = ogr.wkbPolygon)

    # Create field definition from anoka
    if create_fields:
      for i in range(0, self.anoka_definition.GetFieldCount()):
        field = self.anoka_definition.GetFieldDefn(i)
        self.combined.CreateField(field)

    # Create other fields here

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
    new.SetField('EMV_LAND', self.parse_float(old.GetField('EST_LAND_M')))
    # EMV_BLDG (Real | 11 | 0)
    new.SetField('EMV_BLDG', self.parse_float(old.GetField('EST_BLDG_M')))
    # EMV_TOTAL (Real | 11 | 0)
    new.SetField('EMV_TOTAL', self.parse_float(old.GetField('MKT_VAL_TO'))
      if old.GetField('MKT_VAL_TO') is not None else None)
    # TAX_CAPAC (Real | 11 | 0)
    new.SetField('TAX_CAPAC', self.parse_float(old.GetField('NET_TAX_CA')))
    # TOTAL_TAX (Real | 11 | 0)
    new.SetField('TOTAL_TAX', self.parse_float(old.GetField('TAX_TOT')))
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
      if old.GetField('SALE_DATE') is not None
         and self.parse_num(old.GetField('SALE_DATE')) > 0 else None)
    # SALE_VALUE (Real | 11 | 0)
    new.SetField('SALE_VALUE', self.parse_float(old.GetField('SALE_PRICE')))
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


  def ramsey_translation(self, old, new):
    """
    Translation layer for each feature for Ramsey.  We have to basically
    manually translate.

    See: data/ramsey-shp-gdb/Metadata/CDSTL_AttributedParcelPoly.html
    """

    """
    Ramsey fields (not used)
    FIPsPID (String | 17 | 0)
    RollType (String | 1 | 0)
    BldgSuf (String | 3 | 0)
    StrSufType (String | 4 | 0)
    StrSufDir (String | 2 | 0)
    StrNameAll (String | 40 | 0)
    SiteAdd (String | 70 | 0)
    SiteZIP (String | 12 | 0)
    SiteCSZ (String | 60 | 0)
    PrimLast (String | 65 | 0)
    PrimName (String | 65 | 0)
    PrimName1 (String | 65 | 0)
    PrimName2 (String | 65 | 0)
    PrimAdd1 (String | 30 | 0)
    PrimAdd2 (String | 30 | 0)
    PrimAdd (String | 60 | 0)
    PrimCity (String | 20 | 0)
    PrimState (String | 2 | 0)
    PrimZIP5 (String | 5 | 0)
    PrimZIP4 (String | 4 | 0)
    PrimCntry (String | 20 | 0)
    PrimCSZ (String | 60 | 0)
    AltName1 (String | 65 | 0)
    AltName2 (String | 65 | 0)
    AltAdd1 (String | 30 | 0)
    AltAdd2 (String | 30 | 0)
    AltAdd (String | 60 | 0)
    AltCity (String | 20 | 0)
    AltState (String | 2 | 0)
    AltZIP5 (String | 5 | 0)
    AltZIP4 (String | 4 | 0)
    AltCntry (String | 20 | 0)
    AltCSZ (String | 40 | 0)
    HmstdName1 (String | 65 | 0)
    HmstdName2 (String | 65 | 0)
    HmstdAdd1 (String | 30 | 0)
    HmstdAdd2 (String | 30 | 0)
    HmstdAdd (String | 60 | 0)
    HmstdCity (String | 20 | 0)
    HmstdState (String | 2 | 0)
    HmstdZIP5 (String | 5 | 0)
    HmstdZIP4 (String | 4 | 0)
    HmstdCSZ (String | 60 | 0)
    TIFDist (String | 10 | 0)
    SchDist (String | 50 | 0)
    WshdIDTax (String | 3 | 0)
    WshdPoly (String | 60 | 0)
    PlatID (String | 20 | 0)
    TaxDesc (String | 254 | 0)
    PlatDate (Date | 10 | 0)
    Abstract (String | 14 | 0)
    Torrens (String | 14 | 0)
    SqFt (Real | 19 | 11)
    Frontage (Real | 19 | 11)
    LoanCo (String | 10 | 0)
    LoanCoName (String | 30 | 0)
    TaxYear (Integer | 4 | 0)
    EMVYear (Integer | 4 | 0)
    TaxYear1 (Integer | 4 | 0)
    EMVYear1 (Integer | 4 | 0)
    EMVLand1 (Real | 19 | 11)
    EMVBldg1 (Real | 19 | 11)
    EMVTotal1 (Real | 19 | 11)
    TotalTax1 (Real | 19 | 11)
    SpAssess1 (Real | 19 | 11)
    TaxYear2 (Integer | 4 | 0)
    EMVYear2 (Integer | 4 | 0)
    EMVLand2 (Real | 19 | 11)
    EMVBldg2 (Real | 19 | 11)
    EMVTotal2 (Real | 19 | 11)
    TotalTax2 (Real | 19 | 11)
    SpAssess2 (Real | 19 | 11)
    LUC (String | 43 | 0)
    HmstdDesc (String | 45 | 0)
    Structure (String | 32 | 0)
    ExtWall (String | 16 | 0)
    Stories (Integer | 4 | 0)
    RoomTotal (Integer | 4 | 0)
    BedRoom (Integer | 4 | 0)
    FamilyRoom (Integer | 4 | 0)
    Topology (String | 12 | 0)
    Utility (String | 16 | 0)
    X (Real | 19 | 11)
    Y (Real | 19 | 11)
    Latitude (Real | 19 | 11)
    Longitude (Real | 19 | 11)
    ParcelCode (Integer | 4 | 0)
    JoinDate (Date | 10 | 0)
    """

    # If there is not a conversion below the field, it means there is not
    # an eqivalent in Ramsey

    # COUNTY_ID (String | 3 | 0)
    new.SetField('COUNTY_ID', '62')
    # PIN (String | 17 | 0)
    new.SetField('PIN', old.GetField('ParcelID'))
    # BLDG_NUM (String | 10 | 0)
    new.SetField('BLDG_NUM', old.GetField('BldgNum'))
    # PREFIX_DIR (String | 2 | 0)
    new.SetField('PREFIX_DIR', old.GetField('StrPreDir'))
    # PREFIXTYPE (String | 6 | 0)
    new.SetField('PREFIXTYPE', old.GetField('StrPreType'))
    # STREETNAME (String | 40 | 0)
    new.SetField('STREETNAME', old.GetField('StreetName'))
    # STREETTYPE (String | 4 | 0)
    # SUFFIX_DIR (String | 2 | 0)
    new.SetField('SUFFIX_DIR', old.GetField('StrSufDir'))
    # UNIT_INFO (String | 12 | 0)
    new.SetField('UNIT_INFO', old.GetField('Unit'))
    # CITY (String | 30 | 0)
    new.SetField('CITY', old.GetField('SiteCity'))
    # CITY_USPS (String | 30 | 0)
    new.SetField('CITY_USPS', old.GetField('SiteCityPS'))
    # ZIP (String | 5 | 0)
    new.SetField('ZIP', old.GetField('SiteZIP5'))
    # ZIP4 (String | 4 | 0)
    new.SetField('ZIP4', old.GetField('SiteZIP4'))
    # PLAT_NAME (String | 50 | 0)
    new.SetField('PLAT_NAME', old.GetField('PlatName'))
    # BLOCK (String | 5 | 0)
    new.SetField('BLOCK', old.GetField('Block'))
    # LOT (String | 5 | 0)
    new.SetField('LOT', old.GetField('Lot'))
    # ACRES_POLY (Real | 11 | 2)
    new.SetField('ACRES_POLY', old.GetField('AcresPoly'))
    # ACRES_DEED (Real | 11 | 2)
    new.SetField('ACRES_DEED', old.GetField('AcresDeed'))
    # USE1_DESC (String | 100 | 0)
    new.SetField('USE1_DESC', old.GetField('UseType1'))
    # USE2_DESC (String | 100 | 0)
    new.SetField('USE2_DESC', old.GetField('UseType2'))
    # USE3_DESC (String | 100 | 0)
    new.SetField('USE3_DESC', old.GetField('UseType3'))
    # USE4_DESC (String | 100 | 0)
    new.SetField('USE4_DESC', old.GetField('UseType4'))
    # MULTI_USES (String | 1 | 0)
    new.SetField('MULTI_USES', old.GetField('MultiUseYN'))
    # LANDMARK (String | 100 | 0)
    new.SetField('LANDMARK', old.GetField('Landmark'))
    # OWNER_NAME (String | 50 | 0)
    # OWNER_MORE (String | 50 | 0)
    # OWN_ADD_L1 (String | 40 | 0)
    # OWN_ADD_L2 (String | 40 | 0)
    # OWN_ADD_L3 (String | 40 | 0)
    # TAX_NAME (String | 40 | 0)
    # TAX_ADD_L1 (String | 40 | 0)
    # TAX_ADD_L2 (String | 40 | 0)
    # TAX_ADD_L3 (String | 40 | 0)
    # HOMESTEAD (String | 1 | 0)
    new.SetField('HOMESTEAD', old.GetField('HmstdYN'))
    # EMV_LAND (Real | 11 | 0)
    new.SetField('EMV_LAND', old.GetField('EMVLand'))
    # EMV_BLDG (Real | 11 | 0)
    new.SetField('EMV_BLDG', old.GetField('EMVBldg'))
    # EMV_TOTAL (Real | 11 | 0)
    new.SetField('EMV_TOTAL', old.GetField('EMVTotal'))
    # TAX_CAPAC (Real | 11 | 0)
    new.SetField('TAX_CAPAC', old.GetField('TaxCap'))
    # TOTAL_TAX (Real | 11 | 0)
    new.SetField('TOTAL_TAX', old.GetField('TotalTax'))
    # SPEC_ASSES (Real | 11 | 0)
    new.SetField('SPEC_ASSES', old.GetField('SpAssess'))
    # TAX_EXEMPT (String | 1 | 0)
    new.SetField('TAX_EXEMPT', old.GetField('TaxExYN'))
    # XUSE1_DESC (String | 100 | 0)
    new.SetField('XUSE1_DESC', old.GetField('ExemptUse1'))
    # XUSE2_DESC (String | 100 | 0)
    new.SetField('XUSE2_DESC', old.GetField('ExemptUse2'))
    # XUSE3_DESC (String | 100 | 0)
    new.SetField('XUSE3_DESC', old.GetField('ExemptUse3'))
    # XUSE4_DESC (String | 100 | 0)
    new.SetField('XUSE4_DESC', old.GetField('ExemptUse4'))
    # DWELL_TYPE (String | 30 | 0)
    new.SetField('DWELL_TYPE', old.GetField('DwellType'))
    # HOME_STYLE (String | 30 | 0)
    new.SetField('HOME_STYLE', old.GetField('HomeStyle'))
    # FIN_SQ_FT (Real | 11 | 0)
    new.SetField('FIN_SQ_FT', old.GetField('LivingSqFt'))
    # GARAGE (String | 1 | 0)
    new.SetField('GARAGE', old.GetField('GarageYN'))
    # GARAGESQFT (String | 11 | 0)
    new.SetField('GARAGESQFT', old.GetField('GarageSqFt'))
    # BASEMENT (String | 1 | 0)
    new.SetField('BASEMENT', old.GetField('BasementYN'))
    # HEATING (String | 30 | 0)
    new.SetField('HEATING', old.GetField('HeatType'))
    # COOLING (String | 30 | 0)
    new.SetField('COOLING', old.GetField('CoolType'))
    # YEAR_BUILT (Integer | 4 | 0)
    new.SetField('YEAR_BUILT', old.GetField('YearBuilt'))
    # NUM_UNITS (String | 6 | 0)
    new.SetField('NUM_UNITS', old.GetField('LivingUnit'))
    # SALE_DATE (Date | 10 | 0)
    new.SetField('SALE_DATE', old.GetField('LastSale'))
    # SALE_VALUE (Real | 11 | 0)
    new.SetField('SALE_VALUE', old.GetField('SalePrice'))
    # SCHOOL_DST (String | 6 | 0)
    new.SetField('SCHOOL_DST', old.GetField('SchDistNum'))
    # WSHD_DIST (String | 50 | 0)
    new.SetField('WSHD_DIST', old.GetField('WshdTax'))
    # GREEN_ACRE (String | 1 | 0)
    new.SetField('GREEN_ACRE', old.GetField('GrnAcresYN'))
    # OPEN_SPACE (String | 1 | 0)
    new.SetField('OPEN_SPACE', old.GetField('OpenSpcYN'))
    # AG_PRESERV (String | 1 | 0)
    new.SetField('AG_PRESERV', old.GetField('AgPYN'))
    # AGPRE_ENRD (Date | 10 | 0)
    new.SetField('AGPRE_ENRD', old.GetField('AgPEnroll'))
    # AGPRE_EXPD (Date | 10 | 0)
    new.SetField('AGPRE_EXPD', old.GetField('AgPExpire'))
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

    # Manual settings
    new.SetField('COUNTY_ID', '2')

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


  def output_field_source(self, layer_name, field_name, limit):
    """
    Outputs field values for source field.
    """
    self.out('- Outputting values for field %s in %s:\n' % (field_name, layer_name))
    layer = getattr(self, layer_name)
    layer_definition = getattr(self, '%s_definition' % (layer_name))
    count = 0

    for feature in layer:
      if count < limit:
        self.out('%s\n' % (feature.GetField(field_name)))
      else:
        break

      count = count + 1


  def output_field_values(self, field_name):
    """
    Outputs field values for a field.
    """
    found = {}
    count = self.combined.GetFeatureCount()
    widgets = ['- Finding values for %s: ' % (field_name), progressbar.Percentage(), ' ', progressbar.ETA()]
    progress = progressbar.ProgressBar(widgets = widgets, maxval = count).start()
    completed = 0

    # Go through each feature
    for feature in self.combined:
      found[feature.GetField(field_name)] = found[feature.GetField(field_name)] + 1 if feature.GetField(field_name) in found else 1

      # Update progress
      completed = completed + 1
      progress.update(completed)

    # Stop progress bar
    progress.finish()

    # Output results orderd by key
    found_sorted = iter(sorted(found.items()))
    for k, v in found_sorted:
      self.out('%s (%s)\n' % (k, v))


  def output_stats(self, stat):
    """
    Gets some basic stats for certain groups.
    """
    found = []
    count = self.combined.GetFeatureCount()
    widgets = ['- Gathering data stats on "%s": ' % (stat), progressbar.Percentage(), ' ', progressbar.ETA()]
    progress = progressbar.ProgressBar(widgets = widgets, maxval = count).start()
    completed = 0

    # Under 1M
    if stat == 'residential-1M':
      for feature in self.combined:
        amount = feature.GetField('EMV_TOTAL')
        if amount <= 1000000 and amount > 0:
          found.append(amount)

        # Update progress
        completed = completed + 1
        progress.update(completed)

      # Stop progress bar
      progress.finish()

      # Stats
      found_array = numpy.array(found)
      self.out('\n')
      self.out('Min: %s\n' % (numpy.min(found_array)))
      self.out('Max: %s\n' % (numpy.max(found_array)))
      self.out('Median: %s\n' % (numpy.median(found_array)))

      # Quantiles
      intervals = 7
      self.out('\n')
      for x in range(0, intervals + 1):
        step = (100 / float(intervals)) * float(x)
        self.out('Quantile %s: %s\n' % (step, numpy.percentile(found_array, step)))

      # Carto output
      self.out('\n')
      for x in range(0, intervals + 1):
        step = (100 / float(intervals)) * float(x)
        value = numpy.percentile(found_array, step) if x > 0 else 0
        self.out('    [EMV_TOTAL > %s] { polygon-fill: @level%s; }\n' % (value, x + 1))

      # Original
      #[EMV_TOTAL > 0]        { polygon-fill: @level1; }
      #[EMV_TOTAL > 50000]    { polygon-fill: @level2; }
      #[EMV_TOTAL > 75000]    { polygon-fill: @level3; }
      #[EMV_TOTAL > 100000]   { polygon-fill: @level4; }
      #[EMV_TOTAL > 250000]   { polygon-fill: @level5; }
      #[EMV_TOTAL > 500000]   { polygon-fill: @level6; }
      #[EMV_TOTAL > 750000]   { polygon-fill: @level7; }
      #[EMV_TOTAL > 1000000]  { polygon-fill: @level8; }


  def process(self):
    """
    Main execution handler.
    """
    self.argparser = argparse.ArgumentParser(description = self.description, formatter_class = argparse.RawDescriptionHelpFormatter,)

    # Option to output field definition
    self.argparser.add_argument(
      '--field-definition',
      help = 'Output field definition for reference for translating.',
      default = None
    )

    # Option to output field values for source
    self.argparser.add_argument(
      '--field-values-source',
      help = 'Output field values for a specific field of a source data; this should be in the format of source&field&limit, for example "ramsey#SiteCityPS#100".',
      default = None
    )

    # Option to output field values
    self.argparser.add_argument(
      '--field-values-first',
      help = 'Output field values for a specific field of the combined data; min and max if not string. Without combining.',
      default = None
    )

    # Option to output field values
    self.argparser.add_argument(
      '--field-values-last',
      help = 'Output field values for a specific field of the combined data; min and max if not string. After combining.',
      default = None
    )

    # Option to output field values
    self.argparser.add_argument(
      '--stats-residential-emv',
      help = 'Output some basic stats for EMV values under 1M.',
      action = 'store_true'
    )

    # Parse options
    self.args = self.argparser.parse_args()

    # Output field defintion if so
    if self.args.field_definition not in [None, '', 0]:
      self.output_field_definitions(self.args.field_definition)
      return

    # Output field values for source
    if self.args.field_values_source not in [None, '', 0]:
      source, field, limit = self.args.field_values_source.split('#')
      self.output_field_source(source, field, int(limit))
      return

    # Output field values for combined
    if self.args.field_values_first not in [None, '', 0]:
      self.define_combined(False, False)
      self.output_field_values(self.args.field_values_first)
      self.close()
      return

    # Stats
    if self.args.stats_residential_emv:
      self.define_combined(False, False)
      self.output_stats('residential-1M')
      self.close()
      return


    # Figure out totals
    self.get_counts()

    # Set up shape to write to
    self.define_combined()

    # Combine sources.  For some reason if we do hennepin first, it hangs
    # on anoka
    self.combine('ramsey')
    self.combine('anoka')
    self.combine('hennepin')

    # Spatial reference stuff
    self.make_spatial_reference()

    # Output field defintion if so
    if self.args.field_values_last not in [None, '', 0]:
      self.output_field_values(self.args.field_values_last)

    # Close out thing
    self.close()


# Handle execution
if __name__ == '__main__':
  mp = MetroParcels()
