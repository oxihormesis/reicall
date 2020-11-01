release: python manage.py makemigrations call_tracking && python manage.py makemigrations && python manage.py migrate
web: gunicorn twilio_sample_project.wsgi:application --log-file -