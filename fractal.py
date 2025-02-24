import hashlib
import base64

def fractal_hash(data):
    """Unique hash for data chunks."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def fractal_compress(data, min_chunk=4, max_chunk=32):
    """Adaptive fractal compression—finds optimal repeating patterns."""
    compressed = []
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
            score = count * (size ** 0.5)  # Weight longer chunks slightly less
            if score > best_score:
                best_score = score
                best_chunk = (chunk, count)
        if best_chunk:
            compressed.append(best_chunk)
            i += best_chunk[1] * len(best_chunk[0])
        else:
            compressed.append((data[i:], 1))
            break
    return compressed

def fractal_decompress(compressed):
    """Reconstruct data from fractal chunks."""
    return "".join(chunk * count for chunk, count in compressed)

def pack_data(compressed):
    """Pack into transmittable format."""
    return base64.b64encode(str(compressed).encode()).decode()

def unpack_data(packed):
    """Unpack compressed data."""
    return eval(base64.b64decode(packed).decode())
