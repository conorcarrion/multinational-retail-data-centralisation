import datetime
import re
import phonenumbers
import pandas as pd
import tabula


class DataCleaner:
    def df_remove_bad_countries(df):
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
        date = pd.to_datetime(date, errors="raise")
        date = date.strftime("%d %b %Y")
        return date

    def integer_purify(n):
        x = re.sub(r"\D", "", n)
        return x

    def clean_users_df(df):

        # Remove NULL and bad data rows
        df = DataCleaner.df_remove_bad_countries(df)

        # formatting the phone number based on country code
        df = DataCleaner.df_phone_number_clean(df)

        # formatting the date to unambiguous xx NNN xxxx, eg 18 Dec 2022

        df.loc[:, "date_of_birth"] = df.loc[:, "date_of_birth"].apply(
            DataCleaner.date_clean
        )
        df.loc[:, "join_date"] = df.loc[:, "join_date"].apply(DataCleaner.date_clean)

        # changing data types to appropriate type
        df["country_code"] = df["country_code"].astype("category")
        df["country"] = df["country"].astype("category")

        return df

    def clean_card_details_df(df):

        # drop all rows and columns which are all NaN
        df.dropna(how="all", inplace=True, axis=1)
        df.dropna(how="all", inplace=True, axis=0)

        # column 0 and column 5 not dropped so may still contain important information
        # first row is the headers, column 0 and 5 renamed for convenience before
        # setting the column headers to that row, then dropping it.

        df.columns = [
            "data_0",
            "card_number",
            "expiry_date",
            "card_provider",
            "date_payment_confirmed",
            "data_5",
        ]
        # drop column headers from dataframe row 1
        df = df.drop(1)

        # identify rows that have been shifted (column 5 isnt null)
        mask = df["data_5"].notnull()
        bad_rows = df[mask]

        # data_0                                 NaN
        # card_number                           53.0
        # expiry_date               4131871381315066
        # card_provider                        03/27
        # date_payment_confirmed       VISA 16 digit
        # data_5                          2007-07-30
        # Name: 56, dtype: object

        def fix_shifted_rows(row):
            # explicit way to shift all rows to the left
            row["data_0"] = row["card_number"]
            row["card_number"] = row["expiry_date"]
            row["expiry_date"] = row["card_provider"]
            row["card_provider"] = row["date_payment_confirmed"]
            row["date_payment_confirmed"] = row["data_5"]
            return row

        # apply the fix to each row in bad_rows
        fixed_shifted_rows = bad_rows.apply(fix_shifted_rows, axis=1)

        # update the original df with
        df.update(fixed_shifted_rows)

        # NA all the data_5 rows which have been shifted
        # row["data_5"] = pd.NA does not work as the update does not apply

        df.loc[df["date_payment_confirmed"] == df["data_5"], "data_5"] = pd.NA

        # drop column data_5 if all null
        df.dropna(how="all", inplace=True, axis=1)

        # A bunch of rows have the card number under data_0 and everything else under card_number:
        # "4371"  "4393 3590914465383794"	"10/30 JCB 16 digit 1998-03-18"	NaN	NaN	NaN

        # Can isolate these by finding rows containing NaN
        # Create a Boolean mask indicating which rows contain NaN values
        mask = df.isnull()

        # Use the any() method to check if any value in the row is True
        mask = mask.any(axis=1)

        # Select the rows where the mask is True
        combined_rows = df.loc[mask]

        def fix_combined_rows(row):
            # split the combined row into parts
            x = row["card_number"].split(" ")

            # assign each part to the right row
            row["expiry_date"] = x[0]
            row["date_payment_confirmed"] = x[-1]
            row["card_number"] = row["data_0"]

            # recombine the remainder for the card_provider
            row["card_provider"] = " ".join(x[1:-1])
            row["data_0"] = pd.NA
            return row

        fixed_combined_rows = combined_rows.apply(fix_combined_rows, axis=1)
        df.update(fixed_combined_rows)

        df["card_provider"] = df["card_provider"].astype("category")

        # remove rubbish rows via card_provide category
        legit_card_providers = [
            "Diners Club / Carte Blanche",
            "American Express",
            "JCB 16 digit",
            "JCB 15 digit",
            "Maestro",
            "Mastercard",
            "Discover",
            "VISA 16 digit",
            "VISA 19 digit",
            "VISA 13 digit",
        ]

        df = df.loc[df["card_provider"].isin(legit_card_providers)]

        df.loc[:, "date_payment_confirmed"] = df.loc[:, "date_payment_confirmed"].apply(
            DataCleaner.date_clean
        )

        df.drop(columns="data_0", inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df

    def clean_store_details_df(df):
        # remove all null rows
        df.dropna(how="all", inplace=True, axis=1)

        # lat and index column has no information
        df.drop(columns="lat", inplace=True)
        df.drop(columns="index", inplace=True)

        # removing bad rows by selecting only country codes that apply
        legit_country_codes = [None, "GB", "DE", "US"]

        df = df.loc[df["country_code"].isin(legit_country_codes)]

        # moving the latitude column next to the longitude
        latitude = df.pop("latitude")
        df.insert(3, "latitude", latitude)

        # moving the store_code column to far left
        col_move = df.pop("store_code")
        df.insert(0, "store_code", col_move)

        # changing webstore na entries to pd.NA
        df.loc[
            0,
            [
                "address",
                "longitude",
                "latitude",
                "locality",
                "country_code",
                "continent",
            ],
        ] = pd.NA

        x = df.loc[:, "staff_numbers"].apply(DataCleaner.integer_purify)
        df.update(x)

        df.loc[df["continent"] == "eeEurope", "continent"] = "Europe"
        df.loc[df["continent"] == "eeAmerica", "continent"] = "America"

        df["continent"] = df["continent"].astype("category")
        df["country_code"] = df["country_code"].astype("category")
        df["store_type"] = df["store_type"].astype("category")
        df["staff_numbers"] = df["staff_numbers"].astype("int64")
        return df

    def clean_orders_table_df(df):
        df.drop(columns="1", inplace=True)
        df.drop(columns="first_name", inplace=True)
        df.drop(columns="last_name", inplace=True)
        return df

    def clean_products_table_df(df):

        # from df["category"].unique()
        legit_category = [
            "toys-and-games",
            "sports-and-leisure",
            "pets",
            "homeware",
            "health-and-beauty",
            "food-and-drink",
            "diy",
        ]
        mask = df["category"].isin(legit_category)

        # by viewing df[~mask] can look at bad rows and confirm they can be dropped
        df = df[mask]

        # spelling and formatting
        df.loc[df["removed"] == "Still_avaliable", "removed"] = "Available"

        # price column clean
        df.loc[:, "product_price"] = (
            df["product_price"].str.replace("£", "").astype(float)
        )

        # drop Unnamed and reset index
        df.drop(columns="Unnamed: 0", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # see weight_clean function for changes.

        df[["units_in_product", "unit_weight", "product_weight"]] = pd.DataFrame(
            df["weight"].apply(DataCleaner.product_weight_clean).tolist(),
            columns=["units_in_product", "unit_weight", "product_weight"],
        )

        # reorganise columns
        df = df.reindex(
            columns=[
                "product_name",
                "product_code",
                "product_price",
                "category",
                "EAN",
                "date_added",
                "uuid",
                "units_in_product",
                "unit_weight",
                "product_weight",
                "removed",
            ]
        )

        return df

    def product_weight_clean(x):

        # "5 x 120g"
        if "x" in x:
            unit, weight = x.split(" x ")
            unit_weight = weight.rstrip("g")
            unit = int(unit)
            unit_weight = float(unit_weight)
            product_weight = unit * unit_weight
            return [unit, unit_weight, product_weight]

        # "1.6kg"
        elif "k" in x:
            x = x.rstrip("kg")
            x = float(x)
            return [1, x, x]

        # "200ml"
        elif "ml" in x:
            x = x.rstrip("ml")
            x = float(x)
            return [1, x, x]

        # 1 value has "77g ." thanks blair
        elif "g ." in x:
            x = x.rstrip("g .")
            x = float(x)
            x = x / 1000
            return [1, x, x]

        # 200g
        elif "g" in x:
            x = x.rstrip("g")
            x = float(x)
            x = x / 1000
            return [1, x, x]

        # 16oz
        elif "oz" in x:
            x = x.rstrip("oz")
            x = float(x)
            x = 28.3495 * x  # conversion from oz to g
            x = round(x, 4)
            return [1, x, x]
