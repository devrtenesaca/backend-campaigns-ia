from fastapi import FastAPI

# Crea una instancia de FastAPI
app = FastAPI()

# Define una ruta (endpoint)
@app.get("/")
def read_root():
    return {"message": "Hello World"}