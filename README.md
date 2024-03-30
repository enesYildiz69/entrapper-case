# Setup

Run:
```
git clone https://github.com/enesYildiz69/entrapper-case.git
```
Go inside the project:
```
cd entrapeer-case
```
Add .env file to the project directory with the content : 
```
OPENAI_API_KEY="YOUR_API_KEY"
```
Run:
```
docker-compose up --build  
```
Then in another terminal run:
```
curl -X POST http://127.0.0.1:8000/start-operation/
```
If you want to track progress go to:
```
http://127.0.0.1:8000/list-operations/ 
```
After the task is completed, you can view the results in the file:
```
companies_by_continent.json
```
