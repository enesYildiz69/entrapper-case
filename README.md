# entrapper-case
This is the repository for the entrapeer case

1-) add .env file to the project directory with the content : OPENAI_API_KEY="YOUR_API_KEY"

2-) docker-compose up --build  

3-) curl -X POST http://127.0.0.1:8000/start-operation/

4-) curl http://127.0.0.1:8000/list-operations/ (For tracking progress)


