# entrapper-case
This is the repository for the entrapeer case


1-) celery -A celeryconfig worker --loglevel=info
2-) uvicorn main:app --reload
3-) curl -X POST http://127.0.0.1:8000/start-operation/
4-)curl http://127.0.0.1:8000/list-operations/


