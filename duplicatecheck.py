from collections import Counter
import hashlib

def hash(weights: Counter[str, int]) -> int:
    '''
    Given a Counter that stores how many times each token appeared in a page,
    calculate the simhash value of the page.
    '''
    hashes = dict()
    combreversed = [0] * 256 # result of hash would be 256 bits
    for token in weights:
        hashed = hashlib.sha256(token.encode())
        hashes[token] = hashed
    for k,v in hashes.items():
        num = int(v.hexdigest(), 16)
        weight = weights[k]
        counter = 0
        while counter != 256:
            bit = num % 2
            if bit == 1:
                combreversed[counter] += weight
            else:
                combreversed[counter] -= weight
            num = num // 2
            counter += 1
    simhash_value = 0
    for bit in combreversed[::-1]:
        if bit > 0:
            simhash_value = simhash_value * 2 + 1
        else:
            simhash_value *= 2
    return simhash_value

def hash_distance(hash1: int, hash2: int) -> int:
    '''
    Given two simhash values, calculate the distance between the two
    '''
    return bin(hash1 ^ hash2).count('1')

def duplicate_exists(target_hash, prev_simhash):
    '''
    Given a simhash value of page, iterate through the simhash values
    of pages visited previously. Return True if there a page with a simhash 
    value with a distance <= 20.
    '''
    for prev in prev_simhash:
        calc = hash_distance(prev, target_hash)
        if calc <= 20:
            return True
    return False