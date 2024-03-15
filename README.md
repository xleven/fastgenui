# FastGenUI

A idea of generative UI with [FastUI](https://github.com/pydantic/FastUI) and [Instructor](https://github.com/jxnl/instructor).


## Run

```bash
pip install -r requirements.txt

cp .env.example .env 
# set OPENAI_API_KEY in .env

uvicorn chat:app --port 8000 --env-file .env

# visit http://localhost:8000/
```