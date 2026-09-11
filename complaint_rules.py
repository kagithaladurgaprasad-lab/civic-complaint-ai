CATEGORY_RULES = {

    "Pothole": {
        "department": "Roads",
        "urgency": "High"
    },

    "Garbage": {
        "department": "Sanitation",
        "urgency": "Medium"
    },

    "Streetlight": {
        "department": "Electrical",
        "urgency": "Medium"
    },

    "Water Leakage": {
        "department": "Engineering",
        "urgency": "High"
    },

    "Drainage": {
        "department": "Drainage",
        "urgency": "High"
    },

    "Other": {
        "department": "General Municipal Department",
        "urgency": "Low"
    }
}


def get_complaint_rules(category):

    return CATEGORY_RULES.get(
        category,
        CATEGORY_RULES["Other"]
    )