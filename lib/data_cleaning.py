import datetime
import re
import phonenumbers
import pandas as pd
from phonenumbers import NumberParseException


class DataCleaner:
    def clean_csv_data():
        pass

    def clean_api_data():
        pass

    def clean_s3_data():
        pass

    def df_phone_number_clean(df):
        df.loc[:, "phone_number"].apply(lambda x: re.sub(r"[x.()]", "", x).lstrip("00"))

        def reformat_phone_number(row):
            try:
                phonenumbers.format_number(
                    (phonenumbers.parse(row["phone_number"], row["country_code"])),
                    phonenumbers.PhoneNumberFormat.INTERNATIONAL,
                )
            except NumberParseException as e:
                repr(e)

        new_df = df.apply(lambda row: reformat_phone_number(row), axis=1)
        df.head(5)
        return new_df

    def df_clean_user_data(df):

        # Filtering by country to remove bad rows
        countries = ["Germany", "United Kingdom", "United States"]
        df = df.loc[df["country"].isin(countries)]

        # Update rows with country_code GBB to GB
        ggb = df["country_code"] == "GGB"
        df.loc[ggb, "country_code"] = "GB"

        # formatting the phone number based on country code
        df = DataCleaner.df_phone_number_clean(df)

        # formatting the date to unambiguous xx NNN xxxx, eg 18 Dec 2022

        df["date_of_birth"] = pd.to_datetime(
            df["date_of_birth"], format=("%d %b %Y"), errors="raise"
        )

        return df
