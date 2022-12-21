import os
import csv
import tabula
import pandas as pd


class DataExtractor:
    def extract_from_csv():
        pass

    def extract_from_API():
        pass

    def extract_from_S3():
        pass

    def df_extract_rds_table(engine, table_name):
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        return df

    def write_data_to_csv(df, directory):
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        df.to_csv(os.path.join(directory, "data.csv"))

    def retrieve_pdf_data(link):
        df = tabula.read_pdf(link, pages="all", pandas_options={"header": None})
        df = pd.concat(df, ignore_index=True)
        return df
