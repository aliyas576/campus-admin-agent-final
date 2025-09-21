from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.tools import execute_tool

router = APIRouter(prefix="/students", tags=["students"])

class StudentCreate(BaseModel):
    name: str
    student_id: str
    email: str
    department: Optional[str] = "General"

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    active: Optional[bool] = None
    
    class Config:
        # This allows partial updates and prevents validation errors
        extra = "forbid"  # Don't allow extra fields
        validate_all = True
        arbitrary_types_allowed = True

@router.post("", response_model=Dict[str, Any])
async def create_student(student: StudentCreate):
    result = execute_tool("add_student", name=student.name, student_id=student.student_id, 
                         email=student.email, department=student.department)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Student created successfully", "student": result["student"]}

@router.put("/{student_id}", response_model=Dict[str, Any])
async def update_student(student_id: str, student_update: StudentUpdate):
    """Update a student's information"""
    try:
        # Convert Pydantic model to dict and remove None values
        update_data = student_update.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=400, 
                detail="No valid fields provided for update. Allowed fields: name, email, department, active"
            )
        
        # Validate that we have at least one field to update
        allowed_fields = {'name', 'email', 'department', 'active'}
        provided_fields = set(update_data.keys())
        
        if not provided_fields.issubset(allowed_fields):
            invalid_fields = provided_fields - allowed_fields
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid field(s) provided: {', '.join(invalid_fields)}. Allowed fields: {', '.join(allowed_fields)}"
            )
        
        result = execute_tool("update_student", student_id=student_id, **update_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")

@router.get("", response_model=Dict[str, Any])
async def list_students():
    result = execute_tool("list_students")
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("/{student_id}", response_model=Dict[str, Any])
async def get_student(student_id: str):
    result = execute_tool("get_student", student_id=student_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.delete("/{student_id}", response_model=Dict[str, Any])
async def delete_student(student_id: str):
    result = execute_tool("delete_student", student_id=student_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result