web: cd backend/marketio_backend && gunicorn marketio_backend.wsgi:application --bind 0.0.0.0:$PORT
release: python backend/marketio_backend/manage.py migrate
release: python backend/marketio_backend/manage.py stock_seeder