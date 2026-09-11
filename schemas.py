from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):

    name: str

    email: EmailStr

    password: str


class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):

    access_token: str

    token_type: str


class ComplaintCreate(BaseModel):

    title: str

    description: str

    latitude: float

    longitude: float


class ComplaintResponse(BaseModel):

    id: int

    title: str

    description: str

    image_path: str | None = None

    latitude: float | None = None

    longitude: float | None = None

    category: str

    department: str

    urgency: str

    status: str

    user_id: int

    class Config:
        from_attributes = True


# --------------------------------
# Municipal SLA Response
# --------------------------------

class MunicipalSLA(BaseModel):

    service: str

    sla_days: int

    department: str

    source: str

    source_id: str | None = None


# --------------------------------
# Complaint AI Analysis Response
# --------------------------------

class ComplaintAnalysisResponse(BaseModel):

    complaint: ComplaintResponse

    ai_analysis: str

    duplicate: dict

    municipal_sla: MunicipalSLA | None = None