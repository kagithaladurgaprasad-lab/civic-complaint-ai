def get_department(category):

    departments = {

        "Pothole": "Roads Department",

        "Garbage": "Sanitation Department",

        "Streetlight": "Electrical Department",

        "Drainage": "Water and Drainage Department",

        "Other": "General Municipal Department"
    }

    return departments.get(
        category,
        "General Municipal Department"
    )