#!/usr/bin/env python3
"""Validate every checked-in research configuration without starting training."""

from __future__ import annotations

import sys

try:
    from .configlib import config_digest, config_paths, resolve_config, validate_config
except ImportError:  # Direct execution: python3 scripts/validate_configs.py
    from configlib import config_digest, config_paths, resolve_config, validate_config


def main() -> int:
    failures = []
    paths = list(config_paths())
    for path in paths:
        try:
            config = resolve_config(path)
            errors = validate_config(config, path)
        except (OSError, ValueError, TypeError) as error:
            errors = ["{}: {}: {}".format(path, type(error).__name__, error)]
            config = None
        if errors:
            failures.extend(errors)
            continue
        print("OK {:64s} {}".format(str(path.name), config_digest(config)[:12]))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("validated {} configuration files".format(len(paths)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
