from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Agent API"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0"}
