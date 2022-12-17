# Multinational Retail Data Centralisation Project
### Milestone 1

As I started this project I wanted to do everything in Docker as I have used this tool a lot recently and use it instead of conda environments. 
I started by finding the images for postgres and pgadmin4 and seeing if I could indeed do it all with containers. I spent about 30 minutes working out why I couldn't access the pgadmin container via localhost:5000 or 5050 or any port I tried to set it to. In the end I managed to google enough things to get it to stick. 
I created a .env file for all the details. I believe it was adding PGADMIN_LISTEN_PORT=5050 and PGADMIN_LISTEN_ADDRESS=0.0.0.0 to the environment variables via the .env file that allowed me to change the access address from the default [::]:80 to 0.0.0.0:5050. Once I was connected I managed to connect to the postgres container by simply accessing the name of the container I had selected. Very nice.

I proceeded to set up the Docker Compose file and Dockerfile to boot the containers as I wanted with volumes for each. Next I added a third container for my python script, I will need to add more details to it as I work out which ports I will need to use. 

### Milestone 2

I created 3 python files for 3 classes of components of my pipeline. A data extractor, a data connector and a data cleaner. I started writing methods for each. I began by writing a method to load my database credentials from a yaml file. Then I created a method to instantiate my SQLAlchemy engine with the credentials from the previous method. Then I wrote a method to list the tables available from the connected database. 

For the data extractor module, I wrote a method which could take a table name and using the sqlalchemy engine, query the database for this entire table and convert it to a python dictionary. I also added another method which did the same thing but as a Pandas dataframe.

#### Exploratory Data visualisation

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

