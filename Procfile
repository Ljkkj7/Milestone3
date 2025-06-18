web: npm start
web: gunicorn backend.marketio_backend.wsgi:application --bind 0.0.0.0:8000
release: python backend/marketio_backend/manage.py migrate