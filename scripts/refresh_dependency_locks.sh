#!/usr/bin/env sh
set -eu
python -m pip install pip-tools==7.6.2
pip-compile --allow-unsafe --strip-extras --generate-hashes --resolver=backtracking --output-file=requirements-runtime.lock requirements-runtime.in
pip-compile --allow-unsafe --strip-extras --generate-hashes --resolver=backtracking --output-file=requirements-dev.lock requirements-dev.txt
pip-compile --allow-unsafe --strip-extras --generate-hashes --resolver=backtracking --output-file=requirements-audit.lock requirements-audit.in
pip-compile --allow-unsafe --strip-extras --generate-hashes --resolver=backtracking --output-file=requirements-reference-audit.lock requirements-reference-audit.in
