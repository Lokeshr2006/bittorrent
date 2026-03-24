import socket
import threading
import json
import requests
from piece_manager import split_file, get_all_hashes

# Tracker address
TRACKER_URL = 'http://127.0.0.1:6000'

# Seeder info
SEEDER_ID   = 'seeder_1'
SEEDER_IP   = '127.0.0.1'
SEEDER_PORT = 5001

# File to share
FILE_TO_SHARE = 'testfile.txt'


def register_with_tracker(piece_count):
    """
    Tells the tracker: I am seeder_1, I have ALL pieces.
    """
    piece_list = list(range(piece_count))   # [0, 1, 2, 3, ...]

    response = requests.post(f'{TRACKER_URL}/register', json={
        'peer_id': SEEDER_ID,
        'ip':      SEEDER_IP,
        'port':    SEEDER_PORT,
        'pieces':  piece_list
    })

    print(f"Registered with tracker. Response: {response.json()['status']}")


def handle_leecher(conn, addr, pieces, hashes):
    """
    Handles one leecher connection.
    Leecher asks for a piece number, seeder sends that piece back.
    """
    print(f"Leecher connected from {addr}")

    try:
        while True:
            # Receive request from leecher
            data = conn.recv(1024).decode()     # receive piece request
            if not data:
                break                           # leecher disconnected

            request = json.loads(data)          # convert from JSON string to dict

            if request['type'] == 'get_piece':
                piece_index = request['index']  # which piece they want

                # Send the piece data and its hash
                response = {
                    'index': piece_index,
                    'hash':  hashes[piece_index],
                    'data':  list(pieces[piece_index])  # bytes → list for JSON
                }

                response_str = json.dumps(response)
                conn.sendall(response_str.encode())     # send to leecher
                print(f"Sent piece {piece_index} to {addr}")

            elif request['type'] == 'get_info':
                # Leecher asking how many pieces total
                response = {
                    'total_pieces': len(pieces),
                    'hashes':       hashes
                }
                conn.sendall(json.dumps(response).encode())
                print(f"Sent file info to {addr}")

    except Exception as e:
        print(f"Connection error with {addr}: {e}")
    finally:
        conn.close()
        print(f"Leecher {addr} disconnected")


def start_server(pieces, hashes):
    """
    Starts the seeder socket server.
    Listens for leecher connections and handles each in a separate thread.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SEEDER_IP, SEEDER_PORT))
    server.listen(5)                            # allow up to 5 connections

    print(f"Seeder listening on {SEEDER_IP}:{SEEDER_PORT}")
    print("Waiting for leechers...")

    while True:
        try:
            conn, addr = server.accept()
        except Exception as e:
            print("Connection failed:", e)
            continue

        # Handle each leecher in a separate thread
        # so multiple leechers can download at the same time
        thread = threading.Thread(
            target=handle_leecher,
            args=(conn, addr, pieces, hashes)
        )
        thread.daemon = True
        thread.start()


def main():
    print("=== SEEDER STARTING ===")

    # Step 1: Split the file into pieces
    print("Splitting file into pieces...")
    pieces = split_file(FILE_TO_SHARE)
    hashes = get_all_hashes(pieces)
    print(f"Ready to share {len(pieces)} pieces")

    # Step 2: Register with tracker
    register_with_tracker(len(pieces))

    # Step 3: Start listening for leechers
    start_server(pieces, hashes)


if __name__ == '__main__':
    main()