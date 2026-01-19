#!/usr/bin/env python3
"""
Calcul de la transformée de Walsh-Hadamard et de la non-linéarité
d'une fonction booléenne f(x1, x2, x3) = x1·x2 ⊕ x3

Pour exécuter: python walsh_hadamard.py
"""

import itertools
from typing import List, Tuple


def generate_all_binary_vectors(n: int) -> List[List[int]]:
    """
    Génère tous les vecteurs binaires de longueur n.
    
    Args:
        n: Longueur des vecteurs
        
    Returns:
        Liste de tous les vecteurs binaires possibles
    """
    return [list(vec) for vec in itertools.product([0, 1], repeat=n)]


def boolean_function(x: List[int]) -> int:
    """
    Fonction booléenne f(x1, x2, x3) = x1·x2 ⊕ x3
    
    Args:
        x: Vecteur d'entrée [x1, x2, x3]
        
    Returns:
        Résultat de la fonction (0 ou 1)
    """
    if len(x) != 3:
        raise ValueError("La fonction attend exactement 3 variables")
    
    x1, x2, x3 = x
    return (x1 & x2) ^ x3


def dot_product_mod2(x: List[int], y: List[int]) -> int:
    """
    Calcule le produit scalaire de deux vecteurs binaires modulo 2.
    
    Args:
        x: Premier vecteur binaire
        y: Deuxième vecteur binaire
        
    Returns:
        Produit scalaire modulo 2 (0 ou 1)
    """
    if len(x) != len(y):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    
    return sum(x[i] * y[i] for i in range(len(x))) % 2


def walsh_hadamard_coefficient(a: List[int], all_vectors: List[List[int]]) -> int:
    """
    Calcule le coefficient de Walsh-Hadamard Wf(a).
    
    Args:
        a: Vecteur pour lequel calculer le coefficient
        all_vectors: Tous les vecteurs binaires de l'espace
        
    Returns:
        Coefficient de Walsh-Hadamard
    """
    coefficient = 0
    
    for x in all_vectors:
        # Calcul de (-1)^(f(x) + <a,x>)
        exponent = (boolean_function(x) + dot_product_mod2(a, x)) % 2
        coefficient += (-1) ** exponent
    
    return coefficient


def compute_nonlinearity(n: int) -> Tuple[List[Tuple[List[int], int]], int, float]:
    """
    Calcule la non-linéarité d'une fonction booléenne.
    
    Args:
        n: Nombre de variables de la fonction
        
    Returns:
        Tuple contenant:
        - Liste des coefficients de Walsh-Hadamard pour chaque vecteur
        - Valeur absolue maximale des coefficients (hors zéro)
        - Non-linéarité de la fonction
    """
    all_vectors = generate_all_binary_vectors(n)
    walsh_coefficients = []
    non_zero_absolute_values = []
    
    # Calculer tous les coefficients de Walsh-Hadamard
    for a in all_vectors:
        wf_a = walsh_hadamard_coefficient(a, all_vectors)
        walsh_coefficients.append((a.copy(), wf_a))
        
        # Collecter les valeurs absolues non nulles (a ≠ [0,0,0])
        if a != [0] * n:
            non_zero_absolute_values.append(abs(wf_a))
    
    # Trouver la valeur absolue maximale
    w_max = max(non_zero_absolute_values) if non_zero_absolute_values else 0
    
    # Calculer la non-linéarité: NL(f) = 2^(n-1) - W_max/2
    nonlinearity = 2**(n-1) - w_max/2
    
    return walsh_coefficients, w_max, nonlinearity


def display_results(walsh_coefficients: List[Tuple[List[int], int]], 
                   w_max: int, nonlinearity: float, n: int) -> None:
    """
    Affiche les résultats de manière formatée.
    """
    print("=" * 50)
    print("           TRANSFORMÉE DE WALSH-HADAMARD")
    print("=" * 50)
    print(f"Fonction: f(x1, x2, x3) = x1·x2 ⊕ x3")
    print()
    
    print("Coefficients de Walsh-Hadamard:")
    print("-" * 30)
    for a, wf_a in walsh_coefficients:
        print(f"Wf({a}) = {wf_a:2d}")
    
    print()
    print("RÉSULTATS:")
    print("-" * 30)
    print(f"W_max = {w_max}")
    print(f"Non-linéarité NL(f) = {nonlinearity}")

    # Calcul de la non-linéarité maximale théorique
    nl_max_theoretical = (2 ** (n - 1)) - (2 ** ((n // 2) - 1))
    
    # Interprétation
    print()
    print("INTERPRÉTATION:")
    print("-" * 30)
    if nonlinearity == nl_max_theoretical:
        print(f"La fonction est optimalement non-linéaire (NL_max = {nl_max_theoretical})")
    elif nonlinearity >= nl_max_theoretical * 0.75:  # 75% du max
        print(f"La fonction a une très bonne non-linéarité ({nonlinearity}/{nl_max_theoretical})")
    elif nonlinearity >= nl_max_theoretical * 0.5:   # 50% du max
        print(f"La fonction a une bonne non-linéarité ({nonlinearity}/{nl_max_theoretical})")
    else:
        print(f"La fonction a une faible non-linéarité ({nonlinearity}/{nl_max_theoretical})")


def main():
    """Fonction principale."""
    try:
        # Nombre de variables de la fonction booléenne
        n = 3
        
        # Calcul des coefficients et de la non-linéarité
        walsh_coeffs, w_max, nonlinearity = compute_nonlinearity(n)
        
        # Affichage des résultats
        display_results(walsh_coeffs, w_max, nonlinearity, n)
        
    except Exception as e:
        print(f"Erreur: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
