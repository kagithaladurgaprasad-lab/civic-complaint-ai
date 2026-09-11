def get_urgency(title, description):

    text = f"{title} {description}".lower()


    # High urgency
    high_words = [
        "accident",
        "danger",
        "dangerous",
        "life threatening",
        "emergency",
        "fire",
        "collapsed",
        "electric shock",
        "exposed wire",
        "major leak",
        "flooding",
        "blocked road"
    ]

    if any(word in text for word in high_words):

        return "High"


    # Medium urgency
    medium_words = [
        "large pothole",
        "overflowing",
        "broken streetlight",
        "sewage",
        "water leakage",
        "road damage",
        "bad smell"
    ]

    if any(word in text for word in medium_words):

        return "Medium"


    # Default
    return "Low"