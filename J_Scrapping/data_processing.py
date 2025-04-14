import pandas as pd
import numpy as np
import re

def extract_features(description):

    features = {
        'Fabric Type': np.nan,
        'Neckline': np.nan,
        'Collection': np.nan,
        'Shirt Front': np.nan,
        'Shirt Back': np.nan,
        'Shirt Length': np.nan,
        'Trouser': np.nan,
        'Trouser Length': np.nan,
        'Sleeves': np.nan,
        'Sleeve Length': np.nan,
        'Style Cut': np.nan,
        'Length': np.nan,
        'Embellishment': np.nan,
        'Dupatta Length': np.nan,
        'Type': np.nan,
        'Wear Type': np.nan
    }
    
    if pd.isna(description):
        return features
    
    # Split the description by new lines, comma, hyphen, forward slash
    lines = re.split(r"[-,\n\t/]", description)
    lines = [line for line in lines if '*' not in line]

    # /*
    # for line in lines:
    #     for kw in kw_list:
    #         if kw in line.lower():
    #             features[kw] = line.split(':', 1)[1].strip
    # */
    

    for line in lines:
        if 'fabric type:' in line.lower():
            features['Fabric Type'] = line.split(':', 1)[1].strip()
        elif 'neckline:' in line.lower():
            features['Neckline'] = line.split(':', 1)[1].strip()
        elif 'collection:' in line.lower():
            features['Collection'] = line.split(':', 1)[1].strip()
        elif 'dupatta length:' in line.lower():
            features['Dupatta Length'] = line.split(':', 1)[1].strip()
        elif 'shirt length:' in line.lower():
            features['Shirt Length'] = line.split(':', 1)[1].strip()
        elif 'trouser length:' in line.lower():
            features['Trouser Length'] = line.split(':', 1)[1].strip()
        elif 'sleeve length:' in line.lower():
            features['Sleeve Length'] = line.split(':', 1)[1].strip()
        elif 'type:' in line.lower():
            features['Type'] = line.split(':', 1)[1].strip()
        elif 'shirt front:' in line.lower():
            features['Shirt Front'] = line.split(':', 1)[1].strip()
        elif 'shirt back:' in line.lower():
            features['Shirt Back'] = line.split(':', 1)[1].strip()
        elif 'trouser:' in line.lower():
            features['Trouser'] = line.split(':', 1)[1].strip()
        elif 'sleeves:' in line.lower():
            features['Sleeves'] = line.split(':', 1)[1].strip()
        elif 'style cut:' in line.lower():
            features['Style Cut'] = line.split(':', 1)[1].strip()
        elif 'length:' in line.lower():
            features['Length'] = line.split(':', 1)[1].strip()
        elif 'embellishment:' in line.lower():
            features['Embellishment'] = line.split(':', 1)[1].strip()
        elif 'wear type:' in line.lower():
            features['Wear Type'] = line.split(':', 1)[1].strip()    
    return features

# Function to extract key-value pairs from the 'More info' column
def extract_more_info(more_info):
    features = {}
    if pd.isna(more_info):
        return features
    
    # Convert the string representation of the list to an actual list of dictionaries
    more_info_list = eval(more_info)
    
    for info in more_info_list:
        # Split the key and value
        if ':' in info:
            key, value = info.split(':', 1)
            key = key.strip()
            value = value.strip()
            features[key] = value
    return features

# Function to remove the color from the name
def remove_color_from_name(row):
    color = row['Color']
    name = row['Name']
    return name.replace(color, '').strip()

def remove_category_from_name(row):
    categories = row['Product Category'].split() # Split Product Category into words
    name = row['Name']
    for category in categories:
        name = name.replace(category, '').strip()  # Remove each category word from the name
    # Clean up any extra spaces left by the replacements
    name = ' '.join(name.split())
    return name

def data_processing(df):
    print("Starting data processing...")

    # Apply the extraction function to each row in the dataframe
    print("Extracting features from the 'Description' column...")
    features_df = df['Description'].apply(extract_features).apply(pd.Series)
    df = df.drop(columns=['Description']).join(features_df)

    print("Extracting features from the 'More info' column...")
    more_info_features_df = df['More info'].apply(extract_more_info).apply(pd.Series)

    df = df.drop(columns=['More info']).join(more_info_features_df)

    df = df.apply(lambda x: x.astype(str).str.lower())

    df['Name'] = df.apply(remove_color_from_name, axis=1)

    df['Name'] = df.apply(remove_category_from_name, axis=1)

    df['Name'] = df['Name'].str.replace('pc', '').str.strip()


    if 'Design' not in df.columns:
        print("Data processing complete.")
        return df
    else:
        df['Design'] = df['Design'].str.lower().str.replace('with', ' with ')
        df['shirt material'] = df['Design'].str.split(' with ').str[0]
        df['trouser/dupatta'] = df['Design'].str.split(' with ').str[1]

        df['trouser/dupatta'] = df['trouser/dupatta'].astype(str)
        
        print("Splitting 'trouser/dupatta' into 'trouser material' and 'dupatta material' columns...")
        df['trouser material'] = df['trouser/dupatta'].apply(lambda x: x if 'trouser' in x else None)
        df['dupatta material'] = df['trouser/dupatta'].apply(lambda x: x if 'dupatta' in x else None)

        df.drop("trouser/dupatta", axis=1, inplace=True)

        print("Cleaning up material columns...")
        df['trouser material'] = df['trouser material'].str.replace('trouser', '')
        df['dupatta material'] = df['dupatta material'].str.replace('dupatta', '')
        df['shirt material'] = df['shirt material'].str.replace('shirt', '')

    print("Data processing complete.")
    return df
