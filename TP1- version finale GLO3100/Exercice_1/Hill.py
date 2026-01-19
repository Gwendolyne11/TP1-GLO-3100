import numpy as np

def mod_inverse(matrix, mod):
    K = np.asarray(matrix, dtype=int)
    a, b = K[0, 0], K[0, 1]
    c, d = K[1, 0], K[1, 1]
    det = (a * d - b * c) % mod
    det = int(det)
    inv_det = pow(det, -1, mod)
    adj = np.array([[d, -b], [-c, a]], dtype=int) % mod
    return (inv_det * adj) % mod

def string_to_matrix(text, n):
    t = "".join(ch for ch in text.upper() if 'A' <= ch <= 'Z')
    if len(t) % n != 0:
        t += "X" * (n - (len(t) % n))
    cols = len(t) // n
    M = np.zeros((n, cols), dtype=int)
    k = 0
    for j in range(cols):
        for i in range(n):
            M[i, j] = ord(t[k]) - 65
            k += 1
    return M

def matrix_to_string(M):
    n, cols = M.shape
    out = []
    for j in range(cols):
        for i in range(n):
            out.append(chr((int(M[i, j]) % 26) + 65))
    return "".join(out)

#  Système 1
def hill_chriffement_system1(text_clair, key_matrix):
    n = key_matrix.shape[0]
    M = string_to_matrix(text_clair, n)
    C = (M.T.dot(key_matrix) % 26).T
    return matrix_to_string(C)

def hill_dechriffement_system1(text_chiffre, key_matrix):
    n = key_matrix.shape[0]
    K_inv = mod_inverse(key_matrix, 26)
    C = string_to_matrix(text_chiffre, n)
    P = (C.T.dot(K_inv) % 26).T
    return matrix_to_string(P)

# Système 2
def hill_chriffement_system2(text_clair, key_matrix):
    n = key_matrix.shape[0]
    M = string_to_matrix(text_clair, n)
    C = (key_matrix.dot(M) % 26)
    return matrix_to_string(C)

def hill_dechriffement_system2(text_chiffrer, key_matrix):
    n = key_matrix.shape[0]
    K_inv = mod_inverse(key_matrix, 26)
    C = string_to_matrix(text_chiffrer, n)
    P = (K_inv.dot(C) % 26)
    return matrix_to_string(P)


key_matrix = np.array([[3, 4],
                       [6, 3]])

text_clair = "JAMAIS DEUX SANS TROIS HAHAX"

chriffer1 = hill_chriffement_system1(text_clair, key_matrix)
chiffer2 = hill_chriffement_system2(text_clair, key_matrix)

print(" Système 1 (vecteur ligne * matrice) ")
print("Chiffré   :", chriffer1)
print("Déchiffré :", hill_dechriffement_system1(chriffer1, key_matrix))

print("\n Système 2 (avec la transposé) ")
print("Chiffré   :", chiffer2)
print("Déchiffré :", hill_dechriffement_system2(chiffer2, key_matrix))
