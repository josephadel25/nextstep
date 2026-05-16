# NextStep Platform Commands Guide

This file contains all the useful commands you might need to run, build, or deploy different parts of this project.

## 1. Local Development (Without Docker)

### Frontend
Since the frontend is a static `index.html` with CSS/JS, you can run a simple local web server to serve it.
```powershell
# Run this from the root directory
python -m http.server 8080
# Then open http://localhost:8080 in your browser
```

### Backend (FastAPI)
The backend service handles main operations and DB connections.
```powershell
# Navigate to the backend folder
cd backend

# Create a virtual environment (if you haven't already)
python -m venv venv

# Activate the virtual environment (Windows)
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run the backend locally (defaults to http://127.0.0.1:8000)
uvicorn main:app --reload
```

### AI Service (FastAPI)
The AI service handles resume extraction.
```powershell
# Navigate to the ai_service folder
cd ai_service

# Create a virtual environment (if you haven't already)
python -m venv venv

# Activate the virtual environment (Windows)
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run the AI service locally on port 8001
uvicorn main:app --reload --port 8001
```

## 2. Docker Commands

If you want to build and run the services using Docker instead of running them natively.

### Build Images
```powershell
# Build backend image
docker build -t nextstep-backend ./backend

# Build AI service image
docker build -t nextstep-ai-service ./ai_service
```

### Run Containers
```powershell
# Run backend container on port 8000
docker run -d -p 8000:80 --name backend nextstep-backend

# Run AI service container on port 8001
docker run -d -p 8001:8001 --name ai-service nextstep-ai-service
```

### Stop & Remove Containers
```powershell
# Stop the containers
docker stop backend ai-service

# Remove the containers
docker rm backend ai-service
```

## 3. Infrastructure & Deployment (Terraform)

If you are deploying your AWS infrastructure.
```powershell
# Navigate to infrastructure folder
cd infrastructure

# Initialize Terraform (downloads providers)
terraform init

# Plan the changes (preview what will be created)
terraform plan

# Apply the changes (creates the AWS resources)
terraform apply

# To destroy all resources when you are done
terraform destroy
```

## 4. Other Useful Commands

### Jupyter Notebooks
If you need to view or run the model training scripts or walkthroughs:
```powershell
# From the root directory, start Jupyter Lab or Notebook
jupyter notebook
# or
jupyter lab
```
