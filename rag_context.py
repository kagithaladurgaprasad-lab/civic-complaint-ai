
def build_rag_context(
    complaint,
    similar_complaints,
    documents,
    visual_evidence=None,
    duplicate_decision="NEW"
):

    context = []

    # ==========================================
    # CURRENT COMPLAINT
    # ==========================================

    context.append(
        "=== CURRENT COMPLAINT ==="
    )

    context.append(
        f"""
Title: {complaint.get('title', 'Unknown')}
Description: {complaint.get('description', 'Unknown')}
Category: {complaint.get('category', 'Unknown')}
Department: {complaint.get('department', 'Unknown')}
Urgency: {complaint.get('urgency', 'Unknown')}
"""
    )

    # ==========================================
    # DETERMINISTIC DUPLICATE DECISION
    # ==========================================

    context.append(
        "\n=== DUPLICATE DETECTOR DECISION ==="
    )

    context.append(
        f"""
System Duplicate Decision: {duplicate_decision}

IMPORTANT:
The duplicate detector is the authoritative source for
the duplicate classification.

Gemini MUST NOT change this decision.

Map the system decision to the required output label:

DUPLICATE -> Likely Duplicate
POSSIBLY_RELATED -> Possibly Related
NEW -> Not a Duplicate

Use the system decision exactly as provided.
Historical similarity alone must not override it.
"""
    )

    # ==========================================
    # SIMILAR HISTORICAL COMPLAINTS
    # ==========================================

    context.append(
        "\n=== SIMILAR HISTORICAL COMPLAINTS ==="
    )

    if similar_complaints:

        for item in similar_complaints:

            complaint_id = item.get(
                "complaint_id",
                "Unknown"
            )

            text_score = item.get(
                "text_score",
                0
            )

            location_score = item.get(
                "location_score",
                0
            )

            distance = item.get(
                "distance_meters"
            )

            final_score = item.get(
                "final_score",
                0
            )

            title = item.get(
                "title",
                "Unknown"
            )

            description = item.get(
                "description",
                "Unknown"
            )

            category = item.get(
                "category",
                "Unknown"
            )

            department = item.get(
                "department",
                "Unknown"
            )

            context.append(
                f"""
Complaint ID: {complaint_id}
Title: {title}
Description: {description}
Category: {category}
Department: {department}

Text Similarity: {text_score}
Location Score: {location_score}
Distance: {distance} meters
Final Duplicate Score: {final_score}
"""
            )

    else:

        context.append(
            "No similar historical complaints were retrieved."
        )

    # ==========================================
    # VISUAL EVIDENCE
    # ==========================================

    context.append(
        "\n=== VISUAL EVIDENCE ==="
    )

    if visual_evidence:

        for item in visual_evidence:

            image_id = item.get(
                "image_id",
                "Unknown"
            )

            category = item.get(
                "category",
                "Unknown"
            )

            source = item.get(
                "source",
                "Unknown"
            )

            image_similarity = item.get(
                "image_similarity",
                0
            )

            context.append(
                f"""
Image ID: {image_id}
Category: {category}
Source: {source}
Visual Similarity: {image_similarity}
"""
            )

    else:

        context.append(
            "No visually similar reference images were retrieved."
        )

    # ==========================================
    # MUNICIPAL DOCUMENTS
    # ==========================================

    context.append(
        "\n=== MUNICIPAL DOCUMENTS ==="
    )

    # Keep track of SLA records separately
    sla_documents = []

    other_documents = []

    if documents:

        for document in documents:

            # ----------------------------------
            # Handle dictionary returned by
            # document_retrieval.py
            # ----------------------------------

            if isinstance(
                document,
                dict
            ):

                payload = document

                similarity = document.get(
                    "similarity_score",
                    document.get(
                        "score"
                    )
                )

            # ----------------------------------
            # Handle raw Qdrant object
            # ----------------------------------

            elif hasattr(
                document,
                "payload"
            ):

                payload = document.payload or {}

                similarity = getattr(
                    document,
                    "score",
                    None
                )

            else:

                payload = {}

                similarity = None

            # ----------------------------------
            # Extract document information
            # ----------------------------------

            source_id = payload.get(
                "source_id",
                payload.get(
                    "document_id",
                    "Unknown"
                )
            )

            document_title = payload.get(
                "title",
                payload.get(
                    "document_title",
                    "Unknown Document"
                )
            )

            source = payload.get(
                "source",
                "Unknown Source"
            )

            content = payload.get(
                "text",
                payload.get(
                    "content",
                    ""
                )
            )

            document_type = payload.get(
                "document_type",
                ""
            )

            department = payload.get(
                "department",
                ""
            )

            category = payload.get(
                "category",
                ""
            )

            sub_category = payload.get(
                "sub_category",
                ""
            )

            sla_days = payload.get(
                "sla_days"
            )

            # ----------------------------------
            # Identify official SLA records
            # ----------------------------------

            if (
                document_type == "SLA"
                or sla_days is not None
            ):

                sla_documents.append(
                    {
                        "source_id": source_id,
                        "title": document_title,
                        "source": source,
                        "department": department,
                        "category": category,
                        "sub_category": sub_category,
                        "sla_days": sla_days,
                        "text": content,
                        "similarity": similarity
                    }
                )

            else:

                other_documents.append(
                    {
                        "source_id": source_id,
                        "title": document_title,
                        "source": source,
                        "text": content,
                        "similarity": similarity
                    }
                )

    # ==========================================
    # OFFICIAL SLA EVIDENCE
    # ==========================================

    context.append(
        "\n=== OFFICIAL MUNICIPAL SLA ==="
    )

    if sla_documents:

        context.append(
            """
IMPORTANT:
The following records come from the official
AP CDMA Grievance SLA API.

Use these records as the authoritative source
for municipal service resolution timelines.

Do NOT invent or estimate an SLA.

If a relevant SLA record is available, report
the stated maximum resolution time.

If no relevant SLA is available, explicitly say
that the SLA was not found in the retrieved
official records.
"""
        )

        for index, item in enumerate(
            sla_documents,
            start=1
        ):

            context.append(
                f"""
[SLA-{index}]

Source ID: {item['source_id']}
Document Title: {item['title']}
Source: {item['source']}

Department: {item['department']}
Category: {item['category']}
Service: {item['sub_category']}

Maximum Resolution Time:
{item['sla_days']} days

Similarity Score:
{item['similarity']}

Official SLA Record:
{item['text']}
"""
            )

    else:

        context.append(
            """
No official SLA record was retrieved for
this complaint.
Do not invent an SLA value.
"""
        )

    # ==========================================
    # OTHER MUNICIPAL DOCUMENTS
    # ==========================================

    context.append(
        "\n=== OTHER MUNICIPAL DOCUMENTS ==="
    )

    if other_documents:

        for index, item in enumerate(
            other_documents,
            start=1
        ):

            context.append(
                f"""
[DOC-{index}]

Source ID: {item['source_id']}

Document Title:
{item['title']}

Source:
{item['source']}

Similarity Score:
{item['similarity']}

Content:
{item['text']}
"""
            )

    else:

        context.append(
            "No additional municipal documents were retrieved."
        )

    # ==========================================
    # FINAL RAG CONTEXT
    # ==========================================

    final_context = "\n".join(
        context
    )

    return final_context

