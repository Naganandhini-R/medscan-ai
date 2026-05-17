from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat():
    return {"reply": "Hello, I am your medicine assistant."}
