import logging

import geopandas as gpd
import numpy as np
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def shp_to_postgresql(conn_engine, vector_data, schema: str, table_name: str):
    """
    Загружает геоданные типа GeoDataFrame в базу данных PostgreSQL.
    """
    inspector = inspect(conn_engine)
    try:
        table_exists = inspector.has_table(table_name, schema=schema)
        if table_exists:
            existing_data = gpd.read_postgis(f"SELECT * FROM {schema}.{table_name}", conn_engine, geom_col="shape")
            if not vector_data.empty:
                vector_data = vector_data[
                    ~vector_data.apply(
                        lambda row: (
                            (existing_data["date_str"] == row["date_str"])
                            & (existing_data["fire_class"] == row["fire_class"])
                        ).any(),
                        axis=1,
                    )
                ]

                new_count = len(vector_data)
                if new_count > 0:
                    vector_data["objectid"] = np.arange(len(vector_data)) + len(existing_data) + 1
                    vector_data["objectid"] = vector_data["objectid"].astype("int32")
                    vector_data.to_postgis(name=table_name, con=conn_engine, if_exists="append", schema=schema)
                    logger.info(f"Новых объектов добавлено в таблицу {table_name}: {new_count}.")
                else:
                    logger.info(f"Все объекты уже существуют в таблице {table_name}, новых записей не добавлено.")
            else:
                logger.info(f"Нет новых записей для добавления в таблицу {table_name}.")
        else:
            vector_data["objectid"] = np.arange(len(vector_data)) + 1
            vector_data["objectid"] = vector_data["objectid"].astype("int32")
            vector_data.to_postgis(name=table_name, con=conn_engine, schema=schema)
            logger.info(f"Vector layer {table_name} added to database successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error occurred while adding vector layer {table_name} to database: {e}", exc_info=True)
