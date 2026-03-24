import socket
import json
import requests
from piece_manager import reassemble_file, verify_piece

TRACKER_URL = 'http://127.0.0.1:6000'

LEECHER_ID = 'leecher_1'
LEECHER_IP = '127.0.0.1'
LEECHER_PORT = 5002


def register_with_tracker():
    response = requests.post(f'{TRACKER_URL}/register', json={
        'peer_id': LEECHER_ID,
        'ip': LEECHER_IP,
        'port': LEECHER_PORT,
        'pieces': []
    })
    return response.json()['peers']


def connect_to_seeder(peer):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((peer['ip'], peer['port']))
    return s


def get_file_info(sock):
    request = {'type': 'get_info'}
    sock.send(json.dumps(request).encode())

    response = json.loads(sock.recv(100000).decode())
    return response['total_pieces'], response['hashes']


def download_piece(sock, index):
    request = {'type': 'get_piece', 'index': index}
    sock.send(json.dumps(request).encode())

    response = json.loads(sock.recv(1000000).decode())
    return bytes(response['data']), response['hash']


def main():
    print("=== LEECHER STARTING ===")

    # Step 1: register
    peers = register_with_tracker()

    # Step 2: find seeder
    seeder = None
    for peer_id, info in peers.items():
        if peer_id != LEECHER_ID:
            seeder = info
            break

    if not seeder:
        print("No seeder found!")
        return

    print("Connected to seeder:", seeder)

    try:
        sock = connect_to_seeder(seeder)
    except Exception as e:
        print("Connection error:", e)
        return

    # Step 3: get file info
    total_pieces, hashes = get_file_info(sock)
    print("Total pieces:", total_pieces)

    pieces = [None] * total_pieces

    # Step 4: download pieces
    for i in range(total_pieces):
        print(f"Downloading piece {i}...")
        piece, expected_hash = download_piece(sock, i)

        if verify_piece(piece, expected_hash):
            pieces[i] = piece
            print(f"Piece {i} verified ✅")
        else:
            print(f"Piece {i} corrupted ❌")

    sock.close()

    # Step 5: reassemble
    reassemble_file(pieces, 'downloaded_file.txt')
    print("Download complete 🎉")


if __name__ == '__main__':
    main()