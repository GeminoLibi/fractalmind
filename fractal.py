# fractal.py
import hashlib
import base64

def cogito_hash(data):
    """Unique hash for data chunks."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def fractal_compress(data, min_chunk=4, max_chunk=32):
    compressed = []
    chunk_dict = {}
    i = 0
    while i < len(data):
        best_chunk = None
        best_score = -1
        for size in range(min_chunk, min(max_chunk + 1, len(data) - i + 1)):
            chunk = data[i:i + size]
            count = 1
            j = i + size
            while j < len(data) and data[j:j + size] == chunk and count < 255:
                count += 1
                j += size
            score = count * (size ** 0.5)
            if score > best_score:
                best_score = score
                best_chunk = (chunk, count)
        if best_chunk:
            chunk_id = len(chunk_dict)
            if best_chunk[0] not in chunk_dict.values():
                chunk_dict[chunk_id] = best_chunk[0]
            compressed.append((chunk_id, best_chunk[1]))
            i += best_chunk[1] * len(best_chunk[0])
        else:
            chunk_id = len(chunk_dict)
            chunk_dict[chunk_id] = data[i:]
            compressed.append((chunk_id, 1))
            break
    return compressed, chunk_dict

def fractal_decompress(compressed, chunk_dict):
    return "".join(chunk_dict[chunk_id] * count for chunk_id, count in compressed)

def pack_packet(compressed, chunk_dict, metadata):
    dict_str = "#DICT#" + ";".join(f"{k}:{v}" for k, v in chunk_dict.items())
    seq_str = "#SEQ#" + "|".join(f"{c[0]},{c[1]}" for c in compressed)
    return base64.b64encode(f"{dict_str}{seq_str}#{metadata}".encode()).decode()

def unpack_packet(packed):
    try:
        decoded = base64.b64decode(packed).decode()
        parts = decoded.split("#", 3)
        if len(parts) != 4 or parts[0] != "" or parts[1] != "DICT" or parts[2] != "SEQ":
            raise ValueError("Malformed packet structure")
        chunk_dict = {}
        for item in parts[1][5:].split(";"):  # Skip #DICT#
            if ":" in item:
                k, v = item.split(":", 1)
                chunk_dict[int(k)] = v
            else:
                raise ValueError(f"Invalid dict entry: {item}")
        compressed = [(int(c.split(",")[0]), int(c.split(",")[1])) for c in parts[2][5:].split("|")]  # Skip #SEQ#
        metadata = parts[3]
        return compressed, chunk_dict, metadata
    except Exception as e:
        raise ValueError(f"Failed to unpack packet: {e}")
