"""
Add organization management functions to host_auth.py
"""
import os

content = """

# ================= ORGANIZATION MANAGEMENT =================
def load_organizations():
    \"\"\"Load all organizations\"\"\"
    org_file = "organizations.json"
    if os.path.exists(org_file):
        try:
            with open(org_file, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            return {}
    return {}

def get_host_organization(host_id):
    \"\"\"Get organization info for a host\"\"\"
    hosts = load_hosts()
    host = hosts.get(host_id)
    if not host or not host.get("org_id"):
        return None
    
    orgs = load_organizations()
    return orgs.get(host.get("org_id"))

def set_host_organization(host_id, org_id):
    \"\"\"Associate a host with an organization\"\"\"
    hosts = load_hosts()
    if host_id not in hosts:
        return False
    
    orgs = load_organizations()
    if org_id not in orgs:
        return False
    
    org = orgs[org_id]
    hosts[host_id]["org_id"] = org_id
    hosts[host_id]["org_name"] = org.get("org_name", "")
    
    save_hosts(hosts)
    return True

def get_host_org_info(host_id):
    \"\"\"Get host's organization info\"\"\"
    hosts = load_hosts()
    host = hosts.get(host_id, {})
    return {
        "org_id": host.get("org_id", ""),
        "org_name": host.get("org_name", "")
    }
"""

# Append to host_auth.py
with open("host_auth.py", "a") as f:
    f.write(content)
    
print("✓ Organization management functions added to host_auth.py")
