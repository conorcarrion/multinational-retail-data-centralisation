from lib.database_utils import DatabaseConnector
from lib.data_extraction import DataExtractor
from lib.data_cleaning import DataCleaner


class Main:
    def create_engines():
        aicore_credentials = DatabaseConnector.read_db_creds(
            "config/aicore_db_creds.yaml"
        )
        sales_credentials = DatabaseConnector.read_db_creds(
            "config/sales_db_creds.yaml"
        )

        aicore_engine = DatabaseConnector.init_db_engine(aicore_credentials)
        sales_engine = DatabaseConnector.init_db_engine(sales_credentials)
        return aicore_engine, sales_engine

    def create_dim_users(aicore_engine, sales_engine):

        df_legacy_users = DataExtractor.df_extract_rds_table(
            aicore_engine, "legacy_users"
        )

        df_legacy_users_clean = DataCleaner.df_clean_user_data(df_legacy_users)

        DatabaseConnector.df_upload_to_db(
            df_legacy_users_clean, "dim_users", sales_engine
        )

    def create_dim_card_details(sales_engine):
        aicore_s3_creds = DatabaseConnector.read_db_creds("config/aicore_S3_link.yaml")
        aicore_s3_link = aicore_s3_creds["AWS_S3_LINK"]

        df_legacy_card_details = DataExtractor.retrieve_pdf_data(aicore_s3_link)

        df_legacy_card_details_clean = DataCleaner.df_clean_card_data(
            df_legacy_card_details
        )

        DatabaseConnector.df_upload_to_db(
            df_legacy_card_details_clean, "dim_card_details", sales_engine
        )

    def run():
        aicore_engine, sales_engine = Main.create_engines()

        Main.create_dim_users(aicore_engine, sales_engine)
        Main.create_dim_card_details(sales_engine)


if __name__ == "__main__":
    Main.run()
