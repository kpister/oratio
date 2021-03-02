# Open Oratio

An open source pipeline to translate .mp4 video files to .mov video files in 20 different languages.

Generate quality video and podcast localizations at scale.

## Setup

Most important:

`python --version` >= 3.7

`pip install -r docs/requirements.txt`

Also install rubberband
macOS: `brew install rubberband`
Linux: `sudo apt-get install -y rubberband-cli`

And follow the instructions in `docs/` for `aws` and `gcloud` integration.
Then make sure to setup the names of the s3 or gcloud bucket you will store your audio in.
Set the `AWS_BUCKET_NAME` and the `GCLOUD_BUCKET_NAME` constants in `src/constants/constants.py`.

### Optional Setup

Also install image magick, (if you want text overlay)
`brew install imagemagick`

Setup pre-commit, if you want to contribute
`pre-commit install`

Test setup: `pre-commit run`
This should run `black` and `run_tests.py` but both should be skipped until code changes

## Running the pipeline

`python src/main.py tests/test_config.yaml` will test your setup to make sure everything is in the right place.

After `test_config.yaml` starts working, make your own project folder in `media/prod` and edit the `config.yaml` 
to get going! Checkout my test video in `media/prod/kaiser` to familarize yourself with the setup.

`python src/main.py` will use the default config.yaml provided in the home directory.

## Understanding the Repo

Start with `src/main.py`. Run it. Read it.

Follow the commands it executes with a debugger.

Then check out `src/client.py`. This is our biggest piece of abstraction, and especially if you are adding an API feature, you'll want a good understanding of what it is doing.

`src/config.py` and `src/video_project.py` have important setup information and maintain the state of the project.

### File structure

```
. home
/docs - contains documentation on ideas, most documentation is in the relevant .py files
/src - contains source code for the pipeline
/src/api - the neural apis we work with, abstracted in the client.py
/media - contains input and output media
/media/dev - stores temporary files made during translation
/media/prod - stores the finalized input and output files
/media/test - stores test input files
/tests - unit tests for the pipeline
```

## Metrics

Performance (speed)
Performance (accuracy)
