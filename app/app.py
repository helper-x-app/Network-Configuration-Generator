from collections import defaultdict
import ipaddress
from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

def generate_subnets_for_zones(config, networks):
    zones = networks
    base_cidr = config["base_cidr"]
    zone_splitting = int(config["zone_splitting"].split('/')[-1])
    subnet_splitting = int(config["subnet_splitting"].split('/')[-1])

    network_obj = ipaddress.ip_network(base_cidr, strict=False)
    zone_subnets = list(network_obj.subnets(new_prefix=zone_splitting))
    data = []

    for zone_index, zone in enumerate(zones):
        current_zone = zone_subnets[zone_index]
        subnets = list(current_zone.subnets(new_prefix=subnet_splitting))

        for network in zone['networks']:
            subnet = str(subnets.pop(0))

            # Split the subnet into octets
            octets = subnet.split('.')
            challenged_octet = octets[2]
            mask = subnet.split('/')[1]
            # Check if the third and fourth octets are '0' before replacing
            if mask != '24' and challenged_octet == '0':
                subnet = '.'.join((octets[0], octets[1], '1', octets[3]))
                network_name = "LAN"
                network_purpose = "Isolation"
                zone_name = zone['name']
            # elif mask != '24' and challenged_octet != '0':
            else:
                # Join the octets back into a subnet
                subnet = '.'.join(octets)
                network_name = network['name']
                network_purpose = network['purpose']
                zone_name = zone['name']
            # else:

            data.append({
                "Zone Name": zone_name,
                "Network Name": network_name,
                "Subnet": subnet,
                "Purpose": network_purpose
            })

    return data


def generate_subnets_grouped_by_zones(all_subnets):
    data_by_zone = defaultdict(list)
    for subnet in all_subnets:
        zone_name = subnet["Zone Name"]
        data_by_zone[zone_name].append(subnet)

    return dict(data_by_zone)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    payload = request.json
    config = payload['config']
    zones = payload['zones']
    generate_type = payload.get('generate_type', 'byNetwork')

    if generate_type == 'byZone':
        all_subnets = generate_subnets_for_zones(config, zones)
        data = generate_subnets_grouped_by_zones(all_subnets)
    else:
        data = generate_subnets_for_zones(config, zones)

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
        data["Spanned"] = spanned_data
    else:
        data.extend(spanned_data)

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False)
