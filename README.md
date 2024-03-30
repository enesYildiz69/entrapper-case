# entrapper-case
This is the repository for the entrapeer case


1-) celery -A celeryconfig worker --loglevel=info
2-) uvicorn main:app --reload
3-) curl -X POST http://127.0.0.1:8000/start-operation/
3a-)curl http://127.0.0.1:8000/list-operations/
3b-)curl http://127.0.0.1:8000/operation-status/6597d7c2-5a88-48b2-965b-2f6bfd0aea78

