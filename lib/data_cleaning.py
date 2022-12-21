import datetime
import re
import phonenumbers
import pandas as pd


class DataCleaner:
    def clean_csv_data():
        pass

    def clean_api_data():
        pass

    def clean_s3_data():
        pass

    def df_remove_bad_data(df):
        # Filtering by country to remove bad rows
        countries = ["Germany", "United Kingdom", "United States"]
        df = df.loc[df["country"].isin(countries)]

        # Update rows with country_code GBB to GB
        ggb = df["country_code"] == "GGB"
        df.loc[ggb, "country_code"] = "GB"

        return df

    def df_phone_number_clean(df):
        def reformat_phone_number(phone_number, country_code):

            formatted_phone_number = phonenumbers.format_number(
                (phonenumbers.parse(phone_number, country_code)),
                phonenumbers.PhoneNumberFormat.E164,
            )
            return formatted_phone_number

        def stripper(number):
            number = re.sub("\D", "", number)
            number = number.lstrip("00")
            return number

        df.loc[:, "phone_number"] = df["phone_number"].apply(stripper)
        df.loc[:, "phone_number"] = df.apply(
            lambda row: reformat_phone_number(row["phone_number"], row["country_code"]),
            axis=1,
        )

        return df

    def date_clean(date):
        date = pd.to_datetime(date, errors="coerce")
        date = date.strftime("%d %b %Y")
        return date

    def df_clean_user_data(df):

        # Remove NULL and bad data rows
        df = DataCleaner.df_remove_bad_data(df)

        # formatting the phone number based on country code
        df = DataCleaner.df_phone_number_clean(df)

        # formatting the date to unambiguous xx NNN xxxx, eg 18 Dec 2022

        df.loc[:, "date_of_birth"] = df.loc[:, "date_of_birth"].apply(
            DataCleaner.date_clean
        )
        df.loc[:, "join_date"] = df.loc[:, "join_date"].apply(DataCleaner.date_clean)

        # changing data types to appropriate type
        df.loc[:, "country_code"] = df.loc[:, "country_code"].astype("category")

        return df
