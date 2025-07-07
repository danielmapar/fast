# Fast App

![FastApp Logo](./images/logo.png)

This application is an aggregator of [FastQC`](https://github.com/s-andrews/FastQC), [Fastp](https://github.com/OpenGene/fastp) and [HybPiper](https://github.com/mossmatters/HybPiper). It abstract those CLI applications to a simple easy to use interface to streamline research efforts.

## Local Development

* Follow the instructions in the [README.md](../README.md) file.

* Install the dependencies: `poetry install`

* Run the app: `poetry run fast-app`

## Build an executable

* Build the executable by running the following command:
    ```bash
    poetry run pyinstaller --name "FastApp" --windowed --onefile --add-data ".env:." --clean "app/main.py"
    ```

* The executable will be available in the `app/dist` folder. The executable is named `FastApp`.

## Make a release

* Create a new tag: `git tag v0.0.1`

* Push the tag: `git push origin v0.0.1`

* The release will be automatically created by the [GitHub Actions workflow](../.github/workflows/build-and-release.yml).
