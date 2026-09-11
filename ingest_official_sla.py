
import requests
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from vector_db import (
    client,
    DOCUMENT_COLLECTION
)


BASE_URL = (
    "https://apcmms.ap.gov.in/apiv1"
)

DEPARTMENTS = {
    1000000: "Administration",
    1000002: "Engineering",
    1000003: "Public Health and Sanitation",
    4000002: "Revenue",
    1000001: "Town Planning",
    4000003: "Urban Poverty Allevation"
}


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def fetch_sla_data(
    department_id,
    department_name
):
    url = (
        f"{BASE_URL}/public/web/grievances/"
        f"{department_id}/sla-info"
    )

    print(
        f"\nFetching SLA data for "
        f"{department_name}..."
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    data = result.get(
        "data",
        []
    )

    # API response contains multiple arrays.
    # The SLA records are the array containing
    # tckt_sb_ctgry_nm and sla_dy_ct.
    sla_rows = []

    for group in data:
        if not isinstance(group, list):
            continue

        for row in group:
            if (
                isinstance(row, dict)
                and "tckt_sb_ctgry_nm" in row
                and "sla_dy_ct" in row
            ):
                sla_rows.append(row)

    return sla_rows


def main():

    all_sla_rows = []

    for department_id, department_name in DEPARTMENTS.items():

        try:

            rows = fetch_sla_data(
                department_id,
                department_name
            )

            print(
                f"Found {len(rows)} SLA records."
            )

            all_sla_rows.extend(rows)

        except Exception as e:

            print(
                f"ERROR fetching "
                f"{department_name}: {e}"
            )


    if not all_sla_rows:

        print(
            "\nNo SLA records found."
        )

        return


    points = []

    for index, row in enumerate(
        all_sla_rows,
        start=1
    ):

        department = row.get(
            "dprt_nm",
            "Unknown"
        )

        category = row.get(
            "tckt_ctgry_nm",
            "Unknown"
        )

        sub_category = row.get(
            "tckt_sb_ctgry_nm",
            "Unknown"
        )

        sla_days = row.get(
            "sla_dy_ct"
        )

        text = f"""
Official Municipal Service Level Agreement

Department: {department}

Category: {category}

Service: {sub_category}

Maximum Resolution Time: {sla_days} days

Source: Andhra Pradesh CDMA Grievance SLA API
"""

        embedding = model.encode(
            text
        ).tolist()

        point = PointStruct(
            id=100000 + index,
            vector=embedding,
            payload={
                "document_id": (
                    f"CDMA-SLA-{index}"
                ),
                "title": (
                    "CDMA Grievance Service "
                    "Level Agreement"
                ),
                "source": (
                    "AP CDMA Official SLA API"
                ),
                "document_type": "SLA",
                "department": department,
                "category": category,
                "sub_category": sub_category,
                "sla_days": sla_days,
                "text": text
            }
        )

        points.append(point)

        print(
            f"{index}. "
            f"{department} | "
            f"{category} | "
            f"{sub_category} | "
            f"{sla_days} days"
        )


    print(
        f"\nUploading {len(points)} "
        f"SLA records to Qdrant..."
    )

    client.upsert(
        collection_name=DOCUMENT_COLLECTION,
        points=points
    )

    print(
        "\nSuccessfully stored official "
        "SLA records in Qdrant."
    )


if __name__ == "__main__":
    main()

