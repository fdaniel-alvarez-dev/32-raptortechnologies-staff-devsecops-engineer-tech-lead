# db_lab cookbook (example)

This cookbook is intentionally small and safe. It demonstrates the shape of an idempotent “baseline” cookbook without requiring Chef Infra Server.

## What it does

- Ensures a deterministic local directory exists (for local lab artifacts)
- Writes a small marker file indicating the cookbook ran successfully

## Why it exists in this repo

Some environments still use Chef for configuration management and hardening. This repo treats Chef like any other delivery input: it must be reviewable, deterministic in demo mode, and validated before production execution.

