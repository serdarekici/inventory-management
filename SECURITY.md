# Security / Secrets Policy

This repo is designed to be GitHub-safe.

## Do NOT commit
- DB credentials (user/password), tokens, API keys
- connection strings
- private endpoints
- customer data exports

## Use instead
- `.env.example` placeholders
- environment variables at runtime
- local, untracked `.env`

If you accidentally committed a secret, rotate it immediately and rewrite git history.
