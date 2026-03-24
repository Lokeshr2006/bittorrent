from flask import Flask, request, jsonify

app = Flask(__name__)

# This dictionary stores all registered peers
# Format: { "peer_id": { "ip": "127.0.0.1", "port": 5001, "pieces": [0,1,2] } }
peers = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()   # get data from peer

    # ✅ ADD THIS BLOCK HERE
    if not data or not data.get('peer_id') or not data.get('ip'):
        return jsonify({'error': 'Invalid input'}), 400

    # continue normal flow
    peer_id = data['peer_id']
    ip      = data['ip']
    port    = data['port']
    pieces  = data['pieces']

    # Save this peer's info
    peers[peer_id] = {
        'ip': ip,
        'port': port,
        'pieces': pieces
    }

    print(f"Peer registered: {peer_id} at {ip}:{port} with pieces {pieces}")

    # Return list of ALL peers (including this one)
    return jsonify({
        'status': 'registered',
        'peers': peers
    })


@app.route('/update', methods=['POST'])
def update():
    """
    Peer calls this when it downloads a new piece.
    Updates the tracker so others know this peer has more pieces now.
    """
    data = request.get_json()

    peer_id = data['peer_id']
    pieces  = data['pieces']          # updated piece list

    if peer_id in peers:
        peers[peer_id]['pieces'] = pieces    # update the piece list
        print(f"Peer updated: {peer_id} now has pieces {pieces}")
        return jsonify({'status': 'updated'})
    else:
        return jsonify({'status': 'error', 'message': 'peer not found'})


@app.route('/peers', methods=['GET'])
def get_peers():
    """
    Returns the full list of all known peers.
    Any peer can call this anytime to refresh their peer list.
    """
    return jsonify({'peers': peers})


@app.route('/status', methods=['GET'])
def status():
    """
    Simple health check — just to confirm tracker is running.
    """
    return jsonify({
        'status': 'tracker running',
        'total_peers': len(peers)
    })


if __name__ == '__main__':
    print("Tracker started on port 6000...")
    print("Waiting for peers to register...")
    app.run(host='0.0.0.0', port=6000)