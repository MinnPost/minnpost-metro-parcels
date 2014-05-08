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
  [USE1_DESC='TOWNHOUSE'],
  [USE1_DESC='APARTMENT'],
  [USE1_DESC='RESIDENTIAL LAKE SHORE'],
  [USE1_DESC='RESIDENTIAL SINGLE FAMILY'] {
    polygon-opacity: 1;
    polygon-fill: @none;
    
    [EMV_TOTAL > 0]        { polygon-fill: @level1; }
    [EMV_TOTAL > 50000]    { polygon-fill: @level2; }
    [EMV_TOTAL > 75000]    { polygon-fill: @level3;}
    [EMV_TOTAL > 100000]   { polygon-fill: @level4; }
    [EMV_TOTAL > 250000]   { polygon-fill: @level5; }
    [EMV_TOTAL > 500000]   { polygon-fill: @level6; }
    [EMV_TOTAL > 750000]  { polygon-fill: @level7; }
    [EMV_TOTAL > 1000000]  { polygon-fill: @level8; }
   }
}
