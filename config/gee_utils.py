import ee
from google.oauth2 import service_account


def initialize_earth_engine(project_name, server_account_key):
    service_account_file = server_account_key
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/earthengine", "https://www.googleapis.com/auth/drive"],
    )
    ee.Initialize(credentials, project=project_name)
