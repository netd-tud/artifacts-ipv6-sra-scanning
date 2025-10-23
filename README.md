

Artifacts: Scanning the IPv6 Internet Using Subnet-Router Anycast Probing
===

This repository contains the artifacts for the following paper:
```
Scanning the IPv6 Internet Using Subnet-Router Anycast Probing
Maynard Koch, Raphael Hiesgen, Marcin Nawrocki, Thomas C. Schmidt, and Matthias Wählisch
Proc. ACM Netw., Vol. 3, No. CoNEXT4, Article 50. Publication date: December 2025.
https://doi.org/10.1145/3768997
```

# Reproduction of paper artifacts

Requirements to reproduce plots and tables: 256 GB of RAM, 256 GB free disk space

Clone this repository, then: 
1. Make sure python 3.10 is installed.
2. Make a virtual environment: `make python_env`
3. Activate python env: `source .venv/bin/activate`
4. Download required data from [https://doi.org/10.5281/zenodo.17210254](https://doi.org/10.5281/zenodo.17210254)
5. Move the `measurement-raw-data.tar` file into `./data/raw/` and extract it.
6. To get a clean starting environment run `make clean` first.

Now you can reproduce the paper plots with: 

7. `make plots`

The plots are then stored under `reports/figures/`

To reproduce the paper tables you can simply run:

8. `make nbconvert-clean-execute`

## Cleaning the environment
- `make clean` to remove figures and the table.html file.
- `make clean-cache` to remove the cached pickle files for faster plot rendering
- It is necessary to run these commands when creating new dataframes from the raw files (see below)

## Scanning the IPv6 address space
- TBD
