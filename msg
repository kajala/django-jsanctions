python manage.py makemessages -i venv -i data
cd sanctions/locale
python ../../manage.py compilemessages
cd ..
