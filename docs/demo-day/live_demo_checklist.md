# Live Demo Checklist

## Before Starting

- [ ] Docker Desktop is running.
- [ ] `.env` contains `GROQ_API_KEY`.
- [ ] `.env` contains `JWT_SECRET`.
- [ ] `.env` contains `JWT_AUDIENCE=tool-125`.
- [ ] `.env` contains `JWT_ISSUER=tool-125-auth`.
- [ ] Network access is available for Groq.
- [ ] Demo JWT is generated and ready.
- [ ] `demo_inputs.json` and `expected_outputs.json` are open as backup.

## Startup

- [ ] Run `docker compose up --build -d`.
- [ ] Run `docker compose ps`.
- [ ] Confirm `tool-125-ai-service` is healthy.
- [ ] Confirm Redis is healthy.
- [ ] Confirm PostgreSQL is healthy.

## Endpoint Checks

- [ ] `GET /health` returns `200`.
- [ ] `POST /describe` returns `200`.
- [ ] `POST /recommend` returns `200`.
- [ ] `POST /generate-report` returns `200`.
- [ ] Missing JWT returns `401`.
- [ ] Prompt injection payload returns `400`.

## Speaking Checks

- [ ] Opening is under 20 seconds.
- [ ] Technical explanation is under 60 seconds.
- [ ] Non-technical value explanation is ready.
- [ ] Fallback explanation is ready.
- [ ] Closing summary is ready.

