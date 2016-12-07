#!/bin/bash -xe
# Runs bandit tests

pyver="$(python -V 2>&1)"

if [[ $pyver =~ Python\ 2\.6 ]]
then
    echo 'Bandit does not support python 2.6'
else
    bandit -r pypuppetdb
    bandit -r tests -s B101
fi
