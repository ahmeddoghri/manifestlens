# manifestlens

**C2PA Content Credential inspection and policy gate.**

![manifestlens cover](demo/cover.png)

Inspect claims, actions, ingredients, validation status, and signing metadata behind Content Credentials.

![manifestlens workbench](demo/dashboard.png)

## What ships

- A deterministic domain analysis engine with explicit scope
- JSON API and responsive local browser workbench
- CLI demo and file-driven analysis
- Docker image, unit tests, and GitHub Actions matrix
- No API keys and no uploaded user data

## Run it end to end

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e .
manifestlens demo
manifestlens inspect demo/C_with_CAWG_data.jpg
manifestlens serve
```

Open <http://127.0.0.1:8090>. Analyze your own JSON input with `manifestlens analyze input.json`.

## API

- `GET /api/demo` returns the committed fixture and result.
- `POST /api/analyze` runs the same engine on a JSON body.

## Current basis

- [C2PA manifest model](https://opensource.contentauthenticity.org/docs/manifest/understanding-manifest/)

## Demo result

The workbench resolves one active manifest, its parent ingredient, three edit actions, signing metadata, and a cryptographic hard-binding assertion. The test suite also reads a committed signed asset through the official C2PA Python SDK.

## Scope

Valid Content Credentials show that signed provenance data remains bound to an asset. They do not prove that the depicted event is true, that the signer is trustworthy, or that unsigned content is false.

## Test

The integration fixture is the signed `C_with_CAWG_data.jpg` sample from the Apache-2.0/MIT-licensed [contentauth/c2pa-python](https://github.com/contentauth/c2pa-python) repository.

```bash
python -m unittest discover -s tests -v
```

MIT licensed.
