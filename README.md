# Multinational Retail Data Centralisation Project
## Milestone 1

As I started this project I wanted to do everything in Docker as I have used this tool a lot recently and know it is used ubiquitously throughout industry. 
I started by finding the Docker images for postgres and pgadmin4 and seeing if I could do what I wanted. After finding the images and running a docker compose, I couldn't access the pgadmin container via localhost:5000 or any port I tried to set it to. In the end I managed to make it work by setting PGADMIN_LISTEN_ADDRESS=0.0.0.0 in the environment variables. I think the default was [::], which perhaps does not work on my OS, Ubuntu.
I created a .env file for all the details adding PGADMIN_LISTEN_PORT=5050 and PGADMIN_LISTEN_ADDRESS=0.0.0.0 to the environment variables. This changed the access address from the default [::]:80 to 0.0.0.0:5050. Once I was connected I managed to connect to the postgres container by simply accessing the name of the container I had selected, a useful feature of Docker. 

```
PGADMIN_DEFAULT_EMAIL=cjq234@gmail.com
PGADMIN_DEFAULT_PASSWORD=pgpassword
PGADMIN_LISTEN_PORT=5050
PGADMIN_LISTEN_ADDRESS=0.0.0.0
POSTGRES_USER=postgres
POSTGRES_PASSWORD=pgpassword
```

I proceeded to set up the Docker Compose file and Dockerfile to boot the containers as I wanted with volumes for each. Next I added a third container for my python script, I will need to add more details to it as I work out which ports I will need to use. 

## Milestone 2

I created 3 python files for 3 classes of components of my pipeline. A data extractor, a data connector and a data cleaner. I started writing methods for each. I began by writing a method to load my database credentials from a yaml file. Then I created a method to instantiate my SQLAlchemy engine with the credentials from the previous method. 

*read_db_creds later renamed load_yaml as used for different tasks. Credentials added as an argument for init_db_engine allowing multiple engines from different credentials.

```python
    def read_db_creds():
        with open("config/db_creds.yaml", "r") as outfile:
            # Load the contents of the file as a dictionary
            credentials = yaml.safe_load(outfile)
            return credentials

    def init_db_engine():
        credentials = DatabaseConnector.read_db_creds()
        sqlalchemy_url = sqlalchemy.engine.URL.create(
            "postgresql",
            username=credentials["RDS_USER"],
            password=credentials["RDS_PASSWORD"],
            host=credentials["RDS_HOST"],
            port=credentials["RDS_PORT"],
            database=credentials["RDS_DATABASE"],
        )
        engine = create_engine(sqlalchemy_url)
        return engine

```
For the data extractor module, I wrote a method which, with arguments of the table name and the sqlalchemy engine, runs a query to the database for the entire table provided (SELECT * FROM <table_name>)and converts it to a Pandas dataframe. This method is not available for SQLalchemy 2.0, so I removed argument future=true in the sqlalchemy create_engine method which I had taken from the documentation.

```python
def df_extract_rds_table(engine, table_name):
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        return df
```

### Data Cleaning

For the sake of learning, I used a combination of different tools to explore, clean and format the tables. Sometimes I used pandas and sometimes I used pgadmin and SQL queries, sometimes both. What I did is not a recommendation for a pipeline, but merely to show my ability to use both. 

I had 6 datasets to explore, clean and reformat before uploading them to my postgres database for analysis: User info, credit card details, datetime events, product info, store details and finally the orders table which would be the centre table linking to the others in a star schema. 

#### User details table

As the user details data was in an AWS RDS server, I could connect to it directly with pgadmin. This allowed me to use SQL queries to have a look at the legacy_users data and decide what cleaning steps are necessary. 


```sql
SELECT * FROM legacy_users
WHERE first_name = 'NULL' OR
last_name = 'NULL' OR
date_of_birth = 'NULL' OR
company = 'NULL' OR
email_address = 'NULL' OR
address = 'NULL' OR
country = 'NULL' OR
country_code = 'NULL' OR
phone_number = 'NULL' OR
join_date = 'NULL' OR
user_uuid = 'NULL';
```

The above SQL query showed that there are no rows with null in a single field, there are only entirely null rows. I can safely remove those rows. To isolate those rows, I can use a column with discrete values with low number of unique options:


```sql
SELECT * FROM legacy_users
WHERE country NOT IN ('Germany', 'United Kingdom', 'United States');
```

This query was interesting because it left only NULL and rubbish data. It also showed no entries where the country was NULL or rubbish and the other columns were fine. This indicates again that we are cleaning only complete rows of NULL or rubbish, not individual fields which would be more complicated. 

Further exploration will be done with Pandas by loading the database into a dataframe.

