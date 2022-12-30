import os
import csv
import requests
import tabula
import pandas as pd


class DataExtractor:
    def extract_from_csv():
        pass

    def API_list_number_of_stores(endpoint, headers):
        r = requests.get(endpoint, headers=headers)
        return r.json()["number_stores"]

    def extract_rds_table(engine, table_name):
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        return df

    def retrieve_store_data(endpoint, headers, store_number):

        r = requests.get(
            f"https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/{store_number}",
            headers=headers,
        )

        return r.json()

    def retrieve_stores_data(endpoint, headers, number_of_stores):
        store_data = []
        for store_number in range(number_of_stores):
            request_data = DataExtractor.retrieve_store_data(
                endpoint, headers, store_number
            )
            store_data.append(request_data)

        df = pd.DataFrame(store_data)
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
