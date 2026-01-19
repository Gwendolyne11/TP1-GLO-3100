import math

messagechriffe = """QJAROADEOLHEPQQRRSFEQJELQXE0QXXQREGGEDLJEOKVAOEOFADLOEKAROERQIBIRELQGEOIREU
IELIQFQDKERQOHQDOJEOELQXEOIDXEIKAGGEJEDSFEQIHEHSBBSKIJLEHEOLXHEKEKAIROHQSJJ
EIROSJWQKAGNSEDHELQXEOHQDOKEXREGSEREZERKSKE"""

def dechriffement_affine(message, a, b):
    """
    Déchiffre un message avec le chiffrement affine en utilisant la clé (a, b).

    Args:
        message (str): message chiffré (idéalement en MAJUSCULES A–Z, autres caractères conservés).
        a (int): coefficient multiplicatif (doit être inversible mod 26).
        b (int): décalage additif (0..25).

    Returns:
        str: message déchiffré en clair.

    Raises:
        TypeError: si text n'est pas str ou si a/b ne sont pas des int.
        ValueError: si a n'est pas inversible modulo 26.
    """
    if not isinstance(message, str):
        raise TypeError("text doit être une chaîne (str).")
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("a et b doivent être des entiers (int).")
    if math.gcd(a, 26) != 1:
        raise ValueError("a doit être  inversible dans Z26).")

    inv_a = pow(a, -1, 26)  # inverse mod 26
    messagedechriffe = ""
    for lettre in message:
        if lettre.isalpha():
            x = ord(lettre.upper()) - ord('A')
            p = (inv_a * (x - b)) % 26
            messagedechriffe += chr(p + ord('A'))
        else:
            messagedechriffe+= lettre

    return messagedechriffe

if __name__ == "__main__":

    valide_a = [a for a in range(1, 26) if math.gcd(a, 26) == 1]  #pgcd (a , 26) =1 , les a valides

    print("=== Déchiffrement Affine ===")
    for a in valide_a:
        for b in range(26):
            print(f"\n a={a}, b={b}")
            print(dechriffement_affine(messagechriffe, a, b))
