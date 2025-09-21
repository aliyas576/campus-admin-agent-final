from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.models.database import Student, ActivityLog, SessionLocal
from datetime import datetime

def add_student(name: str, student_id: str, email: str, department: str = "General") -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        existing = db.query(Student).filter(Student.student_id == student_id).first()
        if existing:
            return {"error": f"Student with ID {student_id} already exists"}
        
        student = Student(name=name, student_id=student_id, email=email, department=department)
        db.add(student)
        db.commit()
        db.refresh(student)
        
        return {
            "success": True,
            "student": {
                "id": student.id,
                "name": student.name,
                "student_id": student.student_id,
                "email": student.email,
                "department": student.department
            }
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

def get_student(student_id: str) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return {"error": f"Student with ID {student_id} not found"}
        
        return {
            "success": True,
            "student": {
                "id": student.id,
                "name": student.name,
                "student_id": student.student_id,
                "email": student.email,
                "department": student.department
            }
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

def update_student(student_id: str, **kwargs) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return {"error": f"Student with ID {student_id} not found"}
        
        allowed_fields = {'name', 'email', 'department', 'active'}
        invalid_fields = set(kwargs.keys()) - allowed_fields
        if invalid_fields:
            return {"error": f"Invalid field(s): {', '.join(invalid_fields)}"}
        
        update_count = 0
        for field, value in kwargs.items():
            if hasattr(student, field) and value is not None:
                setattr(student, field, value)
                update_count += 1
        
        if update_count == 0:
            return {"error": "No valid fields provided"}
        
        db.commit()
        db.refresh(student)
        
        return {
            "success": True,
            "message": f"Student {student_id} updated",
            "student": {
                "id": student.id,
                "name": student.name,
                "student_id": student.student_id,
                "email": student.email,
                "department": student.department,
                "active": student.active
            }
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

def list_students() -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        students = db.query(Student).all()
        return {
            "success": True,
            "students": [
                {
                    "id": s.id,
                    "name": s.name,
                    "student_id": s.student_id,
                    "email": s.email,
                    "department": s.department
                } for s in students
            ]
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

def delete_student(student_id: str) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return {"error": f"Student with ID {student_id} not found"}
        
        db.delete(student)
        db.commit()
        return {"success": True, "message": f"Student {student_id} deleted"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

def get_total_students() -> int:
    db: Session = SessionLocal()
    try:
        return db.query(Student).count()
    except Exception as e:
        return 0
    finally:
        db.close()

def get_students_by_department() -> Dict[str, int]:
    db: Session = SessionLocal()
    try:
        departments = {}
        students = db.query(Student).all()
        for student in students:
            departments[student.department] = departments.get(student.department, 0) + 1
        return departments
    except Exception as e:
        return {}
    finally:
        db.close()