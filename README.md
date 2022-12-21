# Multinational Retail Data Centralisation Project
## Milestone 1

As I started this project I wanted to do everything in Docker as I have used this tool a lot recently and know it is used ubiquitously throughout industry. 
I started by finding the Docker images for postgres and pgadmin4 and seeing if I could do what I wanted. After finding the images I coudld not work out why I couldn't access the pgadmin container via localhost:5000 or 5050 or any port I tried to set it to. In the end I managed to make it work by setting PGADMIN_LISTEN_ADDRESS=0.0.0.0 in the environment variables. I think the default was [::], which perhaps does not work on my OS Ubuntu.
I created a .env file for all the details adding PGADMIN_LISTEN_PORT=5050 and PGADMIN_LISTEN_ADDRESS=0.0.0.0 to the environment variables. This changed the access address from the default [::]:80 to 0.0.0.0:5050. Once I was connected I managed to connect to the postgres container by simply accessing the name of the container I had selected, a useful feature of Docker. 

```
PGADMIN_DEFAULT_EMAIL=cjq234@gmail.com
PGADMIN_DEFAULT_PASSWORD=pgpassword
POSTGRES_PASSWORD=pgpassword
PGADMIN_LISTEN_PORT=5050
PGADMIN_LISTEN_ADDRESS=0.0.0.0
```

I proceeded to set up the Docker Compose file and Dockerfile to boot the containers as I wanted with volumes for each. Next I added a third container for my python script, I will need to add more details to it as I work out which ports I will need to use. 

## Milestone 2

I created 3 python files for 3 classes of components of my pipeline. A data extractor, a data connector and a data cleaner. I started writing methods for each. I began by writing a method to load my database credentials from a yaml file. Then I created a method to instantiate my SQLAlchemy engine with the credentials from the previous method. 

```
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
For the data extractor module, I wrote a method which takes arguments of the table name and the sqlalchemy engine and runs a query to the database for this entire table (SELECT * FROM <table_name>)and converts it to a Pandas dataframe. This method is not available for SQLalchemy 2.0, so I am not using future=true in the sqlalchemy create_engine. This method seems insanely useful and I am not sure what they are replacing it with.

```
def df_extract_rds_table(engine, table_name):
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        return df
```

### Exploratory Data analysis

#### Null and Rubbish data

Connecting to the database with pgadmin allows me to use SQL queries to have a look at the legacy_users data and decide what cleaning steps are necessary. 

```
@sql
```
SELECT * FROM legacy_users
WHERE first_name = 'NULL' OR
last_name = 'NULL' OR
date_of_birth = 'NULL' OR
company = 'NULL' OR
email_address = null OR
address = 'NULL' or
country = 'NULL' OR
country_code = 'NULL' OR
phone_number = 'NULL' OR
join_date = 'NULL' OR
user_uuid = 'NULL';
```

shows that there are no rows with null in a single field, there are only entirely null rows. This means that I can remove those rows quite easily. 

@sql
```
SELECT * FROM legacy_users
WHERE  country NOT IN ('Germany', 'United Kingdom', 'United States');
```
The country column is the only column with fixed discrete answers. By filtering for all that don't match the exact spelling I can get another look.

This list was interesting because it showed no mispellings of the country names. It left only NULL and rubbish data. It also showed no entries where the country was NULL or rubbish and the other columns were fine. This indicates again that we are cleaning only complete rows of NULL or rubbish, not individual fields which would be more complicated. 

As there are so many rows, further exploration will have to be done with Pandas by loading the database into a dataframe.

#### Phone numbers

The phone numbers have all sorts of non-integer characters in them which need to be removed. By using regex I can use re.sub and the inverse character \D to remove all non-integers from the number. I used a python library called phonenumbers to parse and format the phone numbers, using the country_code as an argument to format them based on their country code. 

#### Dates

How to format the date of birth and join date columns is open to interpretation as it depends how we will need it for analysis. Having them in datetime formats is useful for calculation timespan from those dates which may be used for promotional offers, however if human legibility is preferable, then a string of dd MMM yyyy, eg 29 Dec 2022 is the least ambiguous internationally. I will leave it for now and if we need to change it later we can do so.

#### Data types

Aside from dates, the only entries which should not be strings are the country and country_codes which should be category type. By using pd.astype() I changed these as required.

#### N/A of any invalid data 

```
new_df["length_of_no"] = new_df.loc[:, "phone_number"].apply(len)

new_df["length_of_no"].value_counts().sort_index()

8        1
9        2
10      14
11     173
12    2439
13    9878
14      30
15    1021
16    1527
17     199
Name: length_of_no, dtype: int64
```