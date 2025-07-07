#!/bin/bash

echo "---> Installing pre-commit and hooks"

cd ~/fast

pre-commit install --install-hooks || echo "---> Failed installing hooks"

echo "---> Finished installing pre-commit and hooks"
