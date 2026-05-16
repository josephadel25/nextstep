import json

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Complete Model Walkthrough: From Raw Data to Inference\n",
    "This notebook covers the entire lifecycle of our Named Entity Recognition (NER) model for Resume Parsing.\n",
    "\n",
    "**Steps covered:**\n",
    "1. Data Preprocessing\n",
    "2. Base Model Evaluation (Before Training)\n",
    "3. Fine-Tuning (Training)\n",
    "4. Post-Training Evaluation\n",
    "5. Visualization of Training Metrics\n",
    "6. Real-World Testing"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "from pathlib import Path\n",
    "import torch\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "from datasets import Dataset\n",
    "from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer\n",
    "import evaluate\n",
    "\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Data Preprocessing\n",
    "We load our raw annotated resume dataset and align character-level annotations to token-level labels."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "LABEL_LIST = [\"O\", \"B-SKILL\", \"I-SKILL\", \"B-EDU\", \"I-EDU\", \"B-EXP\", \"I-EXP\"]\n",
    "LABEL_TO_ID = {label: i for i, label in enumerate(LABEL_LIST)}\n",
    "ID_TO_LABEL = {i: label for i, label in enumerate(LABEL_LIST)}\n",
    "\n",
    "MAP_LABELS = {\n",
    "    \"Skills\": \"SKILL\",\n",
    "    \"Degree\": \"EDU\",\n",
    "    \"College Name\": \"EDU\",\n",
    "    \"Companies worked at\": \"EXP\",\n",
    "    \"Designation\": \"EXP\"\n",
    "}\n",
    "\n",
    "model_name = \"distilbert-base-uncased\"\n",
    "tokenizer = AutoTokenizer.from_pretrained(model_name)\n",
    "\n",
    "def load_and_preprocess_data():\n",
    "    examples = []\n",
    "    dataset_paths = [\n",
    "        Path(r\"c:\\Users\\Dell\\Desktop\\Cloud Projecct\\d\\new dataset\\Entity Recognition in Resumes.json\"),\n",
    "        Path(r\"c:\\Users\\Dell\\Desktop\\Cloud Projecct\\d\\new dataset\\traindata.json\")\n",
    "    ]\n",
    "    \n",
    "    for path in dataset_paths:\n",
    "        if not path.exists(): continue\n",
    "        with open(path, \"r\", encoding=\"utf-8\") as f:\n",
    "            for line in f:\n",
    "                if not line.strip(): continue\n",
    "                try: data = json.loads(line)\n",
    "                except: continue\n",
    "                    \n",
    "                text = data[\"content\"]\n",
    "                annotations = data.get(\"annotation\", [])\n",
    "                \n",
    "                char_labels = [\"O\"] * len(text)\n",
    "                for ann in annotations:\n",
    "                    if not ann.get(\"label\"): continue\n",
    "                    label_name = ann[\"label\"][0]\n",
    "                    if label_name not in MAP_LABELS: continue\n",
    "                    entity_type = MAP_LABELS[label_name]\n",
    "                    \n",
    "                    for point in ann[\"points\"]:\n",
    "                        start, end = max(0, point[\"start\"]), min(len(text), point[\"end\"])\n",
    "                        if start < end:\n",
    "                            char_labels[start] = f\"B-{entity_type}\"\n",
    "                            for i in range(start + 1, end):\n",
    "                                char_labels[i] = f\"I-{entity_type}\"\n",
    "                                \n",
    "                tokenized = tokenizer(text, return_offsets_mapping=True, truncation=True, max_length=256, padding=\"max_length\")\n",
    "                offsets = tokenized[\"offset_mapping\"]\n",
    "                \n",
    "                labels = []\n",
    "                for tok_start, tok_end in offsets:\n",
    "                    if tok_start == 0 and tok_end == 0:\n",
    "                        labels.append(-100)\n",
    "                        continue\n",
    "                        \n",
    "                    covered_labels = char_labels[tok_start:tok_end]\n",
    "                    b_tags = [tag for tag in covered_labels if tag.startswith(\"B-\")]\n",
    "                    i_tags = [tag for tag in covered_labels if tag.startswith(\"I-\")]\n",
    "                    \n",
    "                    if b_tags: labels.append(LABEL_TO_ID[b_tags[0]])\n",
    "                    elif i_tags: labels.append(LABEL_TO_ID[i_tags[0]])\n",
    "                    else: labels.append(LABEL_TO_ID[\"O\"])\n",
    "                        \n",
    "                examples.append({\"input_ids\": tokenized[\"input_ids\"], \"attention_mask\": tokenized[\"attention_mask\"], \"labels\": labels})\n",
    "                \n",
    "    return Dataset.from_list(examples)\n",
    "\n",
    "dataset = load_and_preprocess_data()\n",
    "# Using a small subset so this walkthrough notebook executes quickly in demonstrations\n",
    "small_dataset = dataset.select(range(min(150, len(dataset))))\n",
    "dataset_split = small_dataset.train_test_split(test_size=0.2)\n",
    "print(f\"Loaded dataset! Train size: {len(dataset_split['train'])}, Test size: {len(dataset_split['test'])}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Evaluation BEFORE Fine-Tuning\n",
    "Evaluating the untaught base model (`distilbert-base-uncased`) to establish a baseline."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "base_model = AutoModelForTokenClassification.from_pretrained(\n",
    "    model_name,\n",
    "    num_labels=len(LABEL_LIST),\n",
    "    id2label=ID_TO_LABEL,\n",
    "    label2id=LABEL_TO_ID,\n",
    "    ignore_mismatched_sizes=True\n",
    ")\n",
    "\n",
    "seqeval = evaluate.load(\"seqeval\")\n",
    "\n",
    "def compute_metrics(p):\n",
    "    predictions, labels = p\n",
    "    predictions = np.argmax(predictions, axis=2)\n",
    "    true_predictions = [\n",
    "        [LABEL_LIST[p] for (p, l) in zip(prediction, label) if l != -100]\n",
    "        for prediction, label in zip(predictions, labels)\n",
    "    ]\n",
    "    true_labels = [\n",
    "        [LABEL_LIST[l] for (p, l) in zip(prediction, label) if l != -100]\n",
    "        for prediction, label in zip(predictions, labels)\n",
    "    ]\n",
    "    results = seqeval.compute(predictions=true_predictions, references=true_labels)\n",
    "    return {\n",
    "        \"precision\": results[\"overall_precision\"],\n",
    "        \"recall\": results[\"overall_recall\"],\n",
    "        \"f1\": results[\"overall_f1\"],\n",
    "        \"accuracy\": results[\"overall_accuracy\"],\n",
    "    }\n",
    "\n",
    "pre_trainer = Trainer(model=base_model, eval_dataset=dataset_split[\"test\"], compute_metrics=compute_metrics)\n",
    "pre_eval_results = pre_trainer.evaluate()\n",
    "\n",
    "print(\"\\n--- PRE-TRAINING METRICS ---\")\n",
    "print(f\"Precision: {pre_eval_results['eval_precision']:.4f}\")\n",
    "print(f\"Recall:    {pre_eval_results['eval_recall']:.4f}\")\n",
    "print(f\"F1-Score:  {pre_eval_results['eval_f1']:.4f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Fine-Tuning (Training)\n",
    "Training the model on our parsed CVs. For this demonstration walkthrough, we use a quick 3 epochs."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "training_args = TrainingArguments(\n",
    "    output_dir=\"./walkthrough_results\",\n",
    "    eval_strategy=\"epoch\",\n",
    "    learning_rate=5e-5,\n",
    "    per_device_train_batch_size=8,\n",
    "    per_device_eval_batch_size=8,\n",
    "    num_train_epochs=3,\n",
    "    weight_decay=0.01,\n",
    "    save_total_limit=1,\n",
    "    logging_steps=5,\n",
    ")\n",
    "\n",
    "trainer = Trainer(\n",
    "    model=base_model,\n",
    "    args=training_args,\n",
    "    train_dataset=dataset_split[\"train\"],\n",
    "    eval_dataset=dataset_split[\"test\"],\n",
    "    tokenizer=tokenizer,\n",
    "    compute_metrics=compute_metrics\n",
    ")\n",
    "\n",
    "print(\"Starting Training...\")\n",
    "train_results = trainer.train()\n",
    "print(\"Training Complete!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Evaluation AFTER Fine-Tuning\n",
    "Re-evaluating the model on the exact same test set to demonstrate learning improvement."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "post_eval_results = trainer.evaluate()\n",
    "\n",
    "print(\"\\n--- POST-TRAINING METRICS ---\")\n",
    "print(f\"Precision: {post_eval_results['eval_precision']:.4f}\")\n",
    "print(f\"Recall:    {post_eval_results['eval_recall']:.4f}\")\n",
    "print(f\"F1-Score:  {post_eval_results['eval_f1']:.4f}\")\n",
    "\n",
    "f1_improvement = post_eval_results['eval_f1'] - pre_eval_results['eval_f1']\n",
    "print(f\"\\nTotal F1 Improvement: +{f1_improvement:.4f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Visualization of Training Metrics\n",
    "Plotting the training loss to visually confirm the model is learning successfully."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "history = trainer.state.log_history\n",
    "loss_values = [h[\"loss\"] for h in history if \"loss\" in h]\n",
    "steps = [h[\"step\"] for h in history if \"loss\" in h]\n",
    "\n",
    "plt.figure(figsize=(10, 5))\n",
    "plt.plot(steps, loss_values, marker='o', linestyle='-', color='b', label='Training Loss')\n",
    "plt.title('Model Training Loss Over Time')\n",
    "plt.xlabel('Training Steps')\n",
    "plt.ylabel('Loss')\n",
    "plt.legend()\n",
    "plt.grid(True)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Real-World Testing & Visualization\n",
    "Finally, we pass a raw, completely unseen resume paragraph to our newly trained model and visualize what it extracts."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "test_resume = \"\"\"\n",
    "Ahmed Hassan\n",
    "Education: B.Sc. in Computer Science, Cairo University\n",
    "Experience: Software Engineer at Microsoft (2020-2023). Developed microservices.\n",
    "Skills: Highly proficient in Python, SQL, Docker, and Machine Learning algorithms.\n",
    "\"\"\"\n",
    "\n",
    "inputs = tokenizer(test_resume, return_tensors=\"pt\", truncation=True, max_length=256)\n",
    "device = \"cuda\" if torch.cuda.is_available() else \"cpu\"\n",
    "inputs = {k: v.to(device) for k, v in inputs.items()}\n",
    "\n",
    "with torch.no_grad():\n",
    "    outputs = base_model(**inputs)\n",
    "\n",
    "predictions = torch.argmax(outputs.logits, dim=2)\n",
    "tokens = tokenizer.convert_ids_to_tokens(inputs[\"input_ids\"][0])\n",
    "pred_labels = [base_model.config.id2label[p.item()] for p in predictions[0]]\n",
    "\n",
    "extracted_data = {\"SKILL\": [], \"EDU\": [], \"EXP\": []}\n",
    "\n",
    "current_entity = []\n",
    "current_type = None\n",
    "\n",
    "for token, label in zip(tokens, pred_labels):\n",
    "    if token in [\"[CLS]\", \"[SEP]\", \"[PAD]\"]: continue\n",
    "        \n",
    "    if label != \"O\":\n",
    "        entity_type = label.split(\"-\")[1]\n",
    "        clean_token = token.replace(\"##\", \"\")\n",
    "        \n",
    "        if label.startswith(\"B-\"):\n",
    "            if current_entity:\n",
    "                extracted_data[current_type].append(\"\".join(current_entity))\n",
    "            current_entity = [clean_token] if not token.startswith(\"##\") else [\" \" + clean_token]\n",
    "            current_type = entity_type\n",
    "        elif label.startswith(\"I-\") and current_type == entity_type:\n",
    "            if token.startswith(\"##\"):\n",
    "                current_entity.append(clean_token)\n",
    "            else:\n",
    "                current_entity.append(\" \" + clean_token)\n",
    "    else:\n",
    "        if current_entity:\n",
    "            extracted_data[current_type].append(\"\".join(current_entity))\n",
    "            current_entity = []\n",
    "            current_type = None\n",
    "\n",
    "if current_entity:\n",
    "    extracted_data[current_type].append(\"\".join(current_entity))\n",
    "\n",
    "print(\"RAW RESUME TEXT:\")\n",
    "print(\"-\" * 50)\n",
    "print(test_resume.strip())\n",
    "print(\"\\nAI EXTRACTED ENTITIES:\")\n",
    "print(\"-\" * 50)\n",
    "for category, items in extracted_data.items():\n",
    "    print(f\"{category}: {', '.join(set(items)) if items else 'None found'}\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {"name": "ipython", "version": 3},
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

with open(r"c:\Users\Dell\Desktop\Cloud Projecct\d\model_walkthrough.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print("model_walkthrough.ipynb generated successfully.")
