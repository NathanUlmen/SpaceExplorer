# Space Explorer

![Example](screencast.gif)

## Overview

## Running

## Python
Before running, make sure you have pygame installed.
If it's absent, install by running:

`pip install pygame`

To run the simulation use:

`python main.py`

## Odin

Before running make sure you have Odin installed. Instructions for how to do this can be found online .

To build and run the Odin version use:

`odin build odin/ . -o:speed -o:microarch:native -out:odin-sim && ./odin-sim`


### Profiling was done using SnakeViz

Install:
`pip install snakeviz`

Profile:
`python -m cProfile -o profile.prof main.py`

View:
`snakeviz profile.prof`
