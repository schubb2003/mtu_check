import sys
from solidfire.factory import ElementFactory

class mtu_check(object):
    host = ""
    sip = ""
    mtu = ""
    check = ""

def check_mtu(host, sip, mtu, check):
    mtu_status = mtu_check()
    mtu_status.host = host
    mtu_status.sip = sip
    mtu_status.mtu = mtu
    mtu_status.check = check
    return mtu_status

if len(sys.argv) < 7:
    print("Insufficient arguments entered:\n"
          "Usage: python <script> <remote_mvip> <remote_admin> <remote_password>"
          "<local_mvip> <local_admin> <local_password>")

remote_mvip = sys.argv[1]
remote_admin = sys.argv[2]
remote_password = sys.argv[3]
local_mvip = sys.argv[4]
local_admin = sys.argv[5]
local_password = sys.argv[6]

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
        print("+" + "-"*13 + "+" + "-"*13 + "+----+----+")
        print("|" + ping_status[key].host +"|"+ ping_status[key].sip +"|"+ str(ping_status[key].mtu) +"|"+ ping_status[key].check + "|")
    print("+" + "-"*13 + "+" + "-"*13 + "+----+----+")
        import sys
from solidfire.factory import ElementFactory

class mtu_check(object):
    host = ""
    sip = ""
    mtu = ""
    check = ""

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
    print("| "  + host.ljust(20) + " | " + sip.ljust(20) + " | " + mtu.ljust(10) + " | " + check.ljust(10) + " |".ljust(2))


if len(sys.argv) < 7:
    print("Insufficient arguments entered:\n"
          "Usage: python <script> <remote_mvip> <remote_admin> <remote_password>"
          "<local_mvip> <local_admin> <local_password>")

remote_mvip = sys.argv[1]
remote_admin = sys.argv[2]
remote_password = sys.argv[3]
local_mvip = sys.argv[4]
local_admin = sys.argv[5]
local_password = sys.argv[6]

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
#    print("|Remote       |Local        |MTU |State|")
    prettyPrint("remote       ","local        ","mtu  ","state")
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
        