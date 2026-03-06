# 32-aws-reliability-security-chef

A portfolio-grade, runnable reliability + security toolkit that demonstrates **config management validation** using Chef-style cookbooks alongside safe operational drills.

This repository is intentionally generic (no employer branding). It focuses on verified automation and deterministic checks.

## The 3 core problems this repo solves
1) **Config management hygiene:** a minimal Chef cookbook example with offline guardrails and optional local validation.
2) **Security-minded defaults:** deterministic checks that catch dangerous patterns (e.g., world-writable permissions).
3) **Production-safe validation:** explicit test modes separating offline checks from opt-in integrations.

## Tests (two explicit modes)

This repo supports exactly two test modes via `TEST_MODE`:

- `TEST_MODE=demo` (default): offline-only guardrails (no Chef required)
- `TEST_MODE=production`: real integrations when configured (guarded by explicit opt-in)

Run demo mode:

```bash
make test-demo
```

Run production mode:

```bash
make test-production
```

Optional production checks:
- Set `CHEF_VALIDATE=1` to run a **local** Chef validation using `chef-client -z` (requires Chef installed)

## Chef example

The example cookbook lives at `chef/cookbooks/db_lab/`. Demo-mode guardrails validate cookbook hygiene and produce an evidence artifact:

```bash
python3 tools/chef_guardrails.py --format json --out artifacts/chef_guardrails.json
```

## Sponsorship and contact

Sponsored by:
CloudForgeLabs  
https://cloudforgelabs.ainextstudios.com/  
support@ainextstudios.com

Built by:
Freddy D. Alvarez  
https://www.linkedin.com/in/freddy-daniel-alvarez/

For job opportunities, contact:
it.freddy.alvarez@gmail.com

## License

Personal, educational, and non-commercial use is free. Commercial use requires paid permission.
See `LICENSE` and `COMMERCIAL_LICENSE.md`.
