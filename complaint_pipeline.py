from category_classifier import classify_complaint
from complaint_rules import get_complaint_rules

from duplicate_detector import detect_duplicate
from document_retrieval import retrieve_documents
from rag_context import build_rag_context
from llm_service import generate_complaint_analysis


# ============================================================
# EXTRACT MUNICIPAL SLA
# ============================================================

def extract_municipal_sla(documents, category):

    # ---------------------------------------------------------
    # 1. Keep only official SLA documents
    # ---------------------------------------------------------

    sla_documents = []

    for document in documents:

        if (
            document.get("document_type") == "SLA"
            and document.get("sla_days") is not None
        ):
            sla_documents.append(document)

    if not sla_documents:
        return None

    # ---------------------------------------------------------
    # 2. Exact service matching for known categories
    # ---------------------------------------------------------

    category_services = {

        "Pothole": [
            "pot holes fill up/repairs to the damaged surface",
            "pothole",
            "pot holes",
            "damaged surface"
        ],

        "Streetlight": [
            "non burning of street lights",
            "street light not working",
            "streetlight not working",
            "non-burning of street lights"
        ],

        "Drainage": [
            "manhole of ugd / clogging of drain",
            "clogging of drain",
            "repairs to open drain",
            "drainage",
            "manhole"
        ],

        "Garbage": [
            "garbage",
            "solid waste",
            "waste"
        ],

        "Water Leakage": [
            "water pipe leakage",
            "pipe leakage",
            "water leakage"
        ]
    }

    preferred_services = category_services.get(
        category,
        []
    )

    for preferred_service in preferred_services:

        for document in sla_documents:

            service = (
                document.get("sub_category") or ""
            ).strip().lower()

            if preferred_service.lower() in service:

                return {
                    "service": (
                        document.get("sub_category")
                        or document.get("title")
                        or "Unknown Service"
                    ),
                    "sla_days": int(
                        document["sla_days"]
                    ),
                    "department": (
                        document.get("department")
                        or "Unknown Department"
                    ),
                    "source": (
                        document.get("source")
                        or "Unknown Source"
                    ),
                    "source_id": document.get(
                        "source_id"
                    )
                }

    # ---------------------------------------------------------
    # 3. Special matching for Other complaints
    # ---------------------------------------------------------

    if category == "Other":

        # These keywords identify official services
        # related to parks and public greenery.

        park_keywords = [
            "park",
            "parks",
            "playground",
            "greenery",
            "garden"
        ]

        for document in sla_documents:

            service = (
                document.get("sub_category") or ""
            ).strip().lower()

            # Example:
            # "Maintenance of parks"
            #
            # This matches "park" / "parks".

            if any(
                keyword in service
                for keyword in park_keywords
            ):

                return {
                    "service": (
                        document.get("sub_category")
                        or document.get("title")
                        or "Unknown Service"
                    ),
                    "sla_days": int(
                        document["sla_days"]
                    ),
                    "department": (
                        document.get("department")
                        or "Unknown Department"
                    ),
                    "source": (
                        document.get("source")
                        or "Unknown Source"
                    ),
                    "source_id": document.get(
                        "source_id"
                    )
                }

    # ---------------------------------------------------------
    # 4. Generic semantic fallback for Other
    # ---------------------------------------------------------

    if category == "Other":

        OTHER_SLA_THRESHOLD = 0.65

        matching_sla = []

        for document in sla_documents:

            similarity = document.get(
                "similarity_score",
                0
            )

            if similarity >= OTHER_SLA_THRESHOLD:
                matching_sla.append(document)

        if matching_sla:

            best_sla = max(
                matching_sla,
                key=lambda x: x.get(
                    "similarity_score",
                    0
                )
            )

            return {
                "service": (
                    best_sla.get("sub_category")
                    or best_sla.get("title")
                    or "Unknown Service"
                ),
                "sla_days": int(
                    best_sla["sla_days"]
                ),
                "department": (
                    best_sla.get("department")
                    or "Unknown Department"
                ),
                "source": (
                    best_sla.get("source")
                    or "Unknown Source"
                ),
                "source_id": best_sla.get(
                    "source_id"
                )
            }

    # ---------------------------------------------------------
    # 5. No reliable SLA found
    # ---------------------------------------------------------

    return None


# ============================================================
# PROCESS COMPLAINT
# ============================================================

def process_complaint(
    title,
    description,
    latitude,
    longitude,
    image_path
):

    # ==========================================
    # 1. Classify complaint
    # ==========================================

    category = classify_complaint(
        title,
        description
    )

    # ==========================================
    # 2. Get department and urgency
    # ==========================================

    rules = get_complaint_rules(
        category
    )

    department = rules["department"]

    urgency = rules["urgency"]

    # ==========================================
    # 3. Create complaint information
    # ==========================================

    complaint = {

        "title": title,

        "description": description,

        "latitude": latitude,

        "longitude": longitude,

        "category": category,

        "department": department,

        "urgency": urgency
    }

    # ==========================================
    # 4. Create search text
    # ==========================================

    text = f"""
Title: {title}

Description: {description}

Category: {category}

Department: {department}
"""

    # ==========================================
    # 5. Duplicate Detection
    # ==========================================

    duplicate_result = detect_duplicate(

        text=f"{title} {description}",

        image_path=image_path,

        latitude=latitude,

        longitude=longitude,

        category=category
    )

    # ==========================================
    # 6. Retrieve Municipal Documents
    # ==========================================

    documents = retrieve_documents(

        query=text,

        top_k=5
    )

    # ==========================================
    # 7. Extract Official Municipal SLA
    # ==========================================

    municipal_sla = extract_municipal_sla(

        documents=documents,

        category=category
    )

    # ==========================================
    # 8. Similar Complaints
    # ==========================================

    similar_complaints = duplicate_result.get(
        "candidates",
        []
    )

    # ==========================================
    # 9. Build RAG Context
    # ==========================================

    rag_context = build_rag_context(

        complaint=complaint,

        similar_complaints=similar_complaints,

        documents=documents,

        visual_evidence=duplicate_result.get(
            "visual_evidence",
            []
        ),

        duplicate_decision=duplicate_result.get(
            "decision",
            "NEW"
        )
    )

    # ==========================================
    # 10. Gemini Analysis
    # ==========================================

    ai_analysis = generate_complaint_analysis(
        rag_context
    )

    # ==========================================
    # 11. Final Result
    # ==========================================

    return {

        "category": category,

        "department": department,

        "urgency": urgency,

        "duplicate": duplicate_result,

        "documents": documents,

        "municipal_sla": municipal_sla,

        "rag_context": rag_context,

        "ai_analysis": ai_analysis
    }