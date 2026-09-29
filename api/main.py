from fastapi import FastAPI

app = FastAPI(title="Residencial Aurora API")

@app.get("/")
def read_root():
    return {"message": "API do Assistente Virtual do Residencial Aurora está online!"}
