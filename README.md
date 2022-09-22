# HOOPLApy

This is a Python implementation of HOOPLA
(https://github.com/AntoineThiboult/HOOPLA)

## Installation
In a terminal, clone the repo at the desired path and
enter the project's directory.
```bash
git clone https://github.com/ulaval-rs/HOOPLApy
cd HOOPLApy
```

## Running
You can configure the application via the `config.toml` file.
It follows the same configurations from the original HOOPLA file.
More information can be found here
https://github.com/AntoineThiboult/HOOPLA/blob/master/Doc/HOOPLA_user_manual.pdf

The data at `./data/` that is used for the calibration/simulation/forecast.
It has the same format as the data used in the HOOPLA project.
Support for new formats can be added in the `./hoopla/data/loaders.py` file.


To run HOOPLApy, run the `main.py` file, which is the equivalent
of the `launch_HOOPLA.m` file from the original HOOPLA project.
```sh
python main.py
```