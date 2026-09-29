import uvicorn

if __name__ == "__main__":
    print("=== Iniciando API do Residencial Aurora ===")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
