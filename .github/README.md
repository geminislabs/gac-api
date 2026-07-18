# GitHub configuration — gac-api

## Workflows

| File | Trigger | Purpose |
| ---- | ------- | ------- |
| `quality.yml` | PR/push `develop`, `master` | Lint, tests, coverage, Docker build |
| `deploy.yml` | Push `master`, manual | Build and deploy to EC2 |

## Required status checks (branch `develop`)

- `quality`
- `security`

See `docs/GOVERNANCE.md` for branch protection setup.

## Secrets and variables

Run locally:

```bash
bash scripts/verify_github_config.sh
```

Full reference: `GITHUB_SETUP.md` (if present in repo).

## Dependabot

Weekly updates to `develop` — see `.github/dependabot.yml`.

## Templates

- Pull requests: `pull_request_template.md`
- Issues: `ISSUE_TEMPLATE/`
