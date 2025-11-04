

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

Requirements to reproduce plots and tables: 256 GB of RAM, 256 GB free disk space, recent Ubuntu (e.g., 24.04)

Clone this repository with the `--recursive` flag to also include the submodules used for scanning: 
`git clone https://github.com/netd-tud/artifacts-ipv6-sra-scanning.git --recursive`, then: 
1. Make sure python 3.10 (or newer) is installed.
2. Install the virtual environment package with `apt install python3-venv`.
3. Install `make` with `apt install make`.
4. Make a virtual environment: `make python_env`
5. Activate python env: `source .venv/bin/activate`
6. Remove the current `data/` directory with `rm -rf data/`
7. Download required data from [https://doi.org/10.25532/OPARA-979](https://doi.org/10.25532/OPARA-979) (If the DOI link is broken, use this one instead: [https://opara.zih.tu-dresden.de/handle/123456789/1761](https://opara.zih.tu-dresden.de/handle/123456789/1761))
8. Move the `data.tar` file into the root directory (`artifacts-ipv6-sra-scanning/`) and extract it.
9. To get a clean starting environment run `make clean` first.

Now you can reproduce the paper plots with: 

8. `make plots`

The plots are then stored under `reports/figures/`

To reproduce the paper tables you can simply run:

9. `make tables`
    
This executes the jupyter notebooks and stores the html version under `notebooks/*.html`, showing the tables.

## Cleaning the environment
- `make clean` to remove figures and the table.html file.
- `make clean-cache` to remove the cached pickle files for faster plot rendering
- It is necessary to run these commands when creating new dataframes from the raw files (see below)

## Scanning the IPv6 address space
### Requirements
- IPv6 connectivity with at least one global IPv6 address
- Golang 1.22.2
- Install `jq` with `sudo apt install jq`
- ZMapv6 dependencies: https://github.com/tumi8/zmap/blob/master/INSTALL.md
`sudo apt-get install build-essential cmake libgmp3-dev gengetopt libpcap-dev flex byacc libjson-c-dev pkg-config libunistring-dev libjudy-dev`

### Setup
- Make sure the submodules (`zmap` and `go_ipv6_address_generator`) under `tools/` have been cloned properly
- If not run `git submodule update --init --recursive`
- If you are using the archived version from Zenodo, replace the directories `zmap` and `go_ipv6_address_generator` under `tools/` with the corresponding ZIP archives from Zenodo

### Generating IPv6 target addresses
Follow the instructions in the [README](./tools/go_ipv6_address_generator/README.md) file.
We provide a small template config and a few input prefixes, to check if the address generator is working, simply navigate to `tools/go_ipv6_address_generator` and run:

`go run address-generator-ipv6.go --config-file ./config/config-go-tool`

This generates SRA addresses for /64 subnets. The current config generates 10 per prefix and a maximum of 100 addresses in total.

### Scanning for Subnet-Router anycast addresses
Follow the instructions in the [HOWTOSCAN](./tools/HOWTOSCAN.md) file.

