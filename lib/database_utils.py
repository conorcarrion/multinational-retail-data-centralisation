import yaml
import sqlalchemy
from sqlalchemy import create_engine, inspect


class DatabaseConnector:
    def __init__(self) -> None:
        pass

    def load_yaml(path):
        with open(path, "r") as outfile:
            # Load the contents of the file as a dictionary
            credentials = yaml.safe_load(outfile)
            return credentials

    def init_db_engine(credentials):

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
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        for table_name in table_names:
            print(table_name)
        return table_names

    def df_upload_to_db(df, tablename, engine):
        try:
            df.to_sql(f"{tablename}", engine)
            return True
        except:
            return False
