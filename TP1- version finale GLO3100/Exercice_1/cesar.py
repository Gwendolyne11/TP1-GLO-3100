


messagechriffe = """UNXGHLWBTLCXGXLTBLITLLBMNITKEXLYKTGVTBLHNXLITZGHEFTBLVXJNXCXLTBLVXLMJNXMNOXNQHUMXGBKNGXUHGGXGHMXTVXIKXFBXKMKTOTBEIKTMBJNXEXLGHMXLLHGMBFIHKMTGMXLVXKMXL
FTBLVXGXLMITLVXJNBVHFIMXEXIENLEXLLXGMBXEVXLMWXIKXGWKXIETBLBKTVXJNXMNYTBLXGM
HNMVTLFHBCTBWNYNGTXVKBKXVXMIABABTEHKLIKXGWLNGXZKTGWXBGLIBKTMBHGVTKMNXGTNKTL
UXLHBGIHNKWXVABYYKXKEXIKHVATBGFXLLTZXMKHBLLXVHGWXLWXOKTBXGMLNYYBKX"""

def dechiffrement_cesar(y, b):
    """
    Trouve un message dechiffre  à l'aide du code de cesar en faissant un decalage de b.

    Args:
        y (str):Il s'agit du message qu'on veut dechiffré.
        b (int): indique le nombre de decalage qu'on veut effectuer.

    Returns:
        messagedechriffe (str): Il s'agit du message en clair avec le decalage donnée.

    Raises:
       TypeError: si les entrées y et b ne sont pas un str et int respectivement """

    if not isinstance(y, str):
        raise TypeError("Le message doit être une chaîne de caractères (str).")

    if not isinstance(b, int):
        raise TypeError("Le décalage doit être un entier (int).")

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    messagedechiffre = ""
    for lettre in y:
        if lettre.isalpha():
            valeurennombre = alphabet.index(lettre.upper())
            formule = (valeurennombre - b) % 26
            messagedechiffre += alphabet[formule]
        else:
            messagedechiffre += lettre
    return messagedechiffre

if __name__ == '__main__':

    for b in range(26):
        print(f"\n  Decalage = {b}")
        print(dechiffrement_cesar(messagechriffe, b))