from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI(title="Residencial Aurora API")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # Retorna um emoji de prédio comercial/condomínio em formato SVG
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🏢</text></svg>'
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/")
def read_root():
    return {"message": "API do Assistente Virtual do Residencial Aurora está online!"}
