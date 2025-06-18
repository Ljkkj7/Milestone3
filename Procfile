web: npm start
web: cd backend/marketio_backend && gunicorn marketio_backend.wsgi:application --bind 0.0.0.0:8000
release: python backend/marketio_backend/manage.py migrate