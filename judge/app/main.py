from app.app_factory import get_application

app = get_application()


@app.get("/health")
def health():
    return {"status": "ok"}