# 🏙️ Civic Complaint AI

### Multimodal RAG-Based Municipal Complaint Triage System

Civic Complaint AI is an AI-powered municipal complaint triage application that helps municipal staff process citizen complaints more efficiently.

A citizen can submit a **complaint description, location, and image**. The system analyzes the complaint, identifies the civic issue and responsible department, estimates urgency, searches for similar historical complaints, checks visual similarity, retrieves official municipal SLA information, and generates an evidence-grounded AI analysis.

The application is designed as a **multimodal Retrieval-Augmented Generation (RAG) system** using text embeddings, image embeddings, vector search, official municipal documents, and Gemini.

---

## 🎯 Problem Statement

Municipal departments receive complaints about issues such as:

* Road potholes
* Garbage accumulation
* Broken streetlights
* Drainage problems
* Water leakage
* Other civic infrastructure problems

Manually processing these complaints can require staff to:

1. Read the complaint.
2. Identify the issue.
3. Determine the responsible department.
4. Estimate urgency.
5. Check whether a similar complaint already exists.
6. Review relevant municipal service information.
7. Decide what action should be taken.

This process can be time-consuming, especially when complaint volumes are high.

### Proposed Solution

Civic Complaint AI provides an automated first-level triage system that prepares a complaint for **municipal staff review**.

It does not replace municipal decision-making. Instead, it provides evidence and structured analysis to support staff.

---

# 🚀 Key Features

## 1. Complaint Classification

The system identifies the complaint category using the complaint title and description.

Supported categories:

| Category      | Department                   | Default Urgency |
| ------------- | ---------------------------- | --------------- |
| Pothole       | Roads                        | High            |
| Garbage       | Sanitation                   | Medium          |
| Streetlight   | Electrical                   | Medium          |
| Water Leakage | Engineering                  | High            |
| Drainage      | Drainage                     | High            |
| Other         | General Municipal Department | Low             |

The classification and default routing are handled by the application's processing rules.

---

## 2. Multimodal Duplicate Detection

Duplicate detection uses multiple signals rather than relying on only one similarity score.

### Text Evidence

Historical complaints are converted into embeddings using:

**`all-MiniLM-L6-v2`**

Semantic similarity is then calculated using Qdrant vector search.

### Image Evidence

Complaint images are converted into embeddings using:

**CLIP — `openai/clip-vit-base-patch32`**

Visual similarity is used as supporting evidence, particularly for pothole complaints.

### Location Evidence

The system also compares the geographic distance between the current complaint and historical complaints.

### Combined Decision

The duplicate detection pipeline considers:

```text
             Current Complaint
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   Text Search  Image Search  Location
        │           │           │
        └───────────┼───────────┘
                    ▼
             Evidence Analysis
                    │
                    ▼
          Duplicate Assessment
```

The system produces:

* `DUPLICATE`
* `POSSIBLY_RELATED`
* `NEW`

Similarity alone is not treated as proof that two complaints are duplicates.

---

# 📚 Retrieval-Augmented Generation

The project uses RAG to provide relevant evidence to the LLM before generating the complaint analysis.

The retrieval sources include:

### Historical Complaints

Historical civic complaints are stored as vector embeddings in Qdrant.

They are used to find:

* Similar complaints
* Repeated issues
* Potential duplicate complaints
* Similar complaint patterns

### Official Municipal Documents

Official municipal grievance and SLA information is ingested and stored for retrieval.

Official municipal information is given higher priority than historical complaint data when providing municipal guidance.

---

# 🏛️ Official Municipal SLA Integration

The project integrates official Andhra Pradesh municipal grievance/SLA information.

Examples of retrieved SLA information include:

| Municipal Service                              |     SLA |
| ---------------------------------------------- | ------: |
| Pot holes fill up / repairs to damaged surface | 30 days |
| Non-burning of street lights                   |  3 days |
| Water pipe leakage                             |  3 days |
| UGD / drain manhole clogging                   |   1 day |

The retrieved municipal information is used as supporting evidence in the RAG pipeline.

The application does **not** allow the LLM to invent municipal deadlines or procedures when the required information is unavailable.

---

# 🤖 Grounded Gemini Analysis

After retrieval, the system builds a RAG context containing information such as:

