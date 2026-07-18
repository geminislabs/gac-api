# Release Guide — gac-api

## Version source of truth

- **Git tags:** annotated tags `v*.*.*` (e.g. `v1.0.0`) for release notes
- **Changelog:** `CHANGELOG.md` — move `[Unreleased]` entries under the new version header before tagging
- **Deploy:** push to `master` triggers `.github/workflows/deploy.yml` (EC2)

## Prerequisites

- All changes merged to `develop` via PR with **CI green** (`quality`, `security`)
- `CHANGELOG.md` updated
- GitHub Actions secrets/vars configured for deploy (EC2 SSH, DB, JWT, PASETO, etc.)

## Release sequence

1. Sync `develop`:

   ```bash
   git checkout develop
   git pull origin develop
   ```

2. Merge `develop` into `master` (via PR or fast-forward per team policy):

   ```bash
   git checkout master
   git merge develop
   git push origin master
   ```

3. Optional — tag for changelog traceability:

   ```bash
   git tag -a vX.Y.Z -m "release: vX.Y.Z"
   git push origin vX.Y.Z
   ```

4. **Deploy workflow** runs on push to `master`.

## Rollback

Re-deploy a previous known-good commit on `master`, or manually on EC2:

```bash
docker-compose -f docker-compose.prod.yml down
docker load < gac-api-previous.tar.gz
docker-compose -f docker-compose.prod.yml up -d
```
