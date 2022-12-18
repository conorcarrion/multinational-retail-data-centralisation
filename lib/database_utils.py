import yaml
import sqlalchemy
from sqlalchemy import create_engine, MetaData


class DatabaseConnector:
    def __init__(self) -> None:
        pass

    def read_db_creds():
        with open("config/db_creds.yaml", "r") as outfile:
            # Load the contents of the file as a dictionary
            credentials = yaml.safe_load(outfile)
            return credentials

    def init_db_engine():
        credentials = DatabaseConnector.read_db_creds()
        sqlalchemy_url = sqlalchemy.engine.URL.create(
            "postgresql",
            username=credentials["RDS_USER"],
            password=credentials["RDS_PASSWORD"],
            host=credentials["RDS_HOST"],
            port=credentials["RDS_PORT"],
            database=credentials["RDS_DATABASE"],
        )
        engine = create_engine(sqlalchemy_url)
        return engine

    def list_db_tables(engine):
        # Get the metadata for the database
        metadata = MetaData(bind=engine)

        # Return the list of table names
        return metadata.tables.keys()

    def df_upload_to_db(df, tablename, engine):
        try:
            df.to_sql(f"{tablename}", engine)
            return True
        except:
            return False
