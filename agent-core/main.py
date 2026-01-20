from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from agent import agent
from pydantic import BaseModel

class CommandRequest(BaseModel):
    command: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "HyperOS Agent Active", 
        "version": "1.0.1",
        "system": agent.get_system_status()
    }

@app.post("/execute")
def execute_command(req: CommandRequest):
    try:
        result = agent.execute_instruction(req.command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting HyperOS Agent Core...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
