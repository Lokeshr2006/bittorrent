import hashlib
import os

# Size of each piece = 512 KB
PIECE_SIZE = 512 * 1024

def split_file(filepath):
    """
    Reads a file and splits it into pieces.
    Returns a list of pieces (each piece is raw bytes).
    """
    pieces = []

    with open(filepath, 'rb') as f:       # open file in binary read mode
        while True:
            piece = f.read(PIECE_SIZE)     # read 512KB at a time
            if not piece:                  # if nothing left to read, stop
                break
            pieces.append(piece)           # add piece to our list

    print(f"File split into {len(pieces)} pieces.")
    return pieces


def hash_piece(piece):
    """
    Creates a SHA1 fingerprint for one piece.
    Used to verify the piece is not corrupted.
    """
    return hashlib.sha1(piece).hexdigest()  # returns a 40-character string


def get_all_hashes(pieces):
    """
    Returns a list of hashes, one for each piece.
    """
    return [hash_piece(p) for p in pieces]


def reassemble_file(pieces, output_filepath):
    """
    Joins all pieces back together into the original file.
    """
    with open(output_filepath, 'wb') as f:  # open output file in binary write mode
        for piece in pieces:
            f.write(piece)                  # write each piece one by one

    print(f"File reassembled and saved as: {output_filepath}")


def verify_piece(piece, expected_hash):
    """
    Checks if a downloaded piece is valid.
    Compares its hash with the expected hash.
    Returns True if good, False if corrupted.
    """
    actual_hash = hash_piece(piece)
    return actual_hash == expected_hash