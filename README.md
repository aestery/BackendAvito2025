# Backend-trainee-assignment-autumn-2025

Проект выполнен в рамках отбора на стажировку Авито осенью 2025 года.

[Ссылка на задачу](https://github.com/avito-tech/tech-internship/blob/main/Tech%20Internships/Backend/Backend-trainee-assignment-autumn-2025/Backend-trainee-assignment-autumn-2025.md)

## Сервис назначения ревьюеров для Pull Request’ов

### Migration-Aware Development Plan

The idea is to create solution in Python, which I know best, and then if I would have enough time migrate to Go, which is prefered.

#### Phase 1 - Write app

Most of work expected here.

- Set up deployment.
- Implement service (FastAPI + asyncpg + PostgreSQL).
- Implement stats endpoint.
- Write language-neutral E2E tests.
- Write migration-friendly SQL files.

#### Phase 2 - Validation

- Run E2E tests (should pass unchanged).
- Run load tests again.
- Deploy final Go version.

### FAQ

- why most of text is written in english? - This is the only language I can fast-type and I am too lazy to switch between languages in process.
