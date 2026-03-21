# WSGI entry point for Gunicorn
# Start command: gunicorn wsgi:app
from app import app

if __name__ == "__main__":
    app.run()
