# `publish-pypi.yml` — displaced from `.github/workflows/` on 2026-08-12

This workflow published `scitex-orochi` to PyPI **with no test job anywhere in
the file.** It is moved here rather than deleted so the history and the reason
stay recoverable.

## What it was

```
on: push: tags: ['v*']

jobs:
  build     (no needs)  -> checkout, setup-python, python -m build
  publish   needs: build -> pypa/gh-action-pypi-publish  (id-token: write)
  release   needs: publish -> gh release create
```

There is no test job in the dependency closure of `publish`. A `v*` tag
containing this file publishes to PyPI regardless of whether anything passes.

It really ran: successful publishes for **v0.16.3**, **v0.16.4** and
**v0.17.0** (the current latest tag).

## Why it is safe to remove

This repo already carries `pypi-publish-and-github-release-on-tag.yml`, which
does the same job **gated**:

```
publish -> build -> test        # test runs .github/ci/exec-in-sif.sh run-in-sif.sh
```

That file is present on **both** `main` and `develop`. `publish-pypi.yml` was
present on **`main` only** — it had already been dropped from `develop` and
was never removed here. This is the leftover half of a migration.

## The severity, stated precisely

GitHub resolves workflow files **at the tagged commit**. Releases are tagged on
`develop`, which no longer contains this file, so it has not been firing for
recent releases — it is **dormant, not actively publishing ungated today.**

It becomes live again the moment a tag is cut from `main`, or from any branch
still carrying it. At that point it publishes to PyPI with no tests, in
parallel with the gated workflow and with no dependency on it — so a red test
run in the gated pipeline would not stop this one from shipping the artifact.

A loaded gun rather than a fire, and worth unloading.

## Context

Found while auditing release-gating across the `scitex-ai` org on 2026-08-12
(see `scitex-ai/.github` issue #32 and PR #31). Of 68 tag-triggered release
workflows in the org, this was the **only** publish job with no test job
upstream once the audit was done by resolving `needs:` closures rather than
pattern-matching workflow text.
