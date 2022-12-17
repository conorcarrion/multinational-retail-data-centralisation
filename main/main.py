from lib.database_utils import DatabaseConnector
from lib.data_extraction import DataExtractor
from lib.data_cleaning import DataCleaner

class Main:
    def run():
        engine = DatabaseConnector.init_db_engine()
        tables = DatabaseConnector.list_db_tables(engine)
        print(tables)

        df_legacy_users = DataExtractor.df_extract_rds_table(engine, 'legacy_users')
        DataExtractor.write_data_to_csv(df_legacy_users, 'datacleaning')


if __name__ == "__main__":
    Main.run()