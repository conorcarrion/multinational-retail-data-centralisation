from lib.database_utils import DatabaseConnector
from lib.data_extraction import DataExtractor
from lib.data_cleaning import DataCleaner


class Main:
    def create_engines():
        aicore_credentials = DatabaseConnector.load_yaml("config/aicore_db_creds.yaml")
        sales_credentials = DatabaseConnector.load_yaml("config/sales_db_creds.yaml")

        aicore_engine = DatabaseConnector.init_db_engine(aicore_credentials)
        sales_engine = DatabaseConnector.init_db_engine(sales_credentials)
        return aicore_engine, sales_engine

    def create_dim_users(aicore_engine, sales_engine):

        df_legacy_users = DataExtractor.extract_rds_table(aicore_engine, "legacy_users")

        df_legacy_users_clean = DataCleaner.clean_users_df(df_legacy_users)

        DatabaseConnector.df_upload_to_db(
            df_legacy_users_clean, "dim_users", sales_engine
        )

    def create_dim_card_details(sales_engine):
        s3_pdf_link = DatabaseConnector.load_yaml("config/s3_card_details_pdf.yaml")
        s3_pdf_card_details = s3_pdf_link["AWS_S3_LINK"]

        df_legacy_card_details = DataExtractor.retrieve_pdf_data(s3_pdf_card_details)

        df_legacy_card_details_clean = DataCleaner.clean_card_details_df(
            df_legacy_card_details
        )

        DatabaseConnector.df_upload_to_db(
            df_legacy_card_details_clean, "dim_card_details", sales_engine
        )

    def create_dim_store_details(sales_engine):
        api_credentials = DatabaseConnector.load_yaml("config/aicore_api_key.yaml")
        headers = {"x-api-key": api_credentials["x-api-key"]}
        get_store_endpoint = api_credentials["get-store"]
        get_num_stores_endpoint = api_credentials["get-num-stores"]

        number_of_stores = DataExtractor.API_list_number_of_stores(
            get_num_stores_endpoint, headers
        )

        df_legacy_store_details = DataExtractor.retrieve_stores_data(
            get_store_endpoint, headers, number_of_stores
        )

        df_legacy_store_details = DataCleaner.clean_store_details_df(
            df_legacy_store_details
        )

        DatabaseConnector.df_upload_to_db(
            df_legacy_store_details, "dim_store_details", sales_engine
        )

    def create_products_table(sales_engine):

        products_creds = DatabaseConnector.load_yaml(
            "config/s3_product_details_csv.yaml"
        )

        df_legacy_product_table = DataExtractor.extract_from_public_s3(
            products_creds["Bucket"], products_creds["Key"]
        )

        df_legacy_product_table = DataCleaner.clean_products_table_df(
            df_legacy_product_table
        )

        DatabaseConnector.df_upload_to_db(
            df_legacy_product_table, "products_table", sales_engine
        )

    def create_orders_table(aicore_engine, sales_engine):
        df_legacy_orders_table = DataExtractor.extract_rds_table(
            aicore_engine, "orders_table"
        )

        df_legacy_orders_table = DataCleaner.clean_orders_table_df(
            df_legacy_orders_table
        )

        DatabaseConnector.df_upload_to_db(
            df_legacy_orders_table, "orders_table", sales_engine
        )

    def run():
        aicore_engine, sales_engine = Main.create_engines()
        table_names = DatabaseConnector.list_db_tables(sales_engine)

        function_table = {
            "dim_users": Main.create_dim_users,
            "dim_card_details": Main.create_dim_card_details,
            "dim_store_details": Main.create_dim_store_details,
            "products_table": Main.create_products_table,
            "orders_table": Main.create_orders_table,
        }

        for table, function in function_table.items():
            if table not in table_names:
                function(aicore_engine, sales_engine)


if __name__ == "__main__":
    Main.run()
