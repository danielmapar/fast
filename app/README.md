# Fast App

This application is an aggregator of [FastQC`](https://github.com/s-andrews/FastQC), [Fastp](https://github.com/OpenGene/fastp) and [HybPiper](https://github.com/mossmatters/HybPiper). It abstract those CLI applications to a simple easy to use interface to streamline research efforts.

## Installation

* Follow the instructions in the [README.md](../README.md) file.

* Install the dependencies: `poetry install`

* Run the app: `poetry run fast-app`

## Build an executable

* Build the executable: `poetry run pyinstaller --onefile --windowed --name FastApp app/main.py`

* The executable will be available in the `app/dist` folder. The executable is named `FastApp`.







