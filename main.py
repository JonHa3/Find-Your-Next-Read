"""Entry point for running the API locally.

    python main.py

starts the FastAPI app defined in app/api.py with uvicorn, equivalent to:

    uvicorn app.api:app --reload

Visit http://127.0.0.1:8000/docs for interactive Swagger docs once running.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)
