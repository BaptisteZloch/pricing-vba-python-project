# Projet VBA-Python
## A propos

Projet de construction d'un outil de pricing en utilisant un arbre trinomial d'options americaines et europeennes en VBA et répliqué en Python. Le tout en utilisant la programmation objet.
## Construction
- Racine = noeud initial
- Calculer le prix forward qui sera le noeud fils médian
- Puis calculer les up/down en multipliant/divisant par alpha : $\alpha=e^{\sigma\sqrt{3\times\Delta_t}}$
- Calcule des probabilités : contraines $\Sigma=1$, espérance ($\mathbb{E}[S_{t_{i+1}}|S_{t_i}]=S_{t_i}e^{r\Delta_t}-D_{t_{i+1}}$) = noeud median (meme espérance qu'un process continue)
- 

### Objets : 
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


Node:
- S
- $p_{up}$, $p$, $p_{down}$
- V
