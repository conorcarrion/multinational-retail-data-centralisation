import datetime
import re
import phonenumbers
import pandas as pd
import tabula


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
        df.loc[:, "country"] = df.loc[:, "country"].astype("category")

        return df

    def df_clean_card_data(df):
        # drop first column (old index) and last column (all NaN)
        df = df.drop(df.columns[[0, 6]], axis=1)
        # drop all rows which are all NaN
        df.dropna(how="all", inplace=True)

        # identify rows that have been shifted (column 5 isnt null)
        mask = df[5].notnull()
        bad_rows = df[mask]

        def fix_rows(row):
            # explicit way to shift all rows to the left
            row[0] = row[1]
            row[1] = row[2]
            row[2] = row[3]
            row[3] = row[4]
            row[4] = row[5]
            row[5] = pd.isnull
            return row

        # apply the fix to each row in bad_rows
        fixed_bad_rows = bad_rows.apply(lambda x: fix_rows(x), axis=1)

        # update the original df with
        df.update(fixed_bad_rows)
        df = df.drop(df.columns[4], axis=1)
        df.columns = df.iloc[0]
        df = df.drop(1)

        df.loc[:, "date_payment_confirmed"] = df.loc[:, "date_payment_confirmed"].apply(
            DataCleaner.date_clean
        )

        return df
