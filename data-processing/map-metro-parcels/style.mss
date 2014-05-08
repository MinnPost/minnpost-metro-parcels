Map {
  background-color: transparent;
}

@none: #F1F1F1;

@level1: #543005;
@level2: #8c510a;
@level3: #bf812d;
@level4: #dfc27d;

@level5: #c7eae5;
@level6: #80cdc1;
@level7: #35978f;
@level8: #01665e;
@level9: #003c30;

#parcels {
  polygon-opacity: 1;
  polygon-fill: @none;
  
  [EMV_TOTAL > 0]         { polygon-fill: @level1; }
  [EMV_TOTAL > 100000]    { polygon-fill: @level2; }
  [EMV_TOTAL > 250000]    { polygon-fill: @level3;}
  [EMV_TOTAL > 500000]    { polygon-fill: @level4; }
  [EMV_TOTAL > 1000000]   { polygon-fill: @level5; }
  [EMV_TOTAL > 2000000]   { polygon-fill: @level6; }
  [EMV_TOTAL > 5000000]   { polygon-fill: @level7; }
  [EMV_TOTAL > 20000000]  { polygon-fill: @level8; }
  [EMV_TOTAL > 100000000] { polygon-fill: @level9; }
}
