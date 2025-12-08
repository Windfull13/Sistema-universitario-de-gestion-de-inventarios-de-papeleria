release: echo "Deploying at $(date)" && python clear_db.py
web: gunicorn --config gunicorn_config.py app:app
