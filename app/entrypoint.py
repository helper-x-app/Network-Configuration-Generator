import ipaddress
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def generate_subnets_for_zones(config, networks):
    base_cidr = ipaddress.ip_network(config["base_cidr"], strict=False)
    zone_splitting = int(config["zone_splitting"].split('/')[-1])
    subnet_splitting = int(config["subnet_splitting"].split('/')[-1])

    data = []
    
    # Ensure the starting address is x.x.1.x
    base_cidr = ipaddress.IPv4Network(f"{base_cidr.network_address + 1}/{base_cidr.prefixlen}")

    current_zone = base_cidr.subnets(new_prefix=zone_splitting).__next__()
    subnets = list(current_zone.subnets(new_prefix=subnet_splitting))
    
    # Exclude the first subnet (x.x.0.x/y)
    subnets = subnets[1:]

    for zone_index, zone in enumerate(networks):
        for network in zone['networks']:
            if subnets:
                data.append({
                    "Zone Name": zone['name'],
                    "Network Name": network["name"],
                    "Subnet": str(subnets.pop(0)),
                    "Purpose": network["purpose"]
                })

    return data

def generate_subnets_grouped_by_zones(all_subnets):
    data_by_zone = {}
    for subnet in all_subnets:
        zone_name = subnet["Zone Name"]
        if zone_name not in data_by_zone:
            data_by_zone[zone_name] = []
        data_by_zone[zone_name].append(subnet)

    return data_by_zone

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    payload = request.json
    config = payload['config']
    zones = payload['zones']
    generate_type = payload.get('generate_type', 'byNetwork')

    all_subnets = generate_subnets_for_zones(config, zones)

    # Add spanned VLANs to the data
    spanned_data = []
    for vlan in payload.get('spannedVlans', []):
        spanned_data.append({
            "Zone Name": "Spanned",
            "Network Name": vlan["name"],
            "Subnet": vlan["subnet"],
            "Purpose": vlan["purpose"]
        })

    if generate_type == 'byZone':
        data = generate_subnets_grouped_by_zones(all_subnets)
        data["Spanned"] = spanned_data
    else:
        data = all_subnets + spanned_data

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
