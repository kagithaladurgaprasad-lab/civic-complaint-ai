from search_complaints import search_complaints
from search_images import search_similar_images
from utils import calculate_distance


def calculate_location_score(distance_meters, max_distance=500):
    """Convert geographic distance into a similarity score.

    0 meters      -> 1.0
    500+ meters   -> 0.0
    """
    if distance_meters >= max_distance:
        return 0.0

    return 1 - (distance_meters / max_distance)


def detect_duplicate(
    text, image_path, latitude, longitude, category, top_k=5
):
    print(f"[DUPLICATE] Category: {category}")

    # 1. SEARCH HISTORICAL COMPLAINTS
    print("[DUPLICATE] Running text duplicate search...")
    text_results = search_complaints(
        query=text, category=category, top_k=top_k
    )
    print(
        f"[DUPLICATE] Text duplicate search completed. Results: {len(text_results)}"
    )

    # 2. CATEGORY-AWARE IMAGE SEARCH
    image_results = []
    if category == "Pothole":
        print("[DUPLICATE] Running image duplicate search...")
        image_results = search_similar_images(
            image_path=image_path, top_k=top_k
        )
        print(
            f"[DUPLICATE] Image duplicate search completed. Results: {len(image_results)}"
        )

    # 3. VISUAL EVIDENCE
    visual_evidence = []
    for result in image_results:
        payload = result.payload or {}
        visual_evidence.append({
            "image_id": payload.get("image_id", "Unknown"),
            "image_path": payload.get("image_path", "Unknown"),
            "category": payload.get("category", "Unknown"),
            "source": payload.get("source", "Unknown"),
            "image_similarity": round(result.score, 4),
        })

    # 4. HISTORICAL COMPLAINT ANALYSIS
    candidates = []
    for result in text_results:
        payload = result.payload or {}
        complaint_id = payload.get("complaint_id")
        text_score = result.score

        # Geographic similarity
        old_lat = payload.get("latitude")
        old_lon = payload.get("longitude")

        if old_lat is not None and old_lon is not None:
            distance = calculate_distance(
                latitude, longitude, old_lat, old_lon
            )
            location_score = calculate_location_score(distance)
        else:
            distance = None
            location_score = 0.0

        category_score = 1.0

        final_score = (
            0.65 * text_score + 0.30 * location_score + 0.05 * category_score
        )

        candidates.append({
            "complaint_id": complaint_id,
            "title": payload.get("title", "Unknown"),
            "description": payload.get("description", "Unknown"),
            "category": payload.get("category", "Unknown"),
            "department": payload.get("department", "Unknown"),
            "latitude": old_lat,
            "longitude": old_lon,
            "text_score": round(text_score, 4),
            "location_score": round(location_score, 4),
            "distance_meters": (
                round(distance, 2) if distance is not None else None
            ),
            "final_score": round(final_score, 4),
        })

    # 5. SORT HISTORICAL CANDIDATES
    candidates.sort(key=lambda x: x["final_score"], reverse=True)

    # 6. DUPLICATE DECISION
    if candidates:
        best_match = candidates[0]
        distance = best_match.get("distance_meters")
        text_score = best_match.get("text_score", 0)

        if distance is not None:
            if distance <= 100 and text_score >= 0.80:
                decision = "DUPLICATE"
            elif distance <= 500 and text_score >= 0.70:
                decision = "POSSIBLY_RELATED"
            else:
                decision = "NEW"
        else:
            if text_score >= 0.85:
                decision = "DUPLICATE"
            elif text_score >= 0.70:
                decision = "POSSIBLY_RELATED"
            else:
                decision = "NEW"
    else:
        best_match = None
        decision = "NEW"

    # 7. DEBUG RESULT & RETURN
    print(f"[DUPLICATE] Decision: {decision}")
    print(f"[DUPLICATE] Candidates: {len(candidates)}")

    return {
        "decision": decision,
        "best_match": best_match,
        "candidates": candidates,
        "visual_evidence": visual_evidence,
    }