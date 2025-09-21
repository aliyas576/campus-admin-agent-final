from fastapi import APIRouter, HTTPException
from backend.tools import execute_tool

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/total-students")
async def get_total_students():
    total = execute_tool("get_total_students")
    return {"total_students": total}

@router.get("/students-by-department")
async def get_students_by_department():
    dept_data = execute_tool("get_students_by_department")
    return {"students_by_department": dept_data}