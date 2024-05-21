#!/bin/bash

awk '!x{x=sub("[0-9]+\\.[0-9]+\\.[0-9]+", "'"$1"'")} 7' pyproject.toml > __tmp__ && mv __tmp__ pyproject.toml
