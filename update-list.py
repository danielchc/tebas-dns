import subprocess
import os
import requests
import ipaddress


def get_subnet(cidr):
    network = ipaddress.IPv4Network(cidr, strict=False)
    ip_list = [str(ip) for ip in network.hosts()]
    
    return ip_list

def get_blacklist(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            print(f"[ERROR] Failed to retrieve data. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] An error occurred: {e}")
        return None


def restart_dnsmasq():
    try:
        subprocess.run(["/usr/bin/pkill", "-f", "dnsmasq"], check=False)
    except Exception as e:
        print(f"[ERROR] Failed to stop dnsmasq: {e}")
    try:
        subprocess.run(["/usr/sbin/dnsmasq"], check=False)
        print("[INFO] dnsmasq is running.")
    except Exception as e:
        print(f"[ERROR] Failed to start dnsmasq: {e}")

def generate_dnsmasq():
    file_path = "/etc/dnsmasq.conf"
    
    dns_blacklist=os.environ.get("DNS_BLACKLIST","")
    dns_primary=os.environ.get("DNS_PRIMARY","8.8.8.8")
    dns_secondary=os.environ.get("DNS_SECONDARY","8.8.4.4")
    
    print(f"[INFO] Using DNS {dns_primary} and {dns_secondary}")
    print(f"[INFO] Generating aliases, this may take a while")
    
    blacklist_data = get_blacklist(dns_blacklist)
    
    alias_list=""
    for provider in blacklist_data:
        for subnet in provider["blacklist"]:
            for ip in get_subnet(subnet):
                alias_list+= f"alias={ip},{provider['redirect']},255.255.255.255\n"
        
    config_text = f"""
    log-queries
    no-resolv
    server={dns_primary}
    server={dns_secondary}
    {alias_list}
    """
    print(f"[INFO] Alias generation successfully completed")

    
       
    try:
        with open(file_path, "w") as file:
            file.write(config_text)
            print(f"[INFO] Configuration successfully saved to {file_path}")
    except PermissionError:
        print(f"[ERROR] Permission denied. Please run the script as root.")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")


        
if __name__ == "__main__":
    print(f"[INFO] Updating blacklist...")
    generate_dnsmasq()
    restart_dnsmasq()