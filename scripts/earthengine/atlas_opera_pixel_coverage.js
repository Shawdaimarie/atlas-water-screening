// ATLAS OPERA DSWx-S1 pixel-coverage diagnostic for the registered 8+8 AOIs.
// Run in the Google Earth Engine Code Editor only after the owner has an
// approved Earth Engine-enabled Google Cloud project. This script only prints
// a diagnostic FeatureCollection; it does not export data or create assets.

var START = '2024-09-01';
// Earth Engine catalog availability was observed through 2026-10-28 UTC.
// filterDate has an exclusive end, so this includes that final catalog day.
var END_EXCLUSIVE = '2026-10-29';
var SCALE_M = 30;
var MIN_VALID_AOI_FRACTION = 0.80;
var MIN_DATES_PER_AREA = 90;

var rawAreas = [
  ['United States','Houston',-95.499149,29.648111,-95.240451,29.872689],
  ['United States','Miami',-80.316481,25.649411,-80.067119,25.873989],
  ['United States','Tampa',-82.584317,27.838311,-82.330083,28.062889],
  ['United States','New Orleans',-90.201096,29.838811,-89.941904,30.063389],
  ['United States','New York City',-74.154141,40.600511,-73.857859,40.825089],
  ['United States','Sacramento',-121.638043,38.469311,-121.350757,38.693889],
  ['United States','Atlanta',-84.523047,33.636711,-84.252953,33.861289],
  ['United States','St. Louis',-90.343134,38.514711,-90.055666,38.739289],
  ['International','Jakarta',106.732649,-6.321089,106.958551,-6.096511],
  ['International','Singapore',103.707480,1.239811,103.932120,1.464389],
  ['International','Dubai',55.146695,25.092511,55.394905,25.317089],
  ['International','Mumbai',72.758887,18.963711,72.996513,19.188289],
  ['International','Bangkok',100.386195,13.644011,100.617405,13.868589],
  ['International','Tokyo',139.512069,35.563911,139.788531,35.788489],
  ['International','Manila',120.868164,14.487211,121.100236,14.711789],
  ['International','São Paulo',-46.755791,-23.662789,-46.510809,-23.438211]
];

var areas = ee.FeatureCollection(rawAreas.map(function(row) {
  var geometry = ee.Geometry.Rectangle([row[2], row[3], row[4], row[5]], null, false);
  return ee.Feature(geometry, {
    region: row[0], city: row[1], bbox_wgs84: row[2] + ',' + row[3] + ',' + row[4] + ',' + row[5]
  });
}));

var collection = ee.ImageCollection('OPERA/DSWX/L3_V1/S1')
  .filterDate(START, END_EXCLUSIVE);

// BWTR has documented values 0=valid non-water, 1=water, 250=HAND mask,
// 251=layover/shadow. The catalog states invalid/fill values are also present;
// only 0 and 1 count as valid. A class histogram is included to expose any
// unexpected codes instead of silently treating them as valid observations.
function summarizeArea(area) {
  area = ee.Feature(area);
  var geom = area.geometry();
  var local = collection.filterBounds(geom);
  var dayStrings = ee.List(local.aggregate_array('system:time_start'))
    .map(function(ms) { return ee.Date(ms).format('YYYY-MM-dd'); })
    .distinct().sort();

  var rows = dayStrings.map(function(dayString) {
    dayString = ee.String(dayString);
    var day = ee.Date.parse('YYYY-MM-dd', dayString);
    var dayCollection = local.filterDate(day, day.advance(1, 'day'));
    var mosaic = dayCollection.mosaic();
    var bwtr = mosaic.select('BWTR_Binary_water');
    var valid = bwtr.eq(0).or(bwtr.eq(1));
    var water = bwtr.eq(1).updateMask(valid);
    var validArea = ee.Image.pixelArea().updateMask(valid).rename('valid_m2');
    var waterArea = ee.Image.pixelArea().updateMask(water).rename('water_m2');
    var invalidArea = ee.Image.pixelArea()
      .updateMask(bwtr.eq(250).or(bwtr.eq(251))).rename('known_invalid_m2');
    var histogram = bwtr.reduceRegion({
      reducer: ee.Reducer.frequencyHistogram(), geometry: geom, scale: SCALE_M,
      maxPixels: 1e9, tileScale: 4
    }).get('BWTR_Binary_water');
    var sums = ee.Image.cat([validArea, waterArea, invalidArea]).reduceRegion({
      reducer: ee.Reducer.sum(), geometry: geom, scale: SCALE_M,
      maxPixels: 1e9, tileScale: 4
    });
    var validM2 = ee.Number(ee.Dictionary(sums).get('valid_m2', 0));
    var waterM2 = ee.Number(ee.Dictionary(sums).get('water_m2', 0));
    var invalidM2 = ee.Number(ee.Dictionary(sums).get('known_invalid_m2', 0));
    var aoiM2 = geom.area(1);
    var validFraction = validM2.divide(aoiM2);
    return ee.Feature(null, area.toDictionary())
      .set({
        acquisition_date_utc: dayString,
        source_collection: 'OPERA/DSWX/L3_V1/S1',
        source_product_versions: ee.List(dayCollection.aggregate_array('DSWX_PRODUCT_VERSION'))
          .distinct().sort().join(','),
        source_image_count: dayCollection.size(),
        scale_m: SCALE_M,
        valid_area_m2: validM2,
        water_area_m2: waterM2,
        known_invalid_area_m2: invalidM2,
        aoi_area_m2: aoiM2,
        valid_aoi_fraction: validFraction,
        meets_80pct_coverage_gate: validFraction.gte(MIN_VALID_AOI_FRACTION),
        bwtr_class_histogram: histogram
      });
  });
  return ee.FeatureCollection(rows);
}

var diagnostics = ee.FeatureCollection(areas.iterate(function(area, acc) {
  return ee.FeatureCollection(acc).merge(summarizeArea(area));
}, ee.FeatureCollection([])));

var areaSummary = ee.FeatureCollection(areas.map(function(area) {
  area = ee.Feature(area);
  var areaRows = diagnostics.filter(ee.Filter.eq('city', area.get('city')));
  var dates = areaRows.size();
  var passing = areaRows.filter(ee.Filter.eq('meets_80pct_coverage_gate', true)).size();
  return area.set({
    date_count: dates,
    dates_at_or_above_80pct_valid_pixels: passing,
    passes_90_date_metadata_screen: ee.Number(dates).gte(MIN_DATES_PER_AREA),
    dataset_max_date: END_EXCLUSIVE
  });
}));

print('ATLAS per-area summary (metadata date count is not QA coverage)', areaSummary);
print('ATLAS per-acquisition pixel QA diagnostics (inspect histogram for unknown codes)', diagnostics);
print('Dataset', collection.limit(1));
Map.centerObject(areas, 2);
Map.addLayer(areas, {color: 'yellow'}, 'Registered ATLAS 8+8 AOIs');
