from .student_management import (
    add_student, get_student, update_student, list_students, delete_student,
    get_total_students, get_students_by_department
)

TOOLS = {
    "add_student": add_student,
    "get_student": get_student,
    "update_student": update_student,
    "list_students": list_students,
    "delete_student": delete_student,
    "get_total_students": get_total_students,
    "get_students_by_department": get_students_by_department,
}

def get_tools():
    return TOOLS

def execute_tool(tool_name: str, **kwargs):
    if tool_name in TOOLS:
        return TOOLS[tool_name](**kwargs)
    return {"error": f"Tool {tool_name} not found"}