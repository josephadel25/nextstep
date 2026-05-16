# NextStep (HireFlow) - Full Project Documentation

## 1. Project Overview
NextStep is an intelligent, cloud-based recruitment platform designed to bridge the gap between candidates and recruiters. The platform automatically extracts structured information (Skills, Education, Experience) from uploaded CVs (PDF/DOCX) using a fine-tuned Artificial Intelligence model, reducing manual data entry and streamlining the hiring process.

---

## 2. Team Roles & Contributions
The project was divided into specialized phases, with team members collaborating across domains:

- **AI & Data Science Team**: Responsible for curating the dataset (Kaggle/SkillSpan), processing raw text, fine-tuning the DistilBERT model for Token Classification (NER), and building the AI microservice.
- **Backend & Cloud Architecture Team**: Responsible for designing the relational database, writing the FastAPI backend, implementing JWT authentication, integrating AWS S3, and deploying the system using Docker and AWS EC2.
- **Frontend & UX Design Team**: Responsible for the responsive, glassmorphic HTML/CSS/JS user interface, ensuring dynamic API integration (CORS), and providing a seamless user experience.
- **QA & Testing Team**: Responsible for defining evaluation metrics, running load tests, and ensuring system stability under concurrent user access.

---

## 3. Architecture & Integrations

NextStep utilizes a modern, decoupled microservices architecture deployed entirely on the AWS Cloud (Free Tier).

### 3.1 Cloud Infrastructure (AWS)
- **AWS EC2 (t2.micro)**: Acts as the main host server running Linux (Ubuntu). It runs the backend API, the AI microservice, and the database within isolated Docker containers.
- **AWS S3**: Provides 99.999999999% durability for storing binary candidate resumes. Resumes are saved with UUIDs (e.g., `resumes/{user_id}/{uuid}.pdf`) to prevent collisions. Secure, time-limited pre-signed URLs are generated for recruiters to download resumes.
- **Security**: EC2 Security Groups strictly limit inbound traffic to ports 22 (SSH), 80 (API), and 8080 (Frontend). The AI Service port (8001) is internal to the Docker network and hidden from the public internet.

### 3.2 Microservices & Tech Stack
- **Frontend**: Vanilla HTML, CSS, and JS served by a Python HTTP server on port `8080`.
- **Backend Service (Port 80)**: Built with Python **FastAPI**. Handles user authentication (JWT), profile management, and database CRUD operations.
- **AI Service (Port 8001)**: A dedicated Python microservice running the fine-tuned BERT model via the Hugging Face `transformers` library.
- **Database**: **MySQL** relational database storing normalized data across 8 tables (`users`, `profiles`, `skills`, `education`, `experience`, `courses`, `projects`, `applications`).
- **Containerization**: Both services are packaged with **Docker** and managed via `docker-compose.yml`. They use `restart: always` to ensure high availability.

---

## 4. AI & Machine Learning Pipeline

The core intelligence of NextStep is its Named Entity Recognition (NER) pipeline.

### 4.1 The Model
We used **DistilBERT** (`distilbert-base-uncased`) as the foundation due to its balance of speed and accuracy, which is critical for a free-tier EC2 instance with limited RAM.

### 4.2 Fine-Tuning Phase
The base model was fine-tuned on a custom dataset tailored for resumes (combining Kaggle resume data and the SkillSpan dataset). The model was trained to classify tokens into three primary categories:
- `SKILL` (e.g., Python, SQL, Project Management)
- `EDU` (Degrees and Universities)
- `EXP` (Job Titles and Companies)

*Note: For maximum reliability in production, Education is supplemented with a Rule-Based Heuristic approach, and Experience relies on candidate manual entry, while Skills rely 100% on the fine-tuned AI extraction.*

---

## 5. Testing & Evaluation Matrix

To prove the platform's readiness, we ran three distinct experiments focusing on AI accuracy, API stability, and Cloud scalability.

### Experiment 1: AI Model Evaluation (NER Metrics)
We evaluated the fine-tuned model against a held-out test dataset to calculate Precision, Recall, and F1-Score.

**Command Run:** `python evaluate_model.py`
**Results:**
```text
========================================
             RESULTS
========================================
Total resumes tested: 4
Total time taken:     0.19 seconds
Average time/resume:  0.05 seconds

METRICS:
Precision: 0.84  (84% of extracted skills were correct)
Recall:    0.79  (79% of actual skills were found)
F1-Score:  0.81  (Overall model accuracy score)

Conclusion: Fine-tuned model shows excellent domain adaptation (+44% improvement over base model).
```

### Experiment 2: API Integration Testing
We tested the live backend API to ensure public endpoints respond correctly and private endpoints correctly reject unauthorized access.

**Command Run:** `python test_api.py`
**Results:**
```text
==================================================
  Running API Integration Tests
==================================================
Test 1: GET /api/stats (Public endpoint)
  ✅ Passed. Valid JSON response received.
Test 2: GET /api/auth/me (Unauthorized access)
  ✅ Passed. Correctly blocked unauthorized user.
Test 3: GET /api/profile/me (Unauthorized access)
  ✅ Passed. Correctly blocked unauthorized user.
Test 4: Backend Service Health
  ✅ Passed. Backend is up and connected to DB.

🎉 ALL TESTS PASSED SUCCESSFULLY! The API is stable.
```

### Experiment 3: Cloud Load & Stress Testing
To verify the AWS EC2 `t2.micro` instance could handle real-world traffic, we simulated 50 concurrent users making 10 requests each (500 total requests).

**Command Run:** `python load_test.py`
**Results:**
```text
========================================
             TEST RESULTS
========================================
Total Time Taken:  5.12 seconds
Total Requests:    500
Successful:        500
Failed:            0
Success Rate:      100.00%

PERFORMANCE METRICS:
Requests/Second:   97.60 req/s
Average Latency:   0.2632 seconds per request

Conclusion: PASS ✅ - EC2 instance (t2.micro) successfully handled the load.
```

---

## 6. Deployment Guide (How to Run)

The platform is already deployed live on AWS at `http://13.53.39.78:8080`. 

To deploy it from scratch on a new server, follow these steps:

### Prerequisites
- A Linux server (e.g., Ubuntu on AWS EC2)
- Docker and Docker Compose installed
- AWS IAM Credentials with S3 access

### Step 1: Clone and Configure
1. Upload the source code to the server.
2. Create a `.env` file in the `backend/` directory containing the database and AWS credentials:
   ```env
   DATABASE_URL=mysql+pymysql://user:password@localhost/nextstep
   SECRET_KEY=your_jwt_secret_key
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   S3_BUCKET_NAME=nextstep-resumes-bucket
   ```

### Step 2: Build and Run Docker Containers
Navigate to the root directory containing `docker-compose.yml` and run:
```bash
sudo docker compose up --build -d
```
*This command builds the FastAPI and AI Service images, sets up the internal bridge network, and starts them in detached mode.*

### Step 3: Start the Frontend
Since the frontend uses vanilla HTML/JS, it is served via a lightweight Python server:
```bash
cd /home/ubuntu/nextstep
nohup python3 -m http.server 8080 &
```

### Step 4: Verify Deployment
Run the integration tests or check the Docker logs to ensure everything is running smoothly:
```bash
sudo docker compose logs -f backend
```
Access the application via your browser at `http://<SERVER_IP>:8080`.
