# Contributing to Codegard

## First-time setup

```bash
cp .env.example .env
make dev-build
```

## Branch naming

```
feat/short-description     # new feature
fix/short-description      # bug fix
chore/short-description    # tooling, config, dependencies
```

## Before every PR

Run these commands before pushing. CI checks the same things - better to catch issues locally.

### Backend

```bash
cd backend
uv run ruff format .
uv run ruff check .
```

### Judge

```bash
cd judge
uv run ruff format .
uv run ruff check .
```

### Frontend

```bash
cd frontend
npx prettier --write .
npm run lint
```

## Running tests locally

```bash
make test-backend
make test-judge
```


## Useful commands

```bash
make dev              # start dev environment
make logs             # follow logs
make migrate          # apply migrations
make makemigrations   # create new migrations
make shell            # open shell in backend container
make help             # full list of commands
```
