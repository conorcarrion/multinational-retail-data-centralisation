import pandas as pd


@classmethod
class DataExtractor:
    def extract_from_csv():
        pass
    
    def extract_from_API():
        pass

    def extract_from_S3():
        pass

    def extract_rds_table(engine, table_name):
        # Create a connection to the database
        connection = engine.connect()
        # Execute a SELECT statement to retrieve the data
        result = connection.execute(f"SELECT * FROM {table_name}")
        # Fetch all the rows from the result set
        rows = result.fetchall()
        # Close the connection
        connection.close()
        # Convert the rows to a list of dictionaries
        data = [dict(row) for row in rows]
        return data

    def df_extract_rds_table(engine, table_name):
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        return df

        