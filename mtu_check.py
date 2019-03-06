import argparse
import os
from solidfire.factory import ElementFactory
from platform import system

# declare vars for later use
remote_sips = []
local_sips = []
ping_status = {}

# This class is used to allow for a nice output to be displayed
class MtuCheck(object):
    """
    # Need a object to add to a dict for nice table output
    params: remote_node = remote cluster node
    params: local_node = local cluser node
    params: mtu = mtu of local cluster node
    params: check = output of whether the check is pass or fail
    """
    remote_node = ""
    local_node = ""
    mtu = ""
    check = ""

# This is used to build the object from the class above
def check_mtu(remote_node, local_node, mtu, check):
    mtu_status = MtuCheck()
    mtu_status.remote_node = remote_node
    mtu_status.local_node = local_node
    mtu_status.mtu = mtu
    mtu_status.check = check
    
    return mtu_status

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
    remote_mvip = args.rmtm
    remote_user = args.rmtu
    # If no password on the CLI input, prompt for it
    if not args.rmtp:
        remote_pass = getpass("Enter password for user{} "
                              "on cluster {}: ".format(remote_sfuser,
                                                       remote_sfmvip))
    else:
        remote_pass = args.rmtp
        
    local_mvip = args.lclm
    local_user = args.lclu
    if not args.lclp:
        local_pass = getpass("Enter password for user{} "
                             "on cluster {}: ".format(local_sfuser,
                                                      local_sfmvip))
    else:
        local_pass = args.lclp
    
    return(remote_mvip,
           remote_user,
           remote_pass,
           local_mvip,
           local_user,
           local_pass)

def clear_screen():
    if system().lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')

def prettyPrint(remote_node, local_node, mtu, check):
    """
    # Print a nice table view
    """
    print("| "  + remote_node.center(20) + " | " + 
          local_node.center(20) + " | " + mtu.center(10) + 
          " | " + check.center(10) + " |".center(2))

def connect_remote(remote_mvip, remote_user, remote_pass):
    """
    # Create remote cluster connection
    """
    remote_sfe = ElementFactory.create(remote_mvip,
                                       remote_user,
                                       remote_pass,
                                       print_ascii_art=False)
    
    return remote_sfe

def connect_local(local_mvip, local_user, local_pass):
    """
    # Build local node list
    """
    local_sfe = ElementFactory.create(local_mvip,
                                      local_user,
                                      local_pass,
                                      print_ascii_art=False)
    
    return local_sfe

def build_remote(remote_sfe):
    """
    # Build remote node list
    """
    remote_nodes = remote_sfe.list_active_nodes()
    for node in remote_nodes.nodes:
        remote_sips.append(node.sip)

    for local_node in remote_sips:
        remote_host_list = (','.join(remote_sips))
    
    return remote_sips, remote_host_list

def build_local(local_sfe):
    """
    # Build local node list
    """
    local_nodes = local_sfe.list_active_nodes()
    for node in local_nodes.nodes:
        local_sips.append(node.sip)

    return local_sips

def get_ping_result(local_user, local_pass, remote_host_list):
    """
    # Actually do the work of connecting and running the pings
    """
    # This is a node level command and we connect to 442
    for local_node in local_sips:
        nsip = local_node + ":442"
        nfe = ElementFactory.create(nsip,
                                    local_user,
                                    local_pass,
                                    print_ascii_art=False)

        # Get the node networking configuration
        net_config = nfe.get_network_config()
        net_config_json = net_config.to_json()

        # Set the MTU as an int and remove 28 bytes 
        #    for the network and ICMP headers
        mtu = (int(net_config_json['network']['Bond10G']['mtu'])) - 28

        # Run the ping at the MTU size and prevent fragmentation
        # Need to find a way to run this out a specified 
        #    interface in case of a routed network config
        ping_result = nfe.test_ping(packet_size=mtu,
                                    hosts=remote_host_list,
                                    prohibit_fragmentation=True)
        # Set the result to JSON for easy parsing
        ping_result_json = ping_result.to_json()

        # Run the check and output a simple response
        for remote_node in remote_sips:
            if ping_result_json['details'][remote_node]['successful']:
                check = "pass"
                mtu_out = check_mtu(remote_node, local_node, mtu, check)
                ping_status[remote_node]=mtu_out
                
            else:
                check = "fail"
                mtu_out = check_mtu(remote_node, local_node, mtu, check)
                ping_status[remote_node]=mtu_out
    
def print_ping_result(ping_status):
    ping_status_len = len(ping_status)
    local_status_check = 0
    remote_status_check = 0
    # Set local node information
    local_header = "--Ping from--"
    print("+" + "-"*21 + "+" + \
          "\n| {:^20}".format(local_header) + "{:20}".format("|") + \
          "\n+" + "-"*21 + "+")
          
    for key in ping_status.keys():
        if local_status_check < (ping_status_len - 1):
            print("| {:^20}".format(ping_status[key].local_node) + \
                  "{:20}\n+".format("|") + " "*21 + "+")
        else:
            print("| {:^20}".format(ping_status[key].local_node) + \
                  "{:20}".format("|"))
        local_status_check = local_status_check + 1
    print("+" + "-"*21 + "+\n")
    
    # Set remote node information
    remote_header = "--Ping to--"
    print("+" + "-"*21 + "+" + \
          "\n| {:^20}".format(remote_header) + "{:20}".format("|") + \
          "\n+" + "-"*21 + "+")
          
    for key in ping_status.keys():
        if remote_status_check < (ping_status_len - 1):
            print("| {:^20}".format(ping_status[key].remote_node) + \
                  "{:20}\n+".format("|") + " "*21 + "+")
        else:
            print("| {:^20}".format(ping_status[key].remote_node) + \
                  "{:20}".format("|"))
        remote_status_check = remote_status_check + 1
    print("+" + "-"*21 + "+\n")
    
    # Print the information in a table like format
    print("+" + "-"*71 + "+")
    remote_hdr = "--Remote IP--"
    local_hdr = "--Local IP--"
    mtu_hdr = "--MTU--"
    state_hdr = "--State--"
    prettyPrint(remote_hdr,local_hdr,mtu_hdr,state_hdr)
    
    for key in ping_status.keys():
        remote_node = str(ping_status[key].remote_node)
        local_node = str(ping_status[key].local_node)
        mtu = str(ping_status[key].mtu) + " "
        check = str(ping_status[key].check) + " "
        print("+" + "-"*71 + "+")
        prettyPrint(remote_node, local_node, mtu, check)
    print("+" + "-"*71 + "+")

def main():
    remote_mvip, remote_user, remote_pass, \
    local_mvip, local_user, local_pass = get_inputs()
    remote_sfe = connect_remote(remote_mvip, remote_user, remote_pass)
    local_sfe = connect_local(local_mvip, local_user, local_pass)
    remote_sips, remote_host_list = build_remote(remote_sfe)
    local_sips = build_local(local_sfe)
    get_ping_result(local_user, local_pass, remote_host_list)
    clear_screen()
    print_ping_result(ping_status)

if __name__ == "__main__":
    main()
