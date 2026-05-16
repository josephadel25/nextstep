from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, uuid, pdfplumber, docx, boto3
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

app = FastAPI(title="HireFlow AI Service")

# Load environment variables
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'nextstep-resumes-bucket')
MODEL_DIR = os.getenv('MODEL_DIR', '/app/model')

# Initialize S3 client
s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

# Global pipeline
nlp_pipeline = None

def get_nlp_pipeline():
    global nlp_pipeline
    if nlp_pipeline is None:
        print(f"Loading fine-tuned model from {MODEL_DIR}...")
        if not os.path.exists(MODEL_DIR):
            raise RuntimeError(f"Model directory {MODEL_DIR} not found.")
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
            model = AutoModelForTokenClassification.from_pretrained(MODEL_DIR)
            nlp_pipeline = pipeline("token-classification", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e
    return nlp_pipeline

class ParseRequest(BaseModel):
    s3_url: str

def extract_text_from_pdf(filepath):
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                text += " ".join([w['text'] for w in words]) + "\n"
    except: pass
    return text

def extract_text_from_docx(filepath):
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs: text += para.text + "\n"
    except: pass
    return text

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/parse")
async def parse_resume(request: ParseRequest):
    nlp = get_nlp_pipeline()
    
    # Extract key from S3 URL
    # Assuming s3_url is like "s3://bucket/key" or just the key "resumes/user_id/filename"
    s3_key = request.s3_url
    if s3_key.startswith("s3://"):
        s3_key = s3_key.replace(f"s3://{S3_BUCKET_NAME}/", "")
        
    local_path = f"/tmp/{uuid.uuid4()}"
    
    try:
        # Download from S3
        print(f"Downloading {s3_key} from S3...")
        s3_client.download_file(S3_BUCKET_NAME, s3_key, local_path)
        
        # Extract text
        ext = os.path.splitext(s3_key)[1].lower()
        if ext == '.pdf':
            text = extract_text_from_pdf(local_path)
        elif ext == '.docx':
            text = extract_text_from_docx(local_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
            
        # Run inference
        entities = nlp(text)
        print(f"Raw entities found: {entities}")
        
        # Process results
        result = {"job_title": "", "skills": [], "education": [], "experience": []}
        stop_words = ["and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "with", "by", "of", "is", "are", "was", "were"]
        
        for ent in entities:
            label = ent['entity_group']
            word = ent['word'].strip()
            
            # Clean
            word = word.replace("##", "")
            word = word.strip(":,#' ")
            
            if not word or (len(word) <= 1 and not word.isalnum()):
                continue
            if word.lower() in stop_words:
                continue
                
            if label == "SKILL":
                if word not in result['skills'] and len(word) > 1:
                    result['skills'].append(word)
            elif label == "EDU":
                if word not in [e['degree'] for e in result['education']]:
                    result['education'].append({"degree": word[:150], "school": "Not specified", "year": "Not specified"})
            elif label == "EXP":
                if word not in [e['job_title'] for e in result['experience']]:
                    result['experience'].append({"job_title": word[:150], "company": "Not specified", "period": "Not specified", "description": "Extracted by model"})
                    
        # Comprehensive skill list from user's CVs and common tech stack
        common_skills = [
            # Languages
            "Python", "SQL", "Java", "C++", "JavaScript", "TypeScript", "C#", "PHP", "Go", "Rust", "Kotlin", "Swift", "R", "C",
            # Frontend
            "React", "Angular", "Vue", "HTML", "CSS", "Tailwind", "Bootstrap",
            # Backend / Frameworks
            "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring Boot", "Laravel",
            # Cloud / DevOps
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub", "Jenkins", "Terraform", "CI/CD", "MLOps", "MLflow",
            # AI / ML / Data Science
            "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", "Computer Vision", "Data Science", 
            "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Keras", "OpenCV", "BeautifulSoup", "Web Scraping",
            "Generative AI", "Prompt Engineering", "Hugging Face", "Transformers", "CNNs", "RNNs", "Evolutionary Algorithms",
            # Data Analysis & Visualization
            "Excel", "VBA", "Power Query", "Power BI", "DAX", "Matplotlib", "Seaborn", "Plotly", "Tableau", "EDA", "Data Cleaning", "Dashboard Design",
            # Tools & Platforms
            "Jupyter Notebook", "Google Colab", "Kaggle", "VS Code", "Microsoft Azure", "Microsoft SQL Server",
            # Core CS
            "Data Structures & Algorithms", "OOP", "Database Design", "Software Engineering", "Probability & Statistics"
        ]
        import re
        for skill in common_skills:
            # Use word boundaries to avoid matching parts of words
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                if skill not in result['skills']:
                    result['skills'].append(skill)
                    
        # Cleanup
        if os.path.exists(local_path):
            os.remove(local_path)
            
        return result
        
    except Exception as e:
        if os.path.exists(local_path):
            os.remove(local_path)
        print(f"Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))
