import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import numpy as np
import pdfplumber
import docx

# Suppress warnings
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = 'true'

# Text extraction functions (same as on server)
def extract_text_from_pdf(filepath):
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                # extract_words often handles spacing issues better than extract_text
                words = page.extract_words()
                text += " ".join([w['text'] for w in words]) + "\n"
    except Exception as e:
        text = f"Error reading PDF: {str(e)}"
    return text

def extract_text_from_docx(filepath):
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs: text += para.text + "\n"
    except Exception as e:
        text = f"Error reading DOCX: {str(e)}"
    return text

class ModelTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NextStep - local CV Parser Tester")
        self.root.geometry("900x700")
        self.root.configure(bg="#0a0f1e")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Inter', 10, 'bold'), background='#6366f1', foreground='white')
        style.configure('TLabel', font=('Inter', 10), background='#0a0f1e', foreground='#94a3b8')
        
        # Header
        header = tk.Label(root, text="Local CV Parser & Skill Extractor", font=("Plus Jakarta Sans", 18, "bold"), bg="#0a0f1e", fg="#fff")
        header.pack(pady=15)
        
        # Status
        self.status_label = tk.Label(root, text="Loading model... please wait...", font=("Inter", 10, "italic"), bg="#0a0f1e", fg="#818cf8")
        self.status_label.pack(pady=5)
        
        # Action Buttons Frame
        btn_frame = tk.Frame(root, bg="#0a0f1e")
        btn_frame.pack(pady=10)
        
        self.btn_upload = ttk.Button(btn_frame, text="📁 Upload CV (PDF/DOCX)", command=self.upload_file)
        self.btn_upload.pack(side="left", padx=10)
        
        self.btn_parse = ttk.Button(btn_frame, text="🚀 Extract Info", command=self.parse_text)
        self.btn_parse.pack(side="left", padx=10)
        
        # Input Area
        input_label = tk.Label(root, text="Extracted Text (You can edit this):", font=("Inter", 11, "bold"), bg="#0a0f1e", fg="#94a3b8")
        input_label.pack(anchor="w", padx=40, pady=(10, 5))
        
        self.text_input = scrolledtext.ScrolledText(root, height=12, width=90, font=("Inter", 10), bg="#0f172a", fg="#f1f5f9", insertbackground='white', borderwidth=1, relief="solid")
        self.text_input.pack(padx=40, pady=5)
        
        # Output Area
        output_label = tk.Label(root, text="Results:", font=("Inter", 11, "bold"), bg="#0a0f1e", fg="#94a3b8")
        output_label.pack(anchor="w", padx=40, pady=(10, 5))
        
        self.text_output = scrolledtext.ScrolledText(root, height=12, width=90, font=("Inter", 10), bg="#0f172a", fg="#6ee7b7", borderwidth=1, relief="solid")
        self.text_output.pack(padx=40, pady=5)
        
        # Load Model in background
        self.root.after(100, self.load_model)
        
    def load_model(self):
        model_dir = r"c:\Users\Dell\Desktop\Cloud Projecct\d\cv-extractor-new"
        if not os.path.exists(model_dir):
            self.status_label.config(text="Error: Model directory not found. Train first!", fg="#ef4444")
            return
            
        try:
            from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
            
            print(f"Loading model from {model_dir}...")
            tokenizer = AutoTokenizer.from_pretrained(model_dir)
            model = AutoModelForTokenClassification.from_pretrained(model_dir)
            
            self.nlp = pipeline("token-classification", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
            self.status_label.config(text="Model loaded successfully! Ready to test.", fg="#10b981")
        except Exception as e:
            self.status_label.config(text=f"Error loading model: {str(e)}", fg="#ef4444")

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Resume Files", "*.pdf *.docx")])
        if not file_path:
            return
            
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, f"Loading {os.path.basename(file_path)}...\n")
        self.root.update()
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif ext == '.docx':
            text = extract_text_from_docx(file_path)
        else:
            text = "Unsupported file format."
            
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, text)
        self.status_label.config(text=f"Loaded {os.path.basename(file_path)}", fg="#818cf8")

    def parse_text(self):
        if not hasattr(self, 'nlp'):
            self.text_output.insert(tk.END, "Model not loaded yet.\n")
            return
            
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            return
            
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, "Running inference...\n\n")
        
        entities = self.nlp(text)
        
        extracted_skills = []
        extracted_edu = []
        extracted_exp = []
        
        for ent in entities:
            label = ent['entity_group']
            word = ent['word'].strip()
            
            # Clean up word (remove ## from BPE tokenization if any)
            word = word.replace("##", "")
            
            if label == "SKILL":
                if word not in extracted_skills and len(word) > 1:
                    extracted_skills.append(word)
            elif label == "EDU":
                if word not in extracted_edu and len(word) > 1:
                    extracted_edu.append(word)
            elif label == "EXP":
                if word not in extracted_exp and len(word) > 1:
                    extracted_exp.append(word)
                    
        # Fallback/Parallel: Substring matching for common skills
        common_skills = [
            "python", "java", "c++", "sql", "excel", "powerbi", "pandas", "numpy", 
            "matplotlib", "scikit-learn", "tensorflow", "keras", "azure", "git", "github",
            "deep learning", "nlp", "machine learning", "data analysis"
        ]
        
        text_lower = text.lower()
        for skill in common_skills:
            if skill in text_lower:
                if skill.lower() not in [s.lower() for s in extracted_skills]:
                    extracted_skills.append(skill.title())
                    
        # Rule-based extraction for Education (Keep it as a reference)
        edu_text = ""
        idx = text_lower.find("education")
        if idx != -1:
            next_idx = len(text)
            for other_kw in ["experience", "projects", "skills", "courses", "summary"]:
                oi = text_lower.find(other_kw, idx + 9)
                if oi != -1 and oi < next_idx:
                    next_idx = oi
            edu_text = text[idx + 9:next_idx].strip()
            
        # Display results
        self.text_output.insert(tk.END, "--- Extracted Skills (Model + Fallback) ---\n")
        if extracted_skills:
            # Filter out single characters or punctuation if any
            clean_skills = [s for s in extracted_skills if len(s) > 1 or s.isalnum()]
            self.text_output.insert(tk.END, f"{', '.join(clean_skills)}\n")
        else:
            self.text_output.insert(tk.END, "No skills detected.\n")
            
        self.text_output.insert(tk.END, "\n--- Extracted Education (Model) ---\n")
        if extracted_edu:
            self.text_output.insert(tk.END, f"{', '.join(extracted_edu)}\n")
        else:
            self.text_output.insert(tk.END, "No Education detected by model.\n")
            
        self.text_output.insert(tk.END, "\n--- Extracted Experience (Model) ---\n")
        if extracted_exp:
            self.text_output.insert(tk.END, f"{', '.join(extracted_exp)}\n")
        else:
            self.text_output.insert(tk.END, "No Experience detected by model.\n")
            
        self.text_output.insert(tk.END, "\n--- Rule-Based Education Section (Reference) ---\n")
        if edu_text:
            self.text_output.insert(tk.END, edu_text[:200] + "...\n")
        else:
            self.text_output.insert(tk.END, "No Education section found by rules.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModelTesterApp(root)
    root.mainloop()
