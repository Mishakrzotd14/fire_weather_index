import datetime
import logging.config
import sys

import ee
import geopandas as gpd

from config import settings
from config.config_logging import logging_config
from config.gee_utils import initialize_earth_engine
from db.shp_to_db import shp_to_postgresql
from fwi_gee.fire_resistance import (calculate_fwi_for_period,
                                     merge_and_process_data,
                                     process_fwi_results)

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        logger.info("----------------------------------------------------------------")
        logger.info("Starting the application")
        initialize_earth_engine(settings.gee_project_name, settings.server_account_key)

        current_year = datetime.date.today().year
        start_date = datetime.date(current_year, 4, 1)
        end_date = datetime.date.today() - datetime.timedelta(days=1)
        if (end_date - start_date).days >= 90:
            start_date = end_date - datetime.timedelta(days=90)

        timezone = "EUROPE/MINSK"
        bounds = ee.FeatureCollection(settings.aoi_name)

        vector_fire_resistance = gpd.read_postgis(
            f"SELECT * FROM {settings.DB_USER}.{settings.VECTOR_FIRE_RESISTANCE_NAME}",
            settings.engine,
            geom_col="shape",
        )

        fwi = calculate_fwi_for_period(start_date, end_date, timezone, bounds)
        attributes_gdf = process_fwi_results(fwi, bounds)

        dissolved_gdf = merge_and_process_data(vector_fire_resistance, attributes_gdf, end_date)
        if dissolved_gdf is not None:
            shp_to_postgresql(
                settings.engine,
                dissolved_gdf,
                settings.DB_USER,
                settings.TABLE_NAME,
            )
        logger.info("Application finished successfully")
    except Exception as e:
        logger.exception("An error occurred: %s", e)
        sys.exit(1)
