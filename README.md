# 🏙️ Civic Complaint AI

An AI-powered multimodal municipal complaint triage system that helps classify civic complaints, detect duplicate complaints, retrieve official municipal SLA information, and generate evidence-grounded AI analysis.

## 📌 Problem Statement

Municipal offices receive a large number of complaints related to:

- Road potholes and damage
- Garbage and waste
- Streetlights
- Drainage and sewage
- Water leakage
- Other civic issues

Manually reviewing these complaints can be time-consuming. Staff may need to identify the responsible department, determine urgency, check whether a similar complaint already exists, and refer to municipal service-level information.

**Civic Complaint AI** automates these tasks using NLP, multimodal embeddings, vector search, RAG, and an LLM.

---

## 💡 Solution

A citizen submits:

- Complaint title
- Complaint description
- Location (latitude/longitude)
- Complaint image

The system then:

1. Classifies the complaint.
2. Assigns the responsible department.
3. Determines urgency.
4. Searches historical complaints using semantic similarity.
5. Uses image similarity for visual duplicate evidence.
6. Uses geographic distance as supporting evidence.
7. Retrieves official municipal SLA information.
8. Builds a grounded RAG context.
9. Uses Gemini to generate an evidence-based analysis.
10. Stores the analysis and decision in the database.
11. Provides the result to municipal staff through an admin dashboard.

---

## 🏗️ Architecture

```text
                    Citizen
                       │
                       ▼
              Streamlit Web App
                       │
                       ▼
                 FastAPI API
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   Text Classification        Image Processing
          │                         │
          ▼                         ▼
 Category / Department        CLIP Embedding
 / Urgency                         │
          │                         │
          └────────────┬────────────┘
                       ▼
                 Qdrant Vector DB
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
     Historical    Municipal    Image
     Complaints    Documents    Embeddings
          │            │            │
          └────────────┼────────────┘
                       ▼
                RAG Context Builder
                       │
                       ▼
                   Gemini LLM
                       │
                       ▼
              AI Complaint Analysis
                       │
                       ▼
                  SQLite Database
                       │
                       ▼
                Admin Dashboard
