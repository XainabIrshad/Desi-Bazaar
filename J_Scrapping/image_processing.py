import os
from PIL import Image
import torch
from tqdm import tqdm
from transformers import ViltProcessor, ViltForQuestionAnswering

def image_processing(df, image_dir):
    """Perform image processing by dividing tasks into smaller functions."""
    # Load model and processor
    processor, model = load_model()

    # Convert the product code column to uppercase
    df['Code'] = df['Code'].str.upper()

    # Extract image codes from filenames
    image_codes = extract_image_codes(image_dir)

    # Process DataFrame rows
    df = process_rows(df, image_codes, image_dir, processor, model)

    # Rename columns
    df = rename_columns(df)

    return df

def load_model():
    """Load the VILT model and processor."""
    processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
    model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
    return processor, model

def extract_image_codes(image_dir):
    """Extract codes from image filenames."""
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    image_codes = {f.split('_')[0].upper(): f for f in image_files}  # Convert to uppercase for consistency
    return image_codes

def process_image_and_answer(image, question, processor, model):
    """Run inference on the image and return top 5 answers for the question."""
    try:
        # Prepare inputs
        encoding = processor(image, question, return_tensors="pt")

        # Forward pass
        outputs = model(**encoding)
        logits = outputs.logits

        # Get all possible answers with their scores
        scores = torch.nn.functional.softmax(logits, dim=-1).squeeze().tolist()
        labels = [model.config.id2label[idx] for idx in range(len(scores))]

        # Combine labels and scores into a list of tuples and sort by score
        label_score_pairs = sorted(zip(labels, scores), key=lambda x: x[1], reverse=True)

        # Return the top 5 labels
        return [label for label, _ in label_score_pairs[:5]]
    except Exception as e:
        print(f"Error processing question '{question}': {e}")
        return []

def process_rows(df, image_codes, image_dir, processor, model):
    """Iterate through each row and process images based on the product category."""
    print("Processing images...")
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        product_category = row['Product Category']
        code = row['Code']

        if code not in image_codes:
            continue
        
        img_path = os.path.join(image_dir, image_codes[code])
        image = Image.open(img_path)

        questions = get_questions(product_category)
        
        for question in questions:
            top_5_labels = process_image_and_answer(image, question, processor, model)
            df.at[index, question] = ' '.join(top_5_labels)
    
    return df

def rename_columns(df):
    """Rename columns in the DataFrame."""
    rename_map = {
        "describe the shirt pattern": "Shirt Pattern",
        "describe the shirt color": "Shirt color",
        "describe the neckline of shirt": "Shirt Neckline",
        "describe the sleeves of the shirt": "Shirt Sleeves",
        "describe the daman of shirt": "Shirt Daman",
        "Is shirt length short, mid-length or long": "Shirt Length",
        "describe the trouser pattern": "Trouser Pattern",
        "describe the trouser color": "Trouser Color",
        "Is trouser length short, mid-length or long": "Trouser Length",
        "describe the dupatta color": "Dupatta Color",
        "describe the dupatta pattern": "Dupatta Pattern",
        "Is the item multicolored": "if multicolored",
        "describe the trouser style": "Trouser Style",
        "Is dupatta printed": "Is Dupatta Printed",
        "describe the sleeves pattern": "Sleeves Pattern"
    }
    df.rename(columns=rename_map, inplace=True)
    return df

def get_questions(product_category):
    """Return relevant questions based on product category."""
    category = product_category.strip().lower()
    
    questions_map = {
        'unstitched 1 piece': [
            "describe the shirt pattern", "describe the shirt color", 
            "describe the sleeves of the shirt", "describe the daman of shirt"],
        'unstitched 2 piece - shirt and dupatta': [
            "describe the shirt pattern", "describe the shirt color", 
            "describe the sleeves of the shirt", "describe the daman of shirt", 
            "describe the dupatta color", "describe the dupatta pattern"],
        'unstitched 2 piece - shirt and trouser': [
            "describe the shirt pattern", "describe the shirt color", 
            "describe the sleeves of the shirt", "describe the daman of shirt", 
            "describe the trouser pattern", "describe the trouser color"],
        'unstitched 3 piece': [
            "describe the shirt pattern", "describe the shirt color", 
            "describe the sleeves of the shirt", "describe the daman of shirt", 
            "describe the trouser pattern", "describe the trouser color", 
            "describe the dupatta color", "describe the dupatta pattern"],
        'ladies kurti': [
            "describe the shirt pattern", "describe the shirt color", 
            "describe the neckline of shirt", "describe the sleeves of the shirt", 
            "describe the daman of shirt", "Is shirt length short, mid-length or long"],
        '2 piece stitched': [
            "describe the shirt pattern", "describe the shirt color", 
            "describe the neckline of shirt", "describe the sleeves of the shirt", 
            "describe the daman of shirt", "Is shirt length short, mid-length or long", 
            "describe the trouser pattern", "describe the trouser color", 
            "Is trouser length short, mid-length or long"],
        '3 piece stitched': [
            "describe the shirt pattern", "describe the shirt color", 
            "describe the neckline of shirt", "describe the sleeves of the shirt", 
            "describe the daman of shirt", "Is shirt length short, mid-length or long", 
            "describe the trouser pattern", "describe the trouser color", 
            "Is trouser length short, mid-length or long", 
            "describe the dupatta color", "describe the dupatta pattern"]
    }
    
    return questions_map.get(category, [])  # Return an empty list if no match
