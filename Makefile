# Usage:
#   make setup           # one-time, after cloning
#   make commit m="your message"
#   make warm            # re-compile the venv if kernel startup feels slow

# Precompile .pyc on install so the first import in a fresh Jupyter kernel
# doesn't pay the compile cost. Applies to every uv command run from here.
export UV_COMPILE_BYTECODE = 1

.PHONY: setup commit warm

setup:
	uv sync
	uv run pre-commit install

# Compile whatever is already installed, without touching the lock or reinstalling.
# Use after a manual `uv pip install`, or if a kernel start still feels slow.
# Leading `-`: some packages ship deliberately-unparseable test fixtures, which
# makes compileall exit non-zero even though everything real compiled fine.
warm:
	-uv run python -m compileall -q -j 0 .venv

commit:
	# Version bump, lock upgrade, sync, and requirements.txt export all happen
	# automatically via pre-commit hooks (see .pre-commit-config.yaml) —
	# doing them here too would bump the patch version twice.
	git commit -m "$(m)"
