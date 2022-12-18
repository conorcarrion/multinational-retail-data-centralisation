import datetime
import phonenumbers
import pandas as pd


class DataCleaner:
    def clean_csv_data():
        pass

    def clean_api_data():
        pass

    def clean_s3_data():
        pass

    def df_phone_number_clean(df):
        df["phone_number"] = df["phone_number"].apply(lambda x: x.str.strip("().x"))

        df = df.apply(
            lambda row: phonenumbers.format_number(
                phonenumbers.parse(row["phone_number"], row["country_code"]),
                phonenumbers.PhoneNumberFormat.INTERNATIONAL,
            ),
            axis=1,
        )

    def df_date_clean(df, column):
        df[f"{column}"] = pd.to_datetime(df[f"{column}"]).dt.strftime("%d %b %Y")

    def df_clean_user_data(df):

        # Filtering by country to remove bad rows
        countries = ["Germany", "United Kingdom", "United States"]
        df_filtered = df.loc[df["country"].isin(countries)]

        # formatting the phone number based on country code
        df_phone_clean = DataCleaner.phone_number_clean(df_filtered)

        # formatting the date to unambiguous xx NNN xxxx, eg 18 Dec 2022
        df_dob_clean = DataCleaner.date_clean(df_phone_clean, "date_of_birth")
        df_join_date_clean = DataCleaner.date_clean(df_dob_clean, "join_date")
