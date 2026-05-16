import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
from datasets import Dataset

DATASET_PATH = Path(r"c:\Users\Dell\Desktop\Cloud Projecct\d\new dataset\Entity Recognition in Resumes.json")
MODEL_OUTPUT_DIR = Path(r"c:\Users\Dell\Desktop\Cloud Projecct\d\cv-extractor-new")

LABEL_LIST = ["O", "B-SKILL", "I-SKILL", "B-EDU", "I-EDU", "B-EXP", "I-EXP"]
LABEL_TO_ID = {label: i for i, label in enumerate(LABEL_LIST)}
ID_TO_LABEL = {i: label for i, label in enumerate(LABEL_LIST)}

MAP_LABELS = {
    "Skills": "SKILL",
    "Degree": "EDU",
    "College Name": "EDU",
    "Companies worked at": "EXP",
    "Designation": "EXP"
}

def load_and_preprocess_data(tokenizer):
    examples = []
    
    dataset_paths = [
        Path(r"c:\Users\Dell\Desktop\Cloud Projecct\d\new dataset\Entity Recognition in Resumes.json"),
        Path(r"c:\Users\Dell\Desktop\Cloud Projecct\d\new dataset\traindata.json")
    ]
    
    for path in dataset_paths:
        print(f"Loading from {path.name}...")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                    
                text = data["content"]
                annotations = data.get("annotation", [])
                
                # Create character level labels
                char_labels = ["O"] * len(text)
                for ann in annotations:
                    if not ann.get("label"):
                        continue
                    label_name = ann["label"][0]
                    if label_name not in MAP_LABELS:
                        continue
                    entity_type = MAP_LABELS[label_name]
                    
                    for point in ann["points"]:
                        start = point["start"]
                        end = point["end"]
                        
                        # Ensure indices are within bounds
                        start = max(0, start)
                        end = min(len(text), end)
                        
                        if start < end:
                            char_labels[start] = f"B-{entity_type}"
                            for i in range(start + 1, end):
                                char_labels[i] = f"I-{entity_type}"
                                
                # Tokenize and align
                tokenized = tokenizer(text, return_offsets_mapping=True, truncation=True, max_length=512, padding="max_length")
                offsets = tokenized["offset_mapping"]
                
                labels = []
                for tok_start, tok_end in offsets:
                    if tok_start == 0 and tok_end == 0:
                        labels.append(-100) # Special tokens
                        continue
                        
                    covered_labels = char_labels[tok_start:tok_end]
                    
                    b_tags = [tag for tag in covered_labels if tag.startswith("B-")]
                    i_tags = [tag for tag in covered_labels if tag.startswith("I-")]
                    
                    if b_tags:
                        labels.append(LABEL_TO_ID[b_tags[0]])
                    elif i_tags:
                        labels.append(LABEL_TO_ID[i_tags[0]])
                    else:
                        labels.append(LABEL_TO_ID["O"])
                        
                examples.append({
                    "input_ids": tokenized["input_ids"],
                    "attention_mask": tokenized["attention_mask"],
                    "labels": labels
                })
                
    return Dataset.from_list(examples)

def main():
    model_name = "yashpwr/resume-ner-bert-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    print("Loading and preprocessing dataset...")
    dataset = load_and_preprocess_data(tokenizer)
    print(f"Dataset size: {len(dataset)}")
    
    if len(dataset) == 0:
        print("No valid data found!")
        return
        
    # Split
    dataset_split = dataset.train_test_split(test_size=0.1)
    
    # Load model
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(LABEL_LIST),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID,
        ignore_mismatched_sizes=True
    )
    
    # Training Arguments
    training_args = TrainingArguments(
        output_dir="./results_new",
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=4, # Reduced batch size for safety
        per_device_eval_batch_size=4,
        num_train_epochs=10,
        weight_decay=0.01,
        save_total_limit=1,
        logging_steps=10,
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset_split["train"],
        eval_dataset=dataset_split["test"],
        tokenizer=tokenizer,
    )
    
    print("Starting training...")
    trainer.train()
    
    # Save model
    print(f"Saving model to {MODEL_OUTPUT_DIR}")
    model.save_pretrained(MODEL_OUTPUT_DIR)
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)
    print("Done!")

if __name__ == "__main__":
    main()
