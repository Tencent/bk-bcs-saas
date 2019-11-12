.PHONY: compilemessages
compilemessages:
	django-admin compilemessages --settings=backend.settings.ce.dev

.PHONY: makemessages
makemessages:
	python manage.py makemessages -l zh-hans -l en -i "assets" -i "frontend" --settings=backend.settings.ce.dev
