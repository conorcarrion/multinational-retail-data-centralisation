import yaml
import sqlalchemy
from sqlalchemy import create_engine, MetaData


class DatabaseConnector:
    
    def __init__(self) -> None:
        pass

    def read_db_creds():
        with open("config/db_creds.yaml", "r") as outfile:
        # Load the contents of the file as a dictionary
            credentials = yaml.load(outfile)
            return credentials

    def init_db_engine():
        credentials = DatabaseConnector.read_db_creds()
        sqlalchemy_url = sqlalchemy.engine.URL.create(
            "postgresql",
            username=credentials["RDS_USER"],
            password=credentials["RDS_PASSWORD"],
            host=credentials["RDS_HOST"],
            port=credentials["RDS_PORT"],
            database=credentials["RDS_DATABASE"]
            )
        engine = create_engine(sqlalchemy_url, echo=True, future=True)
        return engine

    def list_db_tables(engine):
        # Get the metadata for the database
        metadata = MetaData(bind=engine)
        # Reflect all the tables in the database
        metadata.reflect()
        # Return the list of table names
        return metadata.tables.keys()
