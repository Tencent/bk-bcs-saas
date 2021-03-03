.PHONY: compilemessages
compilemessages:
	python manage.py compilemessages --settings=backend.settings.ce.dev

.PHONY: makemessages
makemessages:
	python manage.py makemessages -l zh-hans -l en -i "assets" -i "frontend" --settings=backend.settings.ce.dev

.PHONY: requirements.txt
requirements.txt:
	poetry export -f requirements.txt --output requirements.txt
