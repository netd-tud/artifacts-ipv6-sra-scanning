#!/bin/bash

input_file=$1 

# Extract the first and last timestamps
start_time=$(awk -F, 'NR==2 {print $1}' "$input_file")
end_time=$(awk -F, 'END{print $1}' "$input_file")

# Calculate duration in seconds
start_epoch=$(date -d "$start_time" +%s)
end_epoch=$(date -d "$end_time" +%s)
duration_sec=$((end_epoch - start_epoch))

# Convert duration to hh:mm:ss format
duration=$(printf '%02d:%02d:%02d' $((duration_sec/3600)) $(( (duration_sec%3600)/60 )) $((duration_sec%60)))

# Extract total sent packets 
sent_total=$(awk -F, 'END {print $7}' "$input_file")

# Extract total received packets
recv_total=$(awk -F, 'END {print $10}' "$input_file")

# Extract hitrate
hitrate=$(awk -F, 'END {printf "%.2f",$5}' "$input_file")

# Print the results
logger -t measurement-stats -p user.info "Start of Scan: $start_time"
logger -t measurement-stats -p user.info "End of Scan:   $end_time"
logger -t measurement-stats -p user.info "Duration:      $duration"
logger -t measurement-stats -p user.info "Sent Packets:  $sent_total"
logger -t measurement-stats -p user.info "Recv Packets:  $recv_total"
logger -t measurement-stats -p user.info "Hit Rate:  $hitrate%"

