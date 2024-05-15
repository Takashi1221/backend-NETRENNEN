release: python manage.py migrate --settings=config.settings.prod
web: gunicorn config.wsgi --log-file -