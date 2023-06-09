#!/bin/bash

tag=$(git tag --points-at HEAD | sort -V | tail -n 1)
if [ -n "$tag" ]; then
  echo -n "$tag" > ./flow_pdf/git.txt
else
  commit_hash=$(git rev-parse HEAD)
  if [ -n "$commit_hash"] ; then
  else
    commit_hash=$sha
  fi
  echo -n "dev-$commit_hash" > ./flow_pdf/git.txt
fi