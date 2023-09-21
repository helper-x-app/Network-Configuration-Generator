let zoneCount = 0;
let vlanCount = 0;

function addZone(cloneFrom = null) {
    zoneCount++;
    const zonesDiv = document.getElementById('zones');
    const newZoneDiv = document.createElement('div');
    newZoneDiv.className = 'zone';
    newZoneDiv.id = `zone${zoneCount}`;
    newZoneDiv.innerHTML = `
        <label>Zone Name: <input type="text" name="zone_name"></label><br>
        <div id="networks${zoneCount}"></div>
        <button type="button" onclick="addNetwork('networks${zoneCount}')">Add Network</button>
        <button type="button" onclick="addZone('zone${zoneCount}')">Clone</button>
        <button type="button" onclick="removeElement('zone${zoneCount}')">Delete</button>
    `;
    zonesDiv.appendChild(newZoneDiv);

    if (cloneFrom) {
        const sourceZone = document.getElementById(cloneFrom);
        const sourceNetworks = sourceZone.querySelector(`div[id^='networks']`);
        const targetNetworks = newZoneDiv.querySelector(`div[id^='networks']`);
        targetNetworks.innerHTML = sourceNetworks.innerHTML;
    }
}

function addNetwork(networkDivId) {
    const networkDiv = document.getElementById(networkDivId);
    const newNetworkDiv = document.createElement('div');
    newNetworkDiv.innerHTML = `
        <label>Network Name: <input type="text" name="network_name"></label>
        <label>Purpose: <input type="text" name="purpose"></label><br>
    `;
    networkDiv.appendChild(newNetworkDiv);
}

function addSpannedVLAN() {
    vlanCount++;
    const vlanDiv = document.getElementById('spanned-vlans');
    const newVLANDiv = document.createElement('div');
    newVLANDiv.className = 'spanned-vlan';
    newVLANDiv.id = `vlan${vlanCount}`;
    newVLANDiv.innerHTML = `
        <label>Network Name: <input type="text" name="vlan_name"></label>
        <label>Subnet: <input type="text" name="subnet"></label>
        <label>Purpose: <input type="text" name="vlan_purpose"></label><br>
        <button type="button" onclick="removeElement('vlan${vlanCount}')">Delete</button>
    `;
    vlanDiv.appendChild(newVLANDiv);
}

function removeElement(elementId) {
    const element = document.getElementById(elementId);
    element.parentNode.removeChild(element);
}

function generate() {
    const base_cidr = document.getElementById('base_cidr').value;
    const zone_splitting = document.getElementById('zone_splitting').value;
    const subnet_splitting = document.getElementById('subnet_splitting').value;

    const config = {
        base_cidr,
        zone_splitting,
        subnet_splitting
    };

    const zones = [];
    const spannedVlans = [];

    document.querySelectorAll('.zone').forEach(zoneDiv => {
        const zoneName = zoneDiv.querySelector('input[name="zone_name"]').value;
        const networks = [];

        zoneDiv.querySelectorAll('div').forEach(networkDiv => {
            const networkName = networkDiv.querySelector('input[name="network_name"]').value;
            const purpose = networkDiv.querySelector('input[name="purpose"]').value;
            networks.push({ name: networkName, purpose: purpose });
        });

        zones.push({ name: zoneName, networks: networks });
    });

    document.querySelectorAll('.spanned-vlan').forEach(vlanDiv => {
        const vlanName = vlanDiv.querySelector('input[name="vlan_name"]').value;
        const subnet = vlanDiv.querySelector('input[name="subnet"]').value;
        const purpose = vlanDiv.querySelector('input[name="vlan_purpose"]').value;
        spannedVlans.push({ name: vlanName, subnet: subnet, purpose: purpose });
    });

    const generate_type = document.getElementById('generate_type').value;

    const payload = {
        config,
        zones,
        spannedVlans,
        generate_type
    };
    

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        const outputDiv = document.getElementById('output');
        outputDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
