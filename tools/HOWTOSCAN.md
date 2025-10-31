# Running the scan
## Preparation
1. Adjust the config file values for ZMap; under `./configs/config-zmap`
    - change the `gateway-mac` value with your gateway mac address.
    - set the interface for sending by adjusting the `interface` parameter.
    - set the interface for receiving packets, if your scan server does not use asynchronous routing (reply can arrive on different interface than the probe was sent from) you can just use the same interface as for `interface`. Otherwise set `rcv-iface` to the receiving interface.
    - Adjust the `ipv6-source-ip` value, this is the source IP address used when sending out probes.

2. Adjust the input file for address generation under `./configs/config-go-tool`
    - The `"PrefixFile": "./input/example-prefixes"` can be used for testing, but can be replaced with any other prefix list for scanning.
    - To reproduce the paper measurements using the BGP announced prefixes, you can use `./input/bgp-20241004`
    
3. Compile ZMap from source by following the instructions under https://github.com/tumi8/zmap/blob/master/INSTALL.md -- the binary is then stored under `./zmap/src/zmap`.

## Scanning
Run `./run-measurements.sh`, make sure the script is executable and runs either with `sudo` or has `NETCAP` capabilities.

## Monitoring
To check the progress of the scan you can run `log-scan-infos-tmp-print.sh ./monitoring/scan-status.csv`. This will print the current scan status in the terminal.