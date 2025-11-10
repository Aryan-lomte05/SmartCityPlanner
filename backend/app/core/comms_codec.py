from typing import List, Tuple

# Hamming (7,4) implementation (systematic form)
G = [
    # mapping 4-bit data -> 7-bit code (d1,d2,d3,d4)
    # We'll implement compute parity bits directly
]

def encode_7_4(data_bits: List[int]) -> List[int]:
    """
    data_bits: list of 4 bits [d1,d2,d3,d4]
    returns 7-bit codeword [c1..c7] where positions are: [p1 p2 d1 p3 d2 d3 d4]
    (common systematic layout)
    """
    if len(data_bits) != 4:
        raise ValueError("data_bits must be length 4")
    d1, d2, d3, d4 = data_bits
    # parity bits
    p1 = (d1 + d2 + d4) % 2
    p2 = (d1 + d3 + d4) % 2
    p3 = (d2 + d3 + d4) % 2
    return [p1, p2, d1, p3, d2, d3, d4]

def syndrome(codeword: List[int]) -> int:
    # returns syndrome integer (0 means no error)
    p1 = (codeword[0] + codeword[2] + codeword[4] + codeword[5]) % 2
    p2 = (codeword[1] + codeword[2] + codeword[5] + codeword[6]) % 2
    p3 = (codeword[3] + codeword[4] + codeword[5] + codeword[6]) % 2
    # syndrome bits p1 p2 p3 -> form index (1-based) of error bit
    return p3*4 + p2*2 + p1*1

def decode_7_4(codeword: List[int]) -> Tuple[List[int], bool]:
    """
    return (data_bits, corrected_flag)
    """
    if len(codeword) != 7:
        raise ValueError("codeword must be length 7")
    s = syndrome(codeword)
    cw = codeword.copy()
    corrected = False
    if s != 0:
        # flip the (s)th bit (1-indexed)
        idx = s - 1
        if 0 <= idx < 7:
            cw[idx] ^= 1
            corrected = True
    # extract data bits positions [2,4,5,6] (0-indexed 2,4,5,6)
    data = [cw[2], cw[4], cw[5], cw[6]]
    return data, corrected
