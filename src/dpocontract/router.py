from fastapi import APIRouter

router = APIRouter(
    prefix="/dpo",
    tags=["dpoContract"]
)

@router.get("/{user_id}/latest")
def post_contract(user_id):
    contract = {
        "userId": "...", "fullName": "Анна Иванова",
        "department": "Разработка", "position": "Junior",
        "area": "Backend", "targetRole": "Middle Backend",
        "completedAt": "2026-10-20", "score": 52,
        "competencies": [
        {"code": "SQL", "level": 25, "low_confidence": False},
        {"code": "ASYNC", "level": 50}, {"code": "PYTHON", "level": 80}
        ]
    }
