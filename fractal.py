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
    return "".join(chunk_dict.get(chunk_id, "") * count for chunk_id, count in compressed)

def pack_packet(compressed, chunk_dict, metadata):
    dict_str = "#DICT#" + ";".join(f"{k}:{v}" for k, v in chunk_dict.items())
    seq_str = "#SEQ#" + "|".join(f"{c[0]},{c[1]}" for c in compressed)
    meta_str = f"#META#{metadata}"
    packet = f"{dict_str}{seq_str}{meta_str}"
    return base64.b64encode(packet.encode()).decode()

def unpack_packet(packed):
    try:
        decoded = base64.b64decode(packed).decode()
        if "#DICT#" not in decoded or "#SEQ#" not in decoded or "#META#" not in decoded:
            raise ValueError(f"Malformed packet structure: {decoded}")
        dict_part, rest = decoded.split("#SEQ#", 1)
        seq_part, meta_part = rest.split("#META#", 1)
        chunk_dict = {}
        dict_items = dict_part.split("#DICT#", 1)[1].split(";")  # Skip #DICT#
        for item in dict_items:
            if not item:  # Skip empty
                continue
            if ":" not in item:
                raise ValueError(f"Invalid dict entry: {item}")
            k, v = item.split(":", 1)
            chunk_dict[int(k)] = v
        seq_items = seq_part.split("|")
        compressed = []
        for item in seq_items:
            if not item:  # Skip empty
                continue
            id_str, count_str = item.split(",")
            compressed.append((int(id_str), int(count_str)))
        metadata = meta_part
        return compressed, chunk_dict, metadata
    except Exception as e:
        raise ValueError(f"Failed to unpack packet: {e} - Raw packet: {packed}")
