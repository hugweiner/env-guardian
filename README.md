# env-guardian

> CLI tool to validate and sync environment variables across different deployment environments

---

## Installation

```bash
pip install env-guardian
```

Or with pipx for isolated installs:

```bash
pipx install env-guardian
```

---

## Usage

Define your expected variables in a `.env.schema` file:

```
DATABASE_URL=required
API_KEY=required
DEBUG=optional
PORT=optional
```

Then validate your environment against the schema:

```bash
# Validate current environment
env-guardian validate --schema .env.schema

# Sync variables across environments
env-guardian sync --from .env.production --to .env.staging

# Check for missing or extra variables
env-guardian diff --schema .env.schema --env .env.local
```

Example output:

```
✔  DATABASE_URL   present
✔  API_KEY        present
✗  DEBUG          missing (optional)
✖  SECRET_TOKEN   undefined (not in schema)

2 warnings found. Run with --fix to resolve.
```

---

## License

[MIT](LICENSE) © env-guardian contributors