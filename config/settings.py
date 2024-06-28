import os

from sqlalchemy import create_engine

from dotenv import load_dotenv

current_directory = os.getcwd()
dotenv_path = os.path.join(current_directory, "dotenv", ".env")
load_dotenv(dotenv_path)

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_DATABASE = os.environ["DB_DATABASE"]

conn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
engine = create_engine(conn)

gee_project_name = "ee-mkurzenkovotd14"
aoi_name = "projects/ee-mkurzenkovotd14/assets/naroch_pozaroust"

server_account_key = os.path.join(os.path.dirname(__file__), "service-account-key.json")

VECTOR_FIRE_RESISTANCE_NAME = "fire_resistance"
TABLE_NAME = "fire_res_class"
