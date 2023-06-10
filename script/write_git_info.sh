#!/bin/bash

set -evx

tag=$(git tag --points-at HEAD | sort -V | tail -n 1)
if [ -n "$tag" ]; then
  echo -n "$tag" > ./git.txt
else
  commit_hash=$(git rev-parse HEAD)
  if [ ! -n "$commit_hash" ] ; then
    commit_hash=$sha
  fi
  echo -n "$commit_hash" > ./git.txt
fi