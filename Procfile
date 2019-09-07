release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn distance_matrix.wsgi
heroku config:set DISABLE_COLLECTSTATIC=1
