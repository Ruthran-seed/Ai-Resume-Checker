"""
Organization Helper Functions
Manages organization-related operations for hosts and jobs
"""
import json
import os

ORG_FILE = "organizations.json"

def load_organizations():
    """Load all organizations"""
    if os.path.exists(ORG_FILE):
        try:
            with open(ORG_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            return {}
    return {}

def get_organization_by_id(org_id):
    """Get a specific organization by ID"""
    orgs = load_organizations()
    return orgs.get(org_id)

def get_all_organizations():
    """Get list of all organizations with basic info"""
    orgs = load_organizations()
    return list(orgs.values())

def get_organization_name(org_id):
    """Get organization name by ID"""
    org = get_organization_by_id(org_id)
    return org.get("org_name", "Unknown") if org else "Unknown"

def get_host_org_info(host_data):
    """Extract organization info from host data"""
    return {
        "org_id": host_data.get("org_id", ""),
        "org_name": host_data.get("org_name", "Unknown Organization")
    }

def format_org_display(org_name, org_id=None):
    """Format organization name for display"""
    if not org_name or org_name.strip() == "":
        return "🏢 Unaffiliated"
    return f"🏢 {org_name.title()}"
