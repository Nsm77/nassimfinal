# Corrections apportées pendant la fabrication du kit

Chaque ligne est une faute **réelle** trouvée par un contrôle, avec ce qui l'a trouvée et ce qui a été
fait. Aucune n'a été effacée du document une fois corrigée : un kit qui cache ses corrections cache
aussi ses méthodes. Les statuts vont du bloquant (le rendu était faux) au cosmétique (une tournure).
Les P0 et P1 ont été traités avant le gel ; la liste est close par le constat `audit/RIEN-A-AJOUTER.md`.

| id | faute | trouvée par | correction | statut |
| --- | --- | --- | --- | --- |
| C01 | Le rapport revendiquait une contrainte `check` au schéma pour tenir le stock ; le dépôt n'en déclare aucune. | relecture du gisement, puis QA-2 | phrase réécrite : zéro contrainte au schéma, garde en code `src/lib/orders.ts:100-101` ; dette assumée écrite en IV.2 | P0 réglé |
| C02 | Réduction de mouvement annoncée par un hook React : `useReducedMotion` n'apparaît aucune fois. | extraction `facts.py` | fait supprimé, remplacé par la mesure réelle : une règle CSS `src/app/globals.css:161`, un fichier concerné | P0 réglé |
| C03 | Un fait `reduction_mouvement_retard_ms` inventé de toutes pièces (aucune règle correspondante). | extracteur, valeur `None` | fait retiré de `facts.py` ; un fait à `None` se supprime, il ne s'affiche pas | P0 réglé |
| C04 | Nombre de tables annoncé 23 dans une notice ; le schéma en déclare 24. | recomptage par `grep` (QA-2 du second harnais) | nombre corrigé à la source de la notice | P0 réglé |
| C05 | `data/products.json` cité comme gisement de catalogue : le fichier n'existe pas. | QA-3 (chemins cités) | citation remplacée par le manifeste réel `public/data/product-image-manifest.json` | P0 réglé |
| C06 | Fenêtre d'idempotence annoncée « en minutes » ; le code compte en millisecondes. | relecture `src/actions/checkout.ts` | unité corrigée dans le texte et la figure | P0 réglé |
| C07 | Les entités HTML (`&amp;`, `&#160;`) s'imprimaient dans les titres, les légendes et l'appareil de notes. | loi PONCTUATION_COLLÉE (faux positif sur `&amp;`) puis lecture du rendu | `doc.verifier_langue` neutralise chaque entité par des espaces de même longueur avant les scans ; l'échappement est posé à la source par `_legal` | P0 réglé |
| C08 | Espace insécable choisie U+202F : le composeur la cassait en espace ordinaire à l'impression. | rendu (petits carrés puis mesures) | insécable fixée à U+00A0, seule tenue par le moteur de police | P0 réglé |
| C09 | Le sommaire et les listes cliquables comptaient 232 ancres pour 233 signets. | QA-6 (accord ancre/signet) | `Fab.hors_numerotation()` pose l'ancre des annexes non numérotées | P0 réglé |
| C10 | Le résumé et la quatrième de couverture héritaient du compteur de la sixième partie (« 6.9 Quatrième »). | assaut A19 (sonde d'appareil) | section hors numérotation ; titre rendu sans numéro, signet conservé | P0 réglé |
| C11 | Une figure dessinée mais jamais citée (INV-13 violé sans bruit) après une édition de contenu. | contrôle d'orphelinage muet | le contrôle est remonté dans `construire_texte`, donc le `--dry-run` le refuse aussi | P0 réglé |
| C12 | Oscillation du nombre de pages 104 ↔ 105 d'un build à l'autre. | `--determinisme` (empreinte divergente) | plafond de passes porté à six et convergence mesurée deux fois de suite | P0 réglé |
| C13 | `mutation.py` s'organisait autour d'un fait saisi à la main : la faute M1 ne faisait rougir aucun contrôle. | revue de la loi de mutation | fautes M1 à M3 changées pour toucher des gardes réelles (citation de figure, ponctuation collée, extrait hors bornes) | P1 réglé |
| C14 | `chaos.py` cas C4 : la restauration du répertoire `figs/` levait `FileNotFoundError` (`shutil.move` avait **renomé** le dossier). | exécution du procès-verbal C4 | restauration par `rmtree` puis `move` du répertoire temporaire ; le cas est conforme | P1 réglé |
| C15 | Le récapitulatif de mutation levait `KeyError` (`x.get('titre', x['statut'])` évalué avant le test). | exécution | expression par défaut retirée, accesseurs explicites | P1 réglé |
| C16 | Le second harnais exemptait le verbatim en cherchant « mono » dans des fontes Times/Helvetica : zéro span de prose, donc zéro faute déclarée par silence. | première confrontation `ab.py` | la fonte du corps est DejaVu ; la discrimination se fait sur « Mono » et le nombre de spans tenus à part est imprimé | P1 réglé |
| C17 | Regroupement des spans par ordonnée seule : la deuxième ligne d'une cellule se recollait à la première de la voisine, dix-huit emprunts anglais imaginaires. | deuxième divergence `ab.py` | une ligne visuelle = un bloc et une ordonnée, tels que le moteur de texte les donne | P1 réglé |
| C18 | Critère « écart horizontal supérieur à un espace » pour couper une ligne : huit « lignes » commençant par deux-points sur du texte justifié. | troisième divergence `ab.py` | le blanc ne tranche plus la ligne ; la marque d'identifiant est cherchée à ±2 caractères | P1 réglé |
| C19 | Région anglaise bornée par le premier titre « Abstract » : le premier est celui du sommaire, la région se refermait sur rien. | quatrième divergence `ab.py` | qa2 juge la **langue de la ligne** par ses mots outils et consigne les huit lignes anglaises hors champ | P1 réglé |
| C20 | Classe de caractères `A-Zaiz…` écrite sans plage : la loi d'emprunt laissait passer « cart » dans « carte ». | assaut A08 puis QA-5 | classes en plages (`A-Za-zàâä…À-Ÿ`) ; quatre-vingt-onze faux positifs effacés d'un coup | P1 réglé |
| C21 | Loi de ponctuation fautive sur les identifiants de code (`src/db/schema.ts:151`, `16:9`). | scan des cinq cents lignes candidate | le deux-points n'est exempté que suivi d'un chiffre ou de `//` ; les identifiants passent en verbatim | P1 réglé |
| C22 | Cinq cellules d'identifiants en prose dans la table des fautes connues : la loi les condamnait à juste titre. | langue-rendu | littéraux passés en backticks (exemptés par la fonte, et le comptage le dit) | P1 réglé |
| C23 | Mot « items » dans la légende d'une planche de traçabilité. | assaut A08 | « les lignes en attente sont conservées telles quelles » ; la légende ne perd rien | P1 réglé |
| C24 | Porte G8 libellée « environ 120 pages » : un objectif, pas une mesure. | assaut A04 (nombre sans origine) | libellé mesurable : entre le plancher et le plafond de pages, tout vectoriel | P1 réglé |
| C25 | Hypothèse de repli Shopify mentionnée par le cahier sans trace dans le dépôt, et un temps décrite comme « lue dans le code ». | relecture de vérité (§2) | I.4 nomme la demande, inscrit la recherche (`grep` : zéro ligne) et le motif du renoncement ; la carte Q4 de la banque du jury dit la même chose | P1 réglé |
| C26 | Scan de secrets fondé sur `git ls-files` : le kit n'étant pas encore indexé, le périmètre était creux. | relecture de QA-10 | périmètre pris sur l'arborescence du kit (cinquante fichiers), plus `git ls-files` pour les `.env` suivis ; le constat `drizzle.config.json` (URL de base de développement en clair, commit initial) est écrit, pas masqué | P1 réglé |
| C27 | Numéro de téléphone réel des boutiques, présent dans le seed, prêt à être imprimé. | relecture de prudence | champ non reproduit dans le PDF ; la raison est écrite dans la légende | P1 réglé |
| C28 | Coquille `SCESCELLEMENT` dans l'acte B0 (chemin du futur sceau). | porte G2 (la sienne) | ligne réécrite vers `audit/sceau.json` | P2 réglé |
| C29 | À la couverture, le gabarit `[logo établissement]` débordait de son cadre (le texte mesurait 55 pt pour 42 pt de cadre) et la légende du monogramme était imprimée en couleur papier sur papier. | relecture d'un rendu PNG de la page 1, après le scellement | la légende passe en gris ; `[logo]` est ajusté à la largeur utile mesurée par `stringWidth`, `[établissement]` est posé sous le cadre comme l'autre légende ; le PDF est recalculé et rescellé dans le même commit | P2 réglé |

## Règles d'arrêt appliquées

1. Un rouge de contrôle se règle à la source des données ou du texte, jamais en adoucissant le contrôle.
2. Une figure qui ment sur le code se corrige dans l'extracteur, pas dans sa légende.
3. Trois signalements sur le même objet arrêtent la fabrication et ouvrent une décision dans `decisions.md`.