##### Phone numbers
The phone numbers had all sorts of non-integer characters in them which needed to be removed. By using regex I used re.sub and the inverse character \D to remove all non-integers from the number (D is integers in regex). I used a python library called phonenumbers to parse and format the phone numbers, using the country_code as an argument to format them based on their country code. 

##### Dates
How to format date columns is open to interpretation as it depends what sort of analytical queries we might want to run. Having them in datetime formats is useful for the calculation of timespan from those dates, say for promotional offers, however if human legibility is preferable, then a string of dd MMM yyyy, eg 29 Dec 2022 is the least ambiguous internationally. 

##### Data types and N/A of any invalid data 
Aside from dates, the only entries which should not be strings are the country and country_codes which should be category type. By using pd.astype() I changed these as required.



### Card Details table

#### Pdf file

The card details came from a pdf file. To parse this information I used Tabula, a library for java which can read pdfs. To use it within python there is the tabula-py library. In order to use this I had to change my docker image for my app to one which has both java and python installed. I found this in Docker hub. 

#### Starting data

df.head()

|    |   0 | 1                | 2           | 3                           | 4                      |   5 |   6 |
|---:|----:|:-----------------|:------------|:----------------------------|:-----------------------|----:|----:|
|  0 | nan | nan              | nan         | nan                         | nan                    | nan | nan |
|  1 | nan | card_number      | expiry_date | card_provider               | date_payment_confirmed | nan | nan |
|  2 |   0 | 30060773296197   | 09/26       | Diners Club / Carte Blanche | 2015-11-25             | nan | nan |
|  3 |   1 | 349624180933183  | 10/23       | American Express            | 2001-06-18             | nan | nan |
|  4 |   2 | 3529023891650499 | 06/23       | JCB 16 digit                | 2000-12-26             | nan | nan |

As we can see, there are a few issues to fix. I started by using df.dropna() to drop any rows or columns which were completely null. 

This dropped row 6 but not row 5, indicating there might be some data in row 5. 

I initially used a technique to set the second row with the column headers as the column headers, however this caused the nan entries to be added to the index column, which seemed peculiar. Instead I manually entered the column headers with df.columns = [] and dropped the headers row. I named the assorted columns data_0 and data_5 just for ease of accessing whilst cleaning.

