from lib.database_utils import DatabaseConnector
from lib.data_extraction import DataExtractor
from lib.data_cleaning import DataCleaner


class Main:
    def run():
        engine = DatabaseConnector.init_db_engine()
        tables = DatabaseConnector.list_db_tables(engine)
        try:
            print(tables.keys)
        except:
            pass

        df_legacy_users = DataExtractor.df_extract_rds_table(engine, "legacy_users")

        df_legacy_users_clean = DataCleaner.df_clean_user_data(df_legacy_users)

        DatabaseConnector.df_upload_to_db(df_legacy_users_clean, "dim_users", engine)


if __name__ == "__main__":
    Main.run()
