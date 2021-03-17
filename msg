venv/bin/python manage.py makemessages -l en -l fi -i '*venv*' -i '*/data/*' -i '*uploads/*' -i '*downloads/*'
cd jsanctions/locale
../../venv/bin/python ../../manage.py compilemessages
cd ../..