* Current complaint
* Category
* Department
* Urgency
* Similar historical complaints
* Text similarity
* Location evidence
* Image similarity evidence
* Official municipal documents
* Municipal SLA information

This context is passed to Gemini.

The LLM is instructed to remain grounded in the retrieved evidence.

### Generated Analysis

The AI analysis contains:

```text
Complaint Summary
Category
Responsible Department
Urgency
Duplicate Assessment
Evidence
Municipal Guidance
Recommended Action
Confidence
Source Notes
```

The system also applies hallucination controls.

The LLM is instructed not to fabricate:

* Complaint IDs
* Government rules
* Municipal procedures
* SLA deadlines
* Statistics
* Locations
* URLs
* Sources
* Department procedures

When evidence is unavailable, the system is instructed to explicitly report insufficient information.

---

# 🔐 Authentication and Authorization

The backend uses JWT-based authentication.

### Authentication Flow

```text
User Registration
       ↓
Password Hashing
       ↓
SQLite User Record
       ↓
Login
       ↓
JWT Access Token
       ↓
Protected API Endpoints
```

The application supports:

### Citizen

Citizens can:

* Register
* Login
* Submit complaints
* Upload complaint images
* View their complaints
* View complaint analysis

### Admin

Administrators can:

* View all complaints
* View complaint details
* Review AI analysis
* Review duplicate evidence
* Review municipal SLA information
* Update complaint status

Public registration creates users with the `citizen` role. Admin privileges are assigned separately.

---

# 🗄️ Data Storage

The application uses different storage systems for different types of information.

### SQLite

SQLite stores application data such as:

* Users
* Complaints
* Complaint status
* AI analysis
* Duplicate decision
* Municipal SLA information

### Qdrant

Qdrant stores vector embeddings for:

* Historical complaints
* Complaint images
* Municipal documents

This separation allows structured application data and semantic search data to be handled independently.

---

# ⚡ Processing Architecture

```text
                    Citizen
                       │
                       ▼
                Streamlit UI
                       │
                       ▼
                  FastAPI API
                       │
                       ▼
             Complaint Processing
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Text         Image        Location
    Processing    Processing     Evidence
          │            │            │
          ▼            ▼            │
      Category       CLIP           │
      Department    Embedding        │
      Urgency          │            │
          │            ▼            │
          │         Qdrant          │
          │            │            │
          └────────────┼────────────┘
                       ▼
                Historical Search
                       │
                       ▼
               Document Retrieval
                       │
                       ▼
                 RAG Context
                       │
                       ▼
                  Gemini LLM
                       │
                       ▼
                AI Analysis
                       │
                       ▼
                  SQLite
                       │
                       ▼
               Admin Dashboard
```

---

# 🔄 End-to-End Workflow

When a citizen submits a complaint:

### Step 1 — Complaint Submission

The citizen provides:

* Title
* Description
* Latitude
* Longitude
* Image

### Step 2 — Category Detection

The complaint is classified into one of the supported civic categories.

### Step 3 — Department and Urgency

The category is mapped to a responsible department and default urgency.

### Step 4 — Historical Complaint Retrieval

The complaint text is converted into an embedding and searched against historical complaints in Qdrant.

### Step 5 — Image Retrieval

For supported image-based duplicate detection, the complaint image is converted into a CLIP embedding and compared against stored images.

### Step 6 — Location Verification

The geographic distance between the current complaint and historical candidates is calculated.

### Step 7 — Duplicate Assessment

Text similarity, location evidence, category, and visual evidence are combined to determine whether the complaint is:

```text
DUPLICATE
POSSIBLY_RELATED
NEW
```

### Step 8 — Municipal Document Retrieval

Relevant official municipal documents and SLA information are retrieved from Qdrant.

### Step 9 — RAG Context Construction

All relevant evidence is combined into a structured context.

### Step 10 — Gemini Analysis

Gemini generates a grounded complaint analysis.

### Step 11 — Persistence

The following results are saved in SQLite:

* AI analysis
* Duplicate decision
* Municipal SLA
* SLA service
* SLA department
* SLA source

### Step 12 — Staff Review

Municipal staff can review the prepared complaint through the admin dashboard.

---

# 💾 Result Persistence