I wanted to inspect row 5, so I made a mask using df["data_5].notnull() which returns true for all rows which are not null. By then using df[mask] I can get all those rows. 

The only one was row 56:
```
# data_0                                 NaN
# card_number                           53.0
# expiry_date               4131871381315066
# card_provider                        03/27
# date_payment_confirmed       VISA 16 digit
# data_5                          2007-07-30
# Name: 56, dtype: object
```

The row has been shifted to the right. Rather than simply fix the row, I wrote a function which moves all the data to the right place, as in industry it might be required in the future for further batches of data. 

Next I checked for any remaining rows where 1 or more entries were null. Similar to previous technique, I used a mask of `df.null()`, `mask.any(axis=1)` and finally `df.loc[mask]` to view any rows containing 1 or more null values. 

This revealed a block of rows where the card information was not entered correctly. The card number was in the data_0 column, and the rest of the information was concatenated in the card_number column. I wrote a function to fix this, then used `.apply()` and `.update()` to correct the original dataframe.

Finally I used the discrete category of the card_provider to find all the unique card_provider entries with `df["card_provider"].unique()`. By manually creating from this list the legit card provider list, I then used `df.loc[~df["card_provider].isin(legit_card_providers)]` to reveal a lot of bad rows with nonsense information. I could then drop these by:
```python
df = df.loc[df["card_provider"].isin(legit_card_providers)]
```

I then used the previously used date clean function to clean the date_payment_confirmed column to a legible format. 

Finally I used:

```python
df.drop(columns="data_0", inplace=True)
df.reset_index(drop=True, inplace=True)
```

to drop the data_0 column and reset the index given all our removed rows.



### Dim Store Details clean up 

   index                                            address longitude   lat  \
0      0                                                N/A       N/A   N/A   
1      1  Flat 72W\nSally isle\nEast Deantown\nE7B 8EB, ...  51.62907  None   
2      2        Heckerstraße 4/5\n50491 Säckingen, Landshut  48.52961  None   
3      3  5 Harrison tunnel\nSouth Lydia\nWC9 2BE, Westbury     51.26  None   
4      4  Studio 6\nStephen landing\nSouth Simon\nB77 2W...   53.0233  None   

       locality    store_code staff_numbers opening_date   store_type  \
0           N/A  WEB-1388012W           325   2010-06-12   Web Portal   
1  High Wycombe   HI-9B97EE4E            34   1996-10-25        Local   
2      Landshut   LA-0772C7B9            92   2013-04-12  Super Store   
3      Westbury   WE-1DE82CEE            69   2014-01-02  Super Store   
4        Belper   BE-18074576            35   2019-09-09        Local   

   latitude country_code continent  
0      None         None      None  
1  -0.74934           GB    Europe  
2  12.16179           DE    Europe  
3   -2.1875           GB    Europe  
4  -1.48119           GB    Europe  

`df2["lat"].unique()`:
`array(['N/A', None, '13KJZ890JH', '2XE1OWOC23', 'NULL', 'OXVE5QR07O',
       'VKA5I8H32X', 'LACCWDI0SB', 'A3O5CBWAMD', 'UXMWDMX1LC'],
      dtype=object)`
Since it had no useful information, the column was dropped.


df2["country_code"].unique() gives: 
`array([None, 'GB', 'DE', 'US', 'YELVM536YT', 'FP8DLXQVGH', 'NULL',
       'HMHIFNLOBN', 'F3AO8V2LHU', 'OH20I92LX3', 'OYVW925ZL8',
       'B3EH2ZGQAV'], dtype=object)`

If we can cut the 'all' null rows, then fix the 'any' null rows, we can use GB/DE/US to cut any unwanted bad data rows.

```python
mask = df2.isnull()
mask = mask.any(axis=1)
any_null_rows = df2.loc[mask]
```
reveals that the only row which has some null entries are store 0, the webstore. This means we can keep rows with `country_code is in [None, GB, DE, and US]` and this will remove the bad rows. We can check by making a mask of the inverse to see the rubbish lines.

```python
# moving the latitude column next to the longitude
        latitude = df.pop("latitude")
        df.insert(3, "latitude", latitude)

        # moving the store_code column to far left
        col_move = df.pop("store_code")
        df.insert(0, "store_code", col_move)
```

`df2["continent"].unique()` shows:
`array([None, 'Europe', 'America', 'eeEurope', 'eeAmerica'], dtype=object)`

T

`df2["store_type"].unique()`
`array(['Web Portal', 'Local', 'Super Store', 'Mall Kiosk', 'Outlet'],
      dtype=object)`

      looks fine

It makes more sense to have longitude and latitude next to each other, although they also seem like useless information but we will see what is required from the data. 

The store code also seems like it should be the first column. 

The index column has no rogue data in it, so can be dropped.

the first row for the webstore can have pd.NA for all the N/A values for consistency. 

### Products

By using boto3 I imported a csv in an s3 bucket into a pandas dataframe. First by creating the boto3 client and then by using s3.get_object to create a response from the server. Then using pd.read_csv on the body of the response. 

The data looks like this:

"|    |   Unnamed: 0 | product_name                                | product_price   | weight   | category       |           EAN | date_added   | uuid                                 | removed         | product_code   |\n|---:|-------------:|:--------------------------------------------|:----------------|:---------|:---------------|--------------:|:-------------|:-------------------------------------|:----------------|:---------------|\n|  0 |            0 | FurReal Dazzlin' Dimples My Playful Dolphin | £39.99          | 1.6kg    | toys-and-games | 7425710935115 | 2005-12-02   | 83dc0a69-f96f-4c34-bcb7-928acae19a94 | Still_avaliable | R7-3126933h    |\n|  1 |            1 | Tiffany's World Day Out At The Park         | £12.99          | 0.48kg   | toys-and-games |  487128731892 | 2006-01-09   | 712254d7-aea7-4310-aff8-8bcdd0aec7ff | Still_avaliable | C2-7287916l    |\n|  2 |            2 | Tiffany's World Pups Picnic Playset         | £7.00           | 590g     | toys-and-games | 1945816904649 | 1997-03-29   | b089ef6f-b628-4e37-811d-fffe0102ba64 | Still_avaliable | S7-1175877v    |\n|  3 |            3 | Tiffany's World Wildlife Park Adventures    | £12.99          | 540g     | toys-and-games | 1569790890899 | 2013-03-20   | d55de422-8b98-47d6-9991-e4bc4c5c0cb0 | Removed         | D8-8421505n    |\n|  4 |            4 | Cosatto Cosy Dolls Pram                     | £30.00          | 1.91kg   | toys-and-games | 7142740213920 | 2007-12-23   | 7945b657-cb02-4cc5-96cf-f65ed0a8f235 | Still_avaliable | B6-2596063a    |"

Removing bad or nan rows via discrete category:

```
# reveal all the categories
df["category"].unique()

# cut out any bad categories
legit_category = ['toys-and-games', 'sports-and-leisure', 'pets', 'homeware','health-and-beauty',
       'food-and-drink', 'diy']

# create a mask
mask = df["category"].isin(legit_category)

# checking this first to see bad rows (~ inverse mask)
df[~mask]

# making df equal to df without those rows
df = df[mask]
```




### Orders

by checking if the product_quantity and index columns can be converted to integers with coerce, then checking for any null values (coerce changes non integers to NaN), I ascertained that there are no rows with rubbish data.





