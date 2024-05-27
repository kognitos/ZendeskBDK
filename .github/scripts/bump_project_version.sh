#!/bin/bash

awk '!x{x=sub("[0-9]+\\.[0-9]+\\.[0-9]+", "'"$1"'")} 7' pyproject.toml > __tmp__ && mv __tmp__ pyproject.toml
awk '!x{x=sub("[0-9]+\\.[0-9]+\\.[0-9]+", "'"$1"'")} 7' src/openweather/__version__.py > __tmp__ && mv __tmp__ src/openweather/__version__.py
