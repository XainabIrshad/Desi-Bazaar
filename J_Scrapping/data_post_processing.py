import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data (run these once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def combine_columns(df, new_column, *columns):
    """
    Combine multiple columns into a new attribute in a DataFrame.
    
    :param df: The DataFrame to operate on.
    :param new_column: The name of the new column to create.
    :param columns: The columns to combine.
    """
    # Filter out columns that are not in the DataFrame
    columns_to_combine = [col for col in columns if col in df.columns]
    
    if columns_to_combine:
        df[new_column] = df[columns_to_combine[0]].astype(str)
        for col in columns_to_combine[1:]:
            df[new_column] += ', ' + df[col].astype(str)
    else:
        df[new_column] = None  # If none of the columns exist, assign None

    return df

def clean_cell(cell):
    if pd.isna(cell):  # Check if the cell is NaN
        return ""
    words = cell.split(',')
    cleaned_words = set()  # Using a set to avoid duplicates
    for word in words:
        word = word.strip()  # Remove any leading/trailing spaces
        if word.lower() != 'nan' and word not in cleaned_words:
            cleaned_words.add(word)
    return ' '.join(cleaned_words)

def post_processing(df):
    # Specify the columns to process
    cols = ['Fabric Type', 'Neckline', 'Collection', 'Shirt Front', 'Shirt Back', 'Trouser',
            'Sleeves', 'Style Cut', 'Length', 'Embellishment', 'Type', 'Color', 
            'Product Category', 'Season', 'Size', 'Design', 'Shirt Pattern', 
            'Shirt color', 'Shirt Sleeves', 'Shirt Length', 'Shirt Daman', 
            'Shirt Neckline', 'if multicolored', 'Trouser Pattern', 'Trouser Color', 
            'Trouser Length', 'Trouser Style', 'Is Dupatta Printed', 'Dupatta Pattern', 
            'Dupatta Color', 'Sleeves Pattern', 'shirt material', 'trouser material', 
            'dupatta material']
    cols=[col for col in cols if col in df.columns]
    # Initialize NLTK components
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    # Define a function to process text into keywords
    def extract_keywords(text):
        if pd.isna(text):
            return ''
        
        # Tokenize the text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        filtered_tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalpha() and word not in stop_words]
        
        # Return keywords as a space-separated string
        return ', '.join(filtered_tokens)

    # Apply the function to the specified columns
    print("Processing columns for keyword extraction...")
    for col in cols:
        if col in df.columns: 
            print(f"Processing column: {col}")
            df[col] = df[col].apply(extract_keywords)
    print("Combining columns to form new attributes...")


    print("Combining columns to form new attributes...")
    df = combine_columns(df, 'Neckline', 'Neckline', 'Shirt Neckline')
    df = combine_columns(df, 'Fabric Type', 'Fabric Type', 'shirt material', 'trouser material', 'dupatta material')
    df = combine_columns(df, 'Collection', 'Collection', 'Season', 'Design', 'Product Category', 'Type')
    df = combine_columns(df, 'Shirt', 'Shirt Front', 'Shirt Pattern', 'Shirt Back', 'Style Cut', 'Shirt Length', 'Shirt Daman', 'Length')
    df = combine_columns(df, 'Trouser', 'Trouser', 'Trouser Pattern', 'Trouser Length', 'Trouser Style')
    df = combine_columns(df, 'Dupatta', 'Dupatta Pattern')
    df = combine_columns(df, 'Color', 'Color', 'Shirt color', 'Trouser Color', 'Dupatta Color')
    df = combine_columns(df, 'Sleeves', 'Sleeves', 'Sleeves Pattern', 'Shirt Sleeves')

    print("Dropping unnecessary columns...")
    extra_cols = ['Shirt Neckline', 'shirt material', 'trouser material', 'dupatta material', 'Season', 'Design', 
             'Product Category', 'Type', 'Shirt Front', 'Shirt Pattern', 'Shirt Back', 'Style Cut', 
             'Shirt Length', 'Shirt Daman', 'Length', 'Trouser Pattern', 'Trouser Length', 'Trouser Style', 
             'Dupatta Pattern', 'Shirt color', 'Shirt Sleeves', 'if multicolored', 'Is Dupatta Printed', 
             'Dupatta Color', 'Sleeves Pattern']
    extra_cols = [col for col in extra_cols if col in df.columns]
    df.drop(extra_cols, axis=1, inplace=True)
    
    # Apply the clean_cell function to each cell in the DataFrame
    df = df.applymap(clean_cell)
    print("Post-processing complete!")
    
    return df
