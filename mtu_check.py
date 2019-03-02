import argparse
from solidfire.factory import ElementFactory

class mtu_check(object):
    host = ""
    sip = ""
    mtu = ""
    check = ""

def get_inputs():
    """
    Get the inputs for connecting to the cluster
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-lclm', type=str,
                        required=True,
                        metavar='lcl_mvip',
                        help='Local MVIP name or IP')
    parser.add_argument('-lclu', type=str,
                        required=True,
                        metavar='lcl_username',
                        help='Source username to connect with')
    parser.add_argument('-lclp', type=str,
                        required=False,
                        metavar='password',
                        help='Source password for user')
    parser.add_argument('-rmtm', type=str,
                        required=True,
                        metavar='remote_mvip',
                        help='Remote MVIP name or IP')
    parser.add_argument('-rmtu', type=str,
                        required=True,
                        metavar='rmt_username',
                        help='Remote username to connect with')
    parser.add_argument('-rmtp', type=str,
                        required=False,
                        metavar='rmt_password',
                        help='Remote password for user')
    args = parser.parse_args()
    remote_sfmvip = args.rmtm
    remote_sfuser = args.rmtu
    if not args.rmtp:
        remote_sfpass = getpass("Enter password for user{} on cluster {}: ".format(remote_sfuser, remote_sfmvip))
    else:
        remote_sfpass = args.rmtp
        
    local_mvip = args.lclm
    local_sfuser = args.lclu
    if not args.lclp:
        local_sfpass = getpass("Enter password for user{} on cluster {}: ".format(local_sfuser, local_sfmvip))
    else:
        local_sfpass = args.lclp
    
    return sfmvip, sfuser, sfpass

def check_mtu(host, sip, mtu, check):
    mtu_status = mtu_check()
    mtu_status.host = host
    mtu_status.sip = sip
    mtu_status.mtu = mtu
    mtu_status.check = check
    return mtu_status

#Print a table
def prettyPrint(host, sip, mtu, check):
    #When printing values wider than the second column, split and print them
    print("| "  + host.center(20) + " | " + sip.center(20) + " | " + mtu.center(10) + " | " + check.center(10) + " |".center(2))

remote_sips = []
local_sips = []
ping_status = {}

remote_sfe = ElementFactory.create(remote_mvip, remote_admin, remote_password, print_ascii_art=False)
remote_nodes = remote_sfe.list_active_nodes()
for node in remote_nodes.nodes:
    remote_sips.append(node.sip)

for sip in remote_sips:
    remote_host_list = (','.join(remote_sips))
print("remotes are {}".format(remote_host_list))

local_sfe = ElementFactory.create(local_mvip, local_admin, local_password, print_ascii_art=False)
local_nodes = local_sfe.list_active_nodes()
for node in local_nodes.nodes:
    local_sips.append(node.sip)
    
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

    print("+" + "-"*71 + "+")
    remote_hdr = "Remote IP"
    local_hdr = "Local IP"
    mtu_hdr = "MTU"
    state_hdr = "State"
    prettyPrint(remote_hdr,local_hdr,mtu_hdr,state_hdr)
    # Run the check and output a simple response
    for host in remote_sips:
        if ping_result_json['details'][host]['successful']:
            check = "pass"
            mtu_out = check_mtu(host, sip, mtu, check)
            ping_status[host]=mtu_out
            
        else:
            check = "fail"
            mtu_out = check_mtu(host, sip, mtu, check)
            ping_status[host]=mtu_out
    for key in ping_status.keys():
        host = str(ping_status[key].host)
        sip = str(ping_status[key].sip)
        mtu = str(ping_status[key].mtu) + " "
        check = str(ping_status[key].check) + " "
        print("+" + "-"*71 + "+")
        #print("|" + host +"|"+ sip +"|"+ mtu +"|"+ check + " |")
        prettyPrint(host,sip,mtu,check)
    print("+" + "-"*71 + "+")
        