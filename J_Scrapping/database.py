import pandas as pd
import json
import mysql.connector
from mysql.connector import errorcode

def get_db_connection(host, user, password, database):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        allow_local_infile=True 
    )

def create_table(cursor, table_name):
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ("
                   "link TEXT, price TEXT, code TEXT, `Fabric Type` TEXT, Neckline TEXT, Collection TEXT,"
                   "Trouser TEXT, Sleeves TEXT, Embellishment TEXT, Color TEXT, Size TEXT, Shirt TEXT,"
                   "Dupatta TEXT);")
    if cursor:
        print(f"Table {table_name} created successfully.")
    else:
        print(f"Error creating table {table_name}.")

def load_data(cursor, table_name, df):
    # Load the CSV file into a DataFrame
    
    
    # Normalize the DataFrame's column names to lowercase for matching
    df.columns = df.columns.str.lower()
    
    # Define the required columns with their correct names
    required_columns = {
        'link': 'link',
        'price': 'price',
        'code': 'code',
        'fabric type': '`Fabric Type`',
        'neckline': 'Neckline',
        'collection': 'Collection',
        'trouser': 'Trouser',
        'sleeves': 'Sleeves',
        'embellishment': 'Embellishment',
        'color': 'Color',
        'size': 'Size',
        'shirt': 'Shirt',
        'dupatta': 'Dupatta'
    }

    # Create a new DataFrame with only the required columns
    # Map the normalized column names to the original case-sensitive names
    new_df = pd.DataFrame({required_columns[key]: df.get(key, pd.Series([None]*len(df))) for key in required_columns.keys()})

    # Insert the new DataFrame into the SQL table
    for _, row in new_df.iterrows():
        placeholders = ', '.join(['%s'] * len(required_columns))
        sql_query = f"""
        INSERT INTO {table_name} 
        ({', '.join(required_columns.values())})
        VALUES ({placeholders})
        """

        # Execute the SQL query with the row data
        cursor.execute(sql_query, tuple(row))

    # Check if data was inserted successfully
    if cursor.rowcount > 0:
        print(f"Data loaded successfully into table {table_name}.")
    else:
        print(f"Error loading data into table {table_name}.")

def add_fulltext_index(cursor, table_name):
    cursor.execute(f"ALTER TABLE {table_name} "
                   f"ADD FULLTEXT(link, `Fabric Type`, Neckline, Collection, Trouser, Sleeves, Embellishment, Color, Shirt, Dupatta);")
    if cursor:
        print(f"Fulltext index added successfully to table {table_name}.")
    else:
        print(f"Error adding fulltext index to table {table_name}.")



