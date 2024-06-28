import datetime
import sys

import ee
import geopandas as gpd
from shapely.geometry import MultiPolygon

from fwi_gee.fwi_calculate import FWICalculator
from fwi_gee.fwi_inputs import FWI_GFS_GSMAP

sys.setrecursionlimit(20000)


def calculate_fwi_for_period(first_date, date_end, time_zone, aoi):
    """Calculate FWI for the specified period."""
    current_date = first_date
    calculator = FWICalculator(current_date, None)
    while current_date <= date_end:
        if current_date == first_date:
            calculator.set_previous_codes()

        else:
            calculator.set_previous_codes(calculator.ffmc, calculator.dmc, calculator.dc)
        fwi_inputs = FWI_GFS_GSMAP(current_date, time_zone, aoi)
        calculator.update_inputs(fwi_inputs)
        current_date = calculator.obs

    return calculator.compute()


def process_fwi_results(fwi_result, bounds):
    """Process FWI results."""
    fwi_result = fwi_result.reproject(crs="EPSG:4326", scale=11132.0).resample("bicubic")
    mean_dict = fwi_result.reduceRegions(collection=bounds, reducer=ee.Reducer.mean(), scale=10)
    features = mean_dict.getInfo()["features"]
    attributes_gdf = gpd.GeoDataFrame([feat["properties"] for feat in features])
    attributes_gdf = attributes_gdf.rename(columns={"mean": "fwi_mean"})
    return attributes_gdf


def classify_fire_risk(value):
    if 0 < value < 10:
        return 1
    elif 10 <= value < 20:
        return 2
    elif 20 <= value < 30:
        return 3
    elif 30 <= value < 40:
        return 4
    elif value >= 40:
        return 5
    else:
        return 0


def merge_and_process_data(vector, attributes_gdf, date):
    """Merge vector data with attributes and process."""
    merged_gdf = vector.merge(attributes_gdf[["id", "fwi_mean"]], on="id", how="left")
    merged_gdf["fwi_risk"] = merged_gdf["fwi_mean"] * merged_gdf["fr_index"]
    merged_gdf["fire_class"] = merged_gdf["fwi_risk"].apply(classify_fire_risk)
    merged_gdf = merged_gdf[merged_gdf["fire_class"] != 0]
    merged_gdf = merged_gdf[["fire_class", "fwi_mean", "fwi_risk", "shape"]]
    dissolved_gdf = merged_gdf.dissolve(by="fire_class", aggfunc="mean", as_index=False)
    dissolved_gdf["date"] = date
    dissolved_gdf[
        "date_str"
    ] = f"{date.strftime('%Y.%m.%d')}-{(date + datetime.timedelta(days=1)).strftime('%Y.%m.%d')}"
    dissolved_gdf['shape'] = dissolved_gdf['shape'].apply(
        lambda geom: MultiPolygon([geom]) if geom.type == 'Polygon' else geom)
    return dissolved_gdf
