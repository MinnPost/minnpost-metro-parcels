Map {
  background-color: transparent;
}

@none: #F1F1F1;

@level1: #543005;
@level2: #8c510a;
@level3: #bf812d;
@level4: #dfc27d;
@level5: #80cdc1;
@level6: #35978f;
@level7: #01665e;
@level8: #003c30;

#parcels {
  polygon-opacity: 1;
  polygon-fill: @none;
}

#parcels {
  [HOMESTEAD='Y'],
  [USE1_DESC='RESIDENTIAL'],
  [USE1_DESC='CONDOMINIUM'],
  [USE1_DESC='CONDOMINIUMS'],
  [USE1_DESC='TOWNHOUSE'],
  [USE1_DESC='TRIPLEX'],
  [USE1_DESC='APARTMENT'],
  [USE1_DESC='RESIDENTIAL LAKE SHORE'],
  [USE1_DESC='RESIDENTIAL SINGLE FAMILY'],
  [USE1_DESC='Apt 4+ units'],
  [USE1_DESC='Res 1 unit'],
  [USE1_DESC='Res 2-3 units']
  // [USE1_DESC='Res V Land']
  {
    polygon-opacity: 1;
    polygon-fill: @none;

    [EMV_TOTAL > 0] { polygon-fill: @level1; }
    [EMV_TOTAL > 100000.0] { polygon-fill: @level2; }
    [EMV_TOTAL > 140000.0] { polygon-fill: @level3; }
    [EMV_TOTAL > 165000.0] { polygon-fill: @level4; }
    [EMV_TOTAL > 200000.0] { polygon-fill: @level5; }
    [EMV_TOTAL > 245000.0] { polygon-fill: @level6; }
    [EMV_TOTAL > 350000.0] { polygon-fill: @level7; }
    [EMV_TOTAL > 1000000.0] { polygon-fill: @level8; }
  }

  // Ramsey county has water as parcels
  [PIN=~"^WATER.*"] {
    polygon-fill: transparent;
    polygon-opacity: 0;
  }
}
