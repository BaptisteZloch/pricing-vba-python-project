# Projet VBA-Python
## A propos

Projet de construction d'un outil de pricing en utilisant un arbre trinomial d'options americaines et europeennes en VBA et répliqué en Python. Le tout en utilisant la programmation objet.
## Construction
- Racine = noeud initial
- Calculer le prix forward qui sera le noeud fils médian
- Puis calculer les up/down en multipliant/divisant par alpha : $\alpha=e^{\sigma\sqrt{3\times\Delta_t}}$

Input Marchés:
- vol $\sigma$
- $S_0$
- $r$
- $D$
  
Input modele:
- $N$
- $\Delta_t=\frac{T-t_0}{N}$
- $\alpha=e^{\sigma\sqrt{3\times\Delta_t}}$

Input Produits:
- $T$ 
- $K$
- call/put
- american vs european