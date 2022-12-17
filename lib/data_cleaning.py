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

    def phone_number_clean(df):
        df["phone_number"] = df["phone_number"].apply(lambda x: x.str.strip("().x"))

        df = df.apply(
            lambda row: phonenumbers.format_number(
                phonenumbers.parse(row["phone_number"], row["country_code"]),
                phonenumbers.PhoneNumberFormat.INTERNATIONAL,
            ),
            axis=1,
        )

    def dob_clean(df):
        df["date_of_birth"] = pd.to_datetime(df["date_of_birth"]).dt.strftime(
            "%d %b %Y"
        )

    def clean_dataframe(df):

        # Filtering by country to remove bad data
        countries = ["Germany", "United Kingdom", "United States"]
        df_filtered = df.loc[df["country"].isin(countries)]
        df_phone_clean = DataCleaner.phone_number_clean(df_filtered)
        df_dob_clean = DataCleaner.dob_clean(df_phone_clean)
