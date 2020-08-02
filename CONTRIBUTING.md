# Contributing

As an open source project, feel free to fork this under the BSD-3 clause license
and improve it to your heart's content.

We will merge pull requests that we deem relevant to the project and which pass
all our integration testing.


## Minimum requirements

Install and run our pre-commit hooks to prevent improper formatting or broken tests.

Setup pre-commit: `pre-commit install`

Test setup: `pre-commit run`. This should run `black` and `run_tests.py` but both should be skipped until code changes


## Requests

Make your branch names, pull requests and commits meaningful.
Commits like "adds fixes" are harmful to the code base.

The pull request itself should be a selling point. Why is this fix being added?
While we have no strict template to follow, a good idea is to include "what is the root cause of the pull request?", "were alternatives considered?", and "what are the implications of this change?"
