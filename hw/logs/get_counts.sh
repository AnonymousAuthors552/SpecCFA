#!/bin/bash

project=$1

n=8

python3 log_counter.py "./"$project"_baseline"

for ((i=1; i<=n; i++))
do
  directory="./"$project"_experiments/$i"
  if [ -d "$directory" ]; then
    python3 log_counter.py $directory
  else
    echo "$directory does not exist"
  fi
done