AI and retrieval processing occurs when a complaint is submitted.

The generated results are saved in the application database.

When an administrator later opens the complaint details, the application reads the saved analysis instead of running the entire RAG pipeline again.

```text
Complaint Submitted
       ↓
RAG + Gemini Processing
       ↓
Save Results to SQLite
       ↓
Admin Opens Complaint
       ↓
Read Saved Results
```

This avoids unnecessary repeated LLM and vector-database processing.

---

# 🛠️ Technology Stack

| Technology            | Purpose                         |
| --------------------- | ------------------------------- |
| Python                | Application development         |
| FastAPI               | Backend REST API                |
| Streamlit             | Web interface                   |
| SQLite                | Structured application database |
| SQLAlchemy            | Database ORM                    |
| Qdrant                | Vector database                 |
| Sentence Transformers | Text embeddings                 |
| all-MiniLM-L6-v2      | Complaint text embeddings       |
| CLIP                  | Image embeddings                |
| Gemini                | LLM-based complaint analysis    |
| Pydantic              | Request/response validation     |
| JWT                   | Authentication                  |
| bcrypt                | Password hashing                |

---

# 📂 Project Structure

```text
civic_complaint_rag/
│
├── app.py
├── main.py
│
├── auth.py
├── database.py
├── models.py
├── schemas.py
│
├── category_classifier.py
├── department_classifier.py
├── complaint_rules.py
├── complaint_pipeline.py
├── urgency_classifier.py
│
├── duplicate_detector.py
├── nearby_search.py
├── utils.py
│
├── complaint_embeddings.py
├── image_embeddings.py
├── search_complaints.py
├── search_images.py
│
├── document_ingestion.py
├── document_retrieval.py
├── retrieval.py
├── rag_context.py
│
├── llm_service.py
├── vector_db.py
│
├── download_311.py
├── prepare_311.py
├── ingest_311.py
├── ingest_complaints.py
├── ingest_images.py
│
├── ingest_official_cdma.py
├── ingest_official_sla.py
│
├── cleanup_image_collection.py
├── verify_qdrant.py
├── test_distance.py
│
├── sla_chunk.js
├── sla_page.html
│
├── .gitignore
└── README.md
```

> Local datasets, uploaded images, Qdrant storage, SQLite database files, virtual environments, and environment variables are excluded from Git using `.gitignore`.

---

# 🔌 API Endpoints

| Method | Endpoint                         | Description                        |
| ------ | -------------------------------- | ---------------------------------- |
| `GET`  | `/`                              | API health message                 |
| `POST` | `/register`                      | Register a citizen                 |
| `POST` | `/login`                         | Authenticate user                  |
| `POST` | `/complaints`                    | Submit a complaint                 |
| `GET`  | `/my-complaints`                 | Get current user's complaints      |
| `GET`  | `/admin/complaints`              | Get all complaints                 |
| `GET`  | `/admin/complaints/{id}/details` | Get detailed complaint information |
| `PUT`  | `/admin/complaints/{id}/status`  | Update complaint status            |

Interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# 🖥️ Running the Project

## 1. Clone the Repository

```bash
git clone https://github.com/kagithaladurgaprasad-lab/civic-complaint-ai.git
cd civic-complaint-ai
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

## 3. Install Dependencies

Install the Python packages required by the project.

```bash
pip install fastapi uvicorn streamlit sqlalchemy python-dotenv python-jose passlib[bcrypt] python-multipart email-validator sentence-transformers qdrant-client google-genai torch transformers pillow requests
```

## 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_random_jwt_secret
```

Do not commit `.env` to GitHub.

## 5. Start FastAPI

```bash
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 6. Start Streamlit

Open another terminal:

```bash
streamlit run app.py
```

---

# 🧪 Example Complaint

### Input

```text
Title:
Deep pothole near railway station

Description:
There is a deep pothole on the road near the railway station.
It is creating difficulty for vehicles and may cause accidents.
```

The citizen also provides:

```text
Latitude
Longitude
Image
```

### Processing

```text
Complaint
   ↓
Pothole
   ↓
Roads
   ↓
High Urgency
   ↓
Historical Complaint Search
   ↓
Image Similarity
   ↓
Location Comparison
   ↓
Duplicate Assessment
   ↓
Official SLA Retrieval
   ↓
RAG Context
   ↓
Gemini
   ↓
AI Analysis
```

---

# 🧠 Duplicate Detection Example

A complaint with highly similar text but a distant location should not automatically be treated as a duplicate.

For example:

```text
High Text Similarity
+
Large Geographic Distance
        ↓
Not necessarily a duplicate
```

A complaint with:

```text
High Text Similarity
+
Very Close Location
+
Supporting Image Evidence
        ↓
Strong Duplicate Evidence
```

This approach is intended to reduce false duplicate classifications.

---

# 📊 Data Used

The project uses historical civic complaint data for semantic retrieval and duplicate detection.

A prepared subset of NYC 311 complaint data was used during development and testing.

The project also uses official Andhra Pradesh municipal grievance/SLA information for municipal guidance.

Large datasets and local vector storage are intentionally excluded from the GitHub repository.

---

# 🔒 Security Considerations

The project follows several basic security practices:

* API keys are stored in environment variables.
* JWT secrets are stored in environment variables.
* `.env` is excluded from Git.
* Passwords are hashed before storage.
* Protected API endpoints require authentication.
* Admin endpoints require the `admin` role.
* Public registration cannot directly select the admin role.

For production deployment, additional security measures would be required.

---

# ⚠️ Limitations

This is a portfolio and demonstration project rather than a production municipal system.

Current limitations include:

* Rule-based initial complaint classification.
* Local SQLite database.
* Local Qdrant configuration.
* Limited municipal datasets.
* Limited image dataset.
* Duplicate detection thresholds require further validation.
* Official SLA coverage depends on the retrieved municipal data.
* AI output depends on the quality and relevance of retrieved evidence.

The system therefore presents AI analysis as **decision support**, not as a final municipal decision.

---

# 🔮 Future Improvements

Potential improvements include:

* PostgreSQL for production database storage.
* Cloud-hosted Qdrant.
* Improved multimodal reranking.
* Larger civic image datasets.
* More municipal departments and categories.
* Better geographic indexing.
* Complaint notifications.
* Email/SMS status updates.
* Production logging and monitoring.
* Docker-based deployment.
* Cloud deployment.
* Automated evaluation of retrieval quality.
* Automated evaluation of duplicate-detection precision and recall.
* Role-based permissions with more granular administrative roles.

---

# 🎓 What This Project Demonstrates

This project demonstrates practical experience with:

### Machine Learning / NLP

* Text preprocessing
* Text embeddings
* Semantic similarity
* Classification
* Similarity-based retrieval

### Generative AI

* Large Language Models
* Retrieval-Augmented Generation
* Prompt engineering
* Grounded generation
* Hallucination control
* Evidence-based generation

### Multimodal AI

* Image embeddings
* CLIP
* Text + image evidence
* Multimodal duplicate detection

### Vector Databases

* Qdrant
* Vector collections
* Embedding storage
* Similarity search
* Metadata filtering

### Backend Development

* FastAPI
* REST APIs
* JWT authentication
* SQLAlchemy
* Pydantic
* SQLite

### Application Development

* Streamlit
* API integration
* Authentication UI
* Admin dashboard
* Complaint management

---

# 📌 Project Highlights

**Problem:** Manual municipal complaint triage.

**Solution:** Multimodal AI + RAG-based complaint processing.

**Input:** Text + image + geographic location.

**Retrieval:** Historical complaints + official municipal documents.

**Vector Search:** Qdrant.

**Text Embeddings:** Sentence Transformers.

**Image Embeddings:** CLIP.

**LLM:** Gemini.

**Backend:** FastAPI.

**Frontend:** Streamlit.

**Database:** SQLite.

**Authentication:** JWT.

**Output:** Structured, evidence-grounded complaint analysis for municipal staff review.

---

# 👨‍💻 Author

## Durga Prasad

**AI/ML | Generative AI | NLP | RAG | Computer Vision**

This project was developed as an AI/ML portfolio project to demonstrate practical implementation of multimodal retrieval, RAG, LLM integration, vector databases, API development, and AI-assisted complaint triage.

---

# 📄 License

This project is intended for educational, portfolio, and demonstration purposes.
