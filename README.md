# Automatic Newsletter
Process different news source and generate a report


## Usage

You can run the code in this repo in a few different ways.
* ``make run``: this command will run the full pipeline (get news sources, tag them, save to disk, create a report, and email it) from the last time it ran (+1 day) until the day before you run that command.
* ``make shell``: this will create a shell inside a Docker container, from where you can run any code you like
* ``make ipython``: this will create a shell inside a Docker container and start `ipython`.
* ``make notebook``: this will start a jupyter notebook server
* ``make tests``: run all tests in `src/tests/`folder.
* ``make format``: format all files and re-organize dependenices in headers.

In all cases, these commands will build the required Docker image if 
you don't already have it. 