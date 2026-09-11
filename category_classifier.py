def classify_complaint(title, description):

    text = f"{title} {description}".lower()


    # ========================================
    # Water Leakage
    # ========================================

    if any(word in text for word in [
        "water pipe",
        "water leakage",
        "water leak",
        "pipe leakage",
        "pipe leak",
        "leaking pipe",
        "leakage from pipe",
        "pipeline leakage",
        "pipeline leak",
        "water is leaking",
        "water leaking",
        "leaking water pipe"
    ]):
        return "Water Leakage"


    # ========================================
    # Pothole
    # ========================================

    if any(word in text for word in [
        "pothole",
        "road hole",
        "road damage",
        "broken road"
    ]):
        return "Pothole"


    # ========================================
    # Garbage
    # ========================================

    if any(word in text for word in [
        "garbage",
        "waste",
        "trash",
        "litter",
        "dump"
    ]):
        return "Garbage"


    # ========================================
    # Streetlight
    # ========================================

    if any(word in text for word in [
        "streetlight",
        "street light",
        "lamp",
        "light not working",
        "dark road"
    ]):
        return "Streetlight"


    # ========================================
    # Drainage
    # ========================================

    if any(word in text for word in [
        "drain",
        "drainage",
        "sewage",
        "water logging",
        "waterlogging",
        "manhole",
        "clogged drain",
        "drain overflow"
    ]):
        return "Drainage"


    # ========================================
    # Default
    # ========================================

    return "Other"