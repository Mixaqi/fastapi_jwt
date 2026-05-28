up-local:
	docker compose up -d

up-prod:
	docker compose --profile full up -d --build

down:
	docker compose --profile full down

fastapi-local:
	uv run uvicorn app.main:app --reload --port 8000

cache-flush:
	docker compose exec redis redis-cli -n 1 FLUSHDB