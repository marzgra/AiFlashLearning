### create python virtual env:
python3 -m venv .venv

### enter .venv:
source .venv/bin/activate

### install required libs:
pip install -r requirements.txt

### run postgres:
docker run --name ai-flash-learning-postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ai-flash-learning-db \
  -p 5432:5432 \
  -d postgres:15

### set openai api key:
echo 'export OPENAI_API_KEY="..."