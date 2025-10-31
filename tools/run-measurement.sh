#!/bin/bash

# systemd has parent directory configured as working directory
MEASUREMENTS="./measurements"
CONFIGS="./configs"

# get current date and create measurement dir
current_date=$(date -Is --utc | sed 's/:/_/g')
measurement_dir="${MEASUREMENTS}/${current_date}"

if [ ! -d "$measurement_dir" ]; then
  mkdir -p "$measurement_dir"
  logger -t measurement-run-script -p user.info "Created measurement directory: $measurement_dir"
else
  logger -t measurement-run-script -p user.info "Measurement directory already exists: $measurement_dir"
fi

# copy input file into logfile directory
cp $(jq -r '.PrefixFile // empty' "${CONFIGS}/config-go-tool") "${measurement_dir}/"
logger -t measurement-run-script -p user.info "Copied input file into measurement directory."

# logfile name
logfile="${measurement_dir}/zmap_log_${current_date}.log"
logger -t measurement-run-script -p user.info "Logfile set to: $logfile"

# start measurement
logger -t measurement-run-script -p user.info "Starting measurement at $(date)"

go run ./go_ipv6_address_generator/address-generator-ipv6.go --config-file "${CONFIGS}/config-go-tool" | \
./zmap/src/zmap --config "${CONFIGS}/config-zmap" -o "$logfile"


if [ $? -eq 0 ]; then
  logger -t measurement-run-script -p user.info "Measurement completed successfully at $(date)"
else
  logger -t measurement-run-script -p user.err "Measurement unexpectedly stopped at $(date)"
fi

logger -t measurement-run-script -p user.info "Compressing logfile: $logfile"
zstd --rm -T0 $logfile
logger -t measurement-run-script -p user.info "Compressing done."
# extract brief version of scan results and log them
./log-scan-infos.sh ./monitoring/scan-status.csv
