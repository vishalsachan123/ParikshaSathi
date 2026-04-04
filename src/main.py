from fastapi import FastAPI

app = FastAPI()
@app.get("/health")
async def get_root():
    return {"message": "Health is ok : ParikshaSathi"}




