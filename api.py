from fastapi import FastAPI

app = FastAPI(title="FlowGuard AI")

@app.get("/")
def home():
    return {"message": "FlowGuard AI Backend Running"}