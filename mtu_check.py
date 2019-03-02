from solidfire.factory import ElementFactory

remote_mvip = input("Enter the MVIP of the cluster we are pinging out to: ")
remote_admin = input("Enter the remote admin user: ")
remote_password = input("Enter the remote admin password: ")

remote_sfe = ElementFactory.create(remote_mvip, remote_admin, remote_password, print_ascii_art=False)
remote_cls_info = remote_sfe.get_cluster_info()
remote_cls_info_json = remote_cls_info.to_json()
remote_sips = remote_cls_info_json['clusterInfo']['ensemble']
for sip in remote_sips:
    remote_host_list = (','.join(remote_sips))
print("remotes are {}".format(remote_host_list))

local_mvip = input("Enter the MVIP of the cluster we are pinging from: ")
local_admin = input("Enter the local admin user: ")
local_password = input("Enter the local admin password: ")

local_sfe = ElementFactory.create(local_mvip, local_admin, local_password, print_ascii_art=False)
local_cls_info = local_sfe.get_cluster_info()
local_cls_info_json = local_cls_info.to_json()
local_sips = local_cls_info_json['clusterInfo']['ensemble']
for sip in local_sips:
    local_host_list = (','.join(local_sips))
print("locals are {}".format(local_host_list))

# This is a node level command and we connect to 442
for sip in local_sips:
    nsip = sip + ":442"
    nfe = ElementFactory.create(nsip,"admin","Netapp1!",print_ascii_art=False)

    # Get the node networking configuration
    net_config = nfe.get_network_config()
    net_config_json = net_config.to_json()

    # Set the MTU as an int and remove 28 bytes for the network and ICMP headers
    mtu = (int(net_config_json['network']['Bond10G']['mtu'])) - 28

    # Run the ping at the MTU size and prevent fragmentation
    # Need to find a way to run this out a specified interface in case of a routed network config
    ping_result = nfe.test_ping(packet_size=mtu,hosts=remote_host_list, prohibit_fragmentation=True)
    # Set the result to JSON for easy parsing
    ping_result_json = ping_result.to_json()


    # Run the check and output a simple response
    for host in remote_sips:
        if ping_result_json['details'][host]['successful']:
            print("Host {} is not showing MTU issues at MTU size {}".format(host, mtu))
        else:
            print("Host {} is showing MTU issues at MTU size {}".format(host, mtu))
