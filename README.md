# mtu_check
script to check MTU settings

Currently the API does not appear to have a way to specify or force the interface to run the ping from.  This limits viability unless
routing metrics for the gateway are set properly or the network you are checking is directly connected.  This means that pings on routed
networks for replication may not respond as expected.

Hopefully this will be added to the API in the future and I will update this to take that into account at that time.
