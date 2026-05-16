# 🎙️ NextStep Presentation Walkthrough Script

*This is a step-by-step guide on how to present your project to your supervisor. Follow this flow to make sure you hit every grading criteria on your cover sheet!*

---

## ⏱️ Phase 1: The Introduction (1 Minute)
**What to say:**
> "Hello everyone, we are Team 10. Our project is **NextStep (HireFlow)**, an intelligent recruitment platform. 
> The problem we are solving is that recruiters waste hours manually reading and typing out data from hundreds of CVs. 
> Our solution is a cloud-based web app that uses a fine-tuned AI model to automatically read uploaded PDFs and extract the candidate's Skills, Education, and Experience instantly."

---

## ⏱️ Phase 2: The Live Demo (3 Minutes)
*Show, don't just tell. Have your browser open to `http://13.53.39.78:8080`.*

**Step 1: The Home Page**
> "Our platform is deployed live on an AWS server. Here on the homepage, these statistics (Candidates, Recruiters, Resumes) are fetching real-time data from our MySQL database."

**Step 2: Candidate Upload**
- *Action: Register a new candidate and upload a sample PDF resume.*
> "When a candidate uploads their CV, the PDF goes securely to an AWS S3 bucket. At the exact same time, our FastAPI backend sends the text to our internal AI microservice. As you can see, it automatically extracted their skills and education and built their profile without them typing anything."

**Step 3: Recruiter View**
- *Action: Log out, log in as a Recruiter, and view the candidate you just created.*
> "When a recruiter logs in, they see the structured data. If they want the original file, they click 'Download Resume'. This generates a secure, temporary pre-signed URL from AWS S3, ensuring our storage bucket remains private and safe."

---

## ⏱️ Phase 3: The Cloud Architecture (2 Minutes)
*Time to hit the Cloud Computing criteria from your Cover Sheet!*

**What to say:**
> "Let's talk about our cloud architecture. We built this to be 100% free using the AWS Free Tier.
> 1. **Compute:** Everything runs on a single AWS EC2 t2.micro instance.
> 2. **Storage:** Relational data is in a MySQL database, while binary CV files are stored in AWS S3. 
> 3. **Containers:** We used Docker to package our system into two microservices: the FastAPI backend (Port 80) and the BERT AI Service (Port 8001). They talk to each other over an internal Docker network, keeping the AI port completely hidden from the public internet for security.
> 4. **Security:** Our API uses CORS to only accept traffic from our frontend, and AWS Security Groups restrict access to only the necessary ports."

---

## ⏱️ Phase 4: The AI & Machine Learning (2 Minutes)
*Time to hit the AI & ML criteria from your Cover Sheet!*

**What to say:**
> "For the AI component, we didn't just use a basic API. We fine-tuned our own Named Entity Recognition (NER) model.
> We started with Hugging Face's `distilbert-base-uncased` because it is lightweight enough to run on our free EC2 server.
> We fine-tuned it on a custom dataset combining Kaggle resumes and the SkillSpan dataset to recognize specific tokens: `SKILL`, `EDU`, and `EXP`."

*Open your `MODEL_EVALUATION.md` file or have the numbers memorized:*
> "Our evaluation proved the fine-tuning worked. The base model only had an F1-Score of 0.37 for extracting skills. Our fine-tuned model achieved an **F1-Score of 0.81** (an 84% Precision rate). That is a massive 44% improvement in accuracy."

---

## ⏱️ Phase 5: Testing & Metrics (1 Minute)
*If you have terminal access, you can run the test scripts live, otherwise just show the output screenshots or talk about them.*

**What to say:**
> "To prove our platform is production-ready, we wrote three automated testing scripts:
> 1. An **AI Evaluation Script** that calculates our Precision and Recall.
> 2. An **API Integration Test** that proves our JWT authentication successfully blocks unauthorized users.
> 3. A **Cloud Load Test**. We blasted our EC2 server with 500 requests from 50 concurrent users. The server handled 97 requests per second with a 100% success rate and zero crashes."

---

## ⏱️ Phase 6: Conclusion
**What to say:**
> "In conclusion, we successfully integrated a custom machine learning pipeline into a modern, scalable cloud architecture, fully deployed and running at zero cost. Thank you, and we are happy to answer any questions!"
