from fastapi import (
FastAPI,
Depends,
HTTPException,
UploadFile,
File,
Form
)

from schemas import (
UserCreate,
UserResponse,
Token,
ComplaintResponse,
ComplaintAnalysisResponse
)

from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordRequestForm

from database import (
engine,
Base,
get_db
)

from models import (
User,
Complaint
)

from auth import (
hash_password,
verify_password,
create_access_token,
verify_token
)

import os
import shutil

Base.metadata.create_all(bind=engine)

app = FastAPI(
title="Civic Complaint AI",
description=(
"AI-powered municipal complaint classification, "
"duplicate detection, official SLA retrieval "
"and complaint management system."
),
version="1.0.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
return {
"message": "Civic Complaint RAG API is running"
}

@app.post("/register", response_model=UserResponse)
def register(
user: UserCreate,
db: Session = Depends(get_db)
):
existing_user = db.query(User).filter(
User.email == user.email
).first()

```
if existing_user:
    raise HTTPException(
        status_code=400,
        detail="Email already registered"
    )

new_user = User(
    name=user.name,
    email=user.email,
    password_hash=hash_password(user.password),
    role="citizen"
)

db.add(new_user)
db.commit()
db.refresh(new_user)

return new_user
```

@app.post("/login", response_model=Token)
def login(
form_data: OAuth2PasswordRequestForm = Depends(),
db: Session = Depends(get_db)
):
existing_user = db.query(User).filter(
User.email == form_data.username
).first()

```
if not existing_user:
    raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )

if not verify_password(
    form_data.password,
    existing_user.password_hash
):
    raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )

token = create_access_token(
    existing_user.id,
    existing_user.role
)

return {
    "access_token": token,
    "token_type": "bearer"
}
```

@app.post(
"/complaints",
response_model=ComplaintAnalysisResponse
)
def create_complaint(
title: str = Form(...),
description: str = Form(...),
latitude: float = Form(...),
longitude: float = Form(...),
image: UploadFile = File(...),
current_user=Depends(verify_token),
db: Session = Depends(get_db)
):
# Heavy ML imports are intentionally loaded only
# when a complaint is actually submitted.
from complaint_pipeline import process_complaint
from complaint_embeddings import store_text_complaint

```
filename = (
    f"complaint_"
    f"{current_user['user_id']}_"
    f"{image.filename}"
)

file_path = os.path.join(
    UPLOAD_DIR,
    filename
)

with open(file_path, "wb") as buffer:
    shutil.copyfileobj(
        image.file,
        buffer
    )

result = process_complaint(
    title=title,
    description=description,
    image_path=file_path,
    latitude=latitude,
    longitude=longitude
)

category = result["category"]
department = result["department"]
urgency = result["urgency"]
duplicate_result = result["duplicate"]
municipal_sla = result["municipal_sla"]
ai_analysis = result["ai_analysis"]

if duplicate_result["decision"] == "DUPLICATE":
    status = "Duplicate"
else:
    status = "Submitted"

if municipal_sla:
    municipal_sla_days = municipal_sla.get(
        "sla_days"
    )
    municipal_sla_service = municipal_sla.get(
        "service"
    )
    municipal_sla_department = municipal_sla.get(
        "department"
    )
    municipal_sla_source = municipal_sla.get(
        "source"
    )
else:
    municipal_sla_days = None
    municipal_sla_service = None
    municipal_sla_department = None
    municipal_sla_source = None

new_complaint = Complaint(
    title=title,
    description=description,
    image_path=file_path,
    latitude=latitude,
    longitude=longitude,
    category=category,
    department=department,
    urgency=urgency,
    status=status,
    user_id=current_user["user_id"],
    ai_analysis=ai_analysis,
    duplicate_decision=duplicate_result["decision"],
    municipal_sla_days=municipal_sla_days,
    municipal_sla_service=municipal_sla_service,
    municipal_sla_department=municipal_sla_department,
    municipal_sla_source=municipal_sla_source
)

db.add(new_complaint)
db.commit()
db.refresh(new_complaint)

store_text_complaint(
    complaint_id=new_complaint.id,
    title=title,
    description=description,
    category=category,
    department=department,
    urgency=urgency,
    latitude=latitude,
    longitude=longitude
)

return {
    "complaint": new_complaint,
    "ai_analysis": ai_analysis,
    "duplicate": duplicate_result,
    "municipal_sla": municipal_sla
}
```

@app.get(
"/my-complaints",
response_model=list[ComplaintResponse]
)
def get_my_complaints(
current_user=Depends(verify_token),
db: Session = Depends(get_db)
):
complaints = db.query(
Complaint
).filter(
Complaint.user_id == current_user["user_id"]
).order_by(
Complaint.id.desc()
).all()

```
return complaints
```

@app.get(
"/admin/complaints",
response_model=list[ComplaintResponse]
)
def get_all_complaints(
current_user=Depends(verify_token),
db: Session = Depends(get_db)
):
if current_user["role"] != "admin":
raise HTTPException(
status_code=403,
detail="Admin access required"
)

```
complaints = db.query(
    Complaint
).order_by(
    Complaint.id.desc()
).all()

return complaints
```

@app.get(
"/admin/complaints/{complaint_id}/details"
)
def get_complaint_details(
complaint_id: int,
current_user=Depends(verify_token),
db: Session = Depends(get_db)
):
if current_user["role"] != "admin":
raise HTTPException(
status_code=403,
detail="Admin access required"
)

```
complaint = db.query(
    Complaint
).filter(
    Complaint.id == complaint_id
).first()

if not complaint:
    raise HTTPException(
        status_code=404,
        detail="Complaint not found"
    )

municipal_sla = None

if complaint.municipal_sla_days is not None:
    municipal_sla = {
        "service": complaint.municipal_sla_service,
        "sla_days": complaint.municipal_sla_days,
        "department": complaint.municipal_sla_department,
        "source": complaint.municipal_sla_source,
        "source_id": None
    }

return {
    "complaint": {
        "id": complaint.id,
        "title": complaint.title,
        "description": complaint.description,
        "image_path": complaint.image_path,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "category": complaint.category,
        "department": complaint.department,
        "urgency": complaint.urgency,
        "status": complaint.status,
        "user_id": complaint.user_id
    },
    "ai_analysis": complaint.ai_analysis,
    "duplicate": {
        "decision": complaint.duplicate_decision,
        "best_match": None,
        "candidates": [],
        "visual_evidence": []
    },
    "municipal_sla": municipal_sla
}
```

@app.put(
"/admin/complaints/{complaint_id}/status"
)
def update_complaint_status(
complaint_id: int,
status: str,
current_user=Depends(verify_token),
db: Session = Depends(get_db)
):
if current_user["role"] != "admin":
raise HTTPException(
status_code=403,
detail="Admin access required"
)

```
allowed_statuses = [
    "Submitted",
    "Duplicate",
    "In Progress",
    "Resolved",
    "Rejected"
]

if status not in allowed_statuses:
    raise HTTPException(
        status_code=400,
        detail=(
            f"Invalid status. "
            f"Allowed values: {allowed_statuses}"
        )
    )

complaint = db.query(
    Complaint
).filter(
    Complaint.id == complaint_id
).first()

if not complaint:
    raise HTTPException(
        status_code=404,
        detail="Complaint not found"
    )

complaint.status = status

db.commit()
db.refresh(complaint)

return {
    "message": "Complaint status updated successfully",
    "complaint_id": complaint.id,
    "status": complaint.status
}
