import os
import csv
import requests
import tabula
import pandas as pd
import boto3
from botocore import UNSIGNED
from botocore.client import Config


class DataExtractor:
    def extract_from_public_s3(bucket, key):
        # extracts specified csv from specified bucket with unsigned public client
        s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        response = s3.get_object(Bucket=bucket, Key=key)

        df = pd.read_csv(response.get("Body"))
        return df

    def API_list_number_of_stores(endpoint, headers):
        # returns the number of stores from prebuilt API
        r = requests.get(endpoint, headers=headers)
        return r.json()["number_stores"]

    def extract_rds_table(engine, table_name):
        # loads an RDS table into a dataframe using SQL
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        return df

    def retrieve_store_data(endpoint, headers, store_number):
        # pulls the details for the store number specified in the function.
        r = requests.get(
            f"https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/{store_number}",
            headers=headers,
        )

        return r.json()

    def retrieve_stores_data(endpoint, headers, number_of_stores):
        # use the retrieve store data function and append all the data into a list, then make a dataframe-

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
        # takes a webpage link to a pdf and uses the tabula library to concatenate the table on each page into a dataframe
        df = tabula.read_pdf(link, pages="all", pandas_options={"header": None})
        df = pd.concat(df, ignore_index=True)
        return df

    def extract_json_data(link):
        df = pd.read_json(link)
        return df
