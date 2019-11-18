# Contributing guidelines

## Installation

- Install [`pyenv`](https://github.com/pyenv/pyenv#installation)
- Install [`pipenv`](https://github.com/pypa/pipenv#installation)

### Prepare Python environment

```shell
eval "$(pyenv init -)" # Put this in your .*hrc file
pyenv install 3.8.0
pyenv local 3.8.0
pip install --upgrade pip
pip install -U pipenv
```

### Install virtualenv & dependencies

```shell
pipenv install --dev
```

## Publish new version

```shell
export TAG=
docker build -t evaneos/ssh-action:$TAG .
docker tag evaneos/ssh-action:$TAG evaneos/ssh-action:latest
docker push evaneos/ssh-action:$TAG
docker push evaneos/ssh-action:latest
```
