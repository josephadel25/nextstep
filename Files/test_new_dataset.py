import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

MODEL_DIR = r"c:\Users\Dell\Desktop\Cloud Projecct\d\cv-extractor-new"

def main():
    print("Loading model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        model = AutoModelForTokenClassification.from_pretrained(MODEL_DIR)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please make sure to run train_new_dataset.py first!")
        return
        
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"Device set to use {device}")
    
    # Load a real CV text from the generated raw text folder
    import os
    sample_file = r"c:\Users\Dell\Desktop\Cloud Projecct\d\raw_text_kaggle\0.txt"
    
    if os.path.exists(sample_file):
        print(f"Loading real CV text from {sample_file}...")
        with open(sample_file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        print("Sample file not found. Using fallback text.")
        # Sample text
        text = """
        Ahmed Hassan
        Data Scientist
        
        Summary:
        Experienced data scientist skilled in Python, Machine Learning, and SQL.
        Worked with TensorFlow and Scikit-Learn.
        
        Education:
        Bachelor of Science in Computer Science
        Cairo University, 2023
        
        Experience:
        Data Analyst at Google (2020 - 2022)
        """
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)
    
    # Get labels
    id2label = model.config.id2label
    
    # Decode
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    pred_labels = [id2label[p.item()] for p in predictions[0]]
    
    entities = {
        "SKILL": [],
        "EDU": [],
        "EXP": []
    }
    
    for token, label in zip(tokens, pred_labels):
        if label == "O" or token in ["[CLS]", "[SEP]", "[PAD]"]:
            continue
            
        clean_label = label.replace("B-", "").replace("I-", "")
        clean_token = token.replace("##", "")
        
        if clean_label in entities:
            entities[clean_label].append(clean_token)
            
    print("\nExtracted Entities:")
    print("-" * 50)
    print(f"Skills found: {list(set(entities['SKILL']))}")
    print(f"Education found: {list(set(entities['EDU']))}")
    print(f"Experience found: {list(set(entities['EXP']))}")

if __name__ == "__main__":
    main()
