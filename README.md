# Cléopâtre — Espace Santé Beauté

Plateforme e-commerce « Quiet Luxury » pour la parapharmacie premium Cléopâtre (Ezzahra · Hammam-Lif, Tunisie).

**Stack** : Next.js (App Router) · React 19 · TypeScript strict · Tailwind CSS v4 (`@theme`) · Framer Motion · Drizzle ORM + PostgreSQL · Zod · Server Actions.

## Démarrage

```bash
cp .env.example .env          # ajuster DATABASE_URL / SESSION_SECRET
npm install
npm run db:push               # crée le schéma (drizzle-kit push)
npm run db:seed               # données de démonstration (81 produits, marques, promos, commandes)
npm run dev
```

## Comptes de démonstration

| Rôle    | E-mail                  | Mot de passe |
|---------|-------------------------|--------------|
| Admin   | admin@cleopatre.tn      | Admin123!    |
| Support | support@cleopatre.tn    | Support123!  |
| Client  | client@cleopatre.tn     | Client123!   |

Codes promo : `BIENVENUE10` (−10 % dès 50 DT), `SOLAIRE15` (−15 % univers Solaire), `LIVRAISON` (livraison offerte dès 40 DT), `CLEO20` (−20 DT dès 150 DT).

## Architecture

- `src/app/(site)` — vitrine : accueil, boutique, univers, catégories, besoins, marques, offres, recherche, produit, journal, boutiques, aide, légal, suivi, compte, panier, commande.
- `src/app/admin` — back-office (rôles admin / support) : dashboard, commandes (workflow + restock), produits, stock, clients, promotions, avis, support, recherches, journal, boutiques, audit, exports CSV.
- `src/actions` — Server Actions (auth, boutique, checkout, admin) avec validation Zod, rate-limit, vérification d'origine.
- `src/lib` — argent en millimes (`money.ts`), auth scrypt + sessions httpOnly (`auth.ts`), catalogue, moteur de promotions, commandes (verrouillage `FOR UPDATE`, idempotence, snapshots), i18n typée, presets de motion.
- `src/db/schema.ts` — 23 tables, index, contraintes uniques, relations.
- `src/components/icons` — système d'icônes SVG inline (viewBox 24, trait 1.5, `aria-hidden`).

## Sécurité & configuration

| Variable | Rôle |
|----------|------|
| `SESSION_SECRET` | **Obligatoire en production** (≥ 32 caractères). L'application refuse de démarrer si la variable est absente, trop courte ou égale à une valeur d'exemple. |
| `TRUST_PROXY` | `true` uniquement si l'application tourne derrière un reverse proxy/CDN qui pose `x-forwarded-for`. Sans cette variable, les en-têtes transmis sont **ignorés** : ils sont contrôlables par le client et permettaient de contourner tous les limiteurs de débit en les faisant tourner à chaque requête. Désactivée, tous les visiteurs partagent un seul compartiment — un avertissement est journalisé au démarrage en production. |
| `TRUST_PROXY_HOPS` | Nombre de proxys de confiance entre le client et l'application (défaut `1`). La lecture se fait **depuis la droite** de la chaîne `x-forwarded-for`, là où les valeurs ne sont pas falsifiables. |
| `PAYMENT_METHODS_ENABLED` | Sous-ensemble de `cod,bank_transfer,card,gift_card`. Défaut : `cod,bank_transfer,gift_card`. `card` est refusé par le serveur tant qu'aucune intégration réelle n'existe. |
| `SEED_ADMIN_PASSWORD` / `SEED_SUPPORT_PASSWORD` / `SEED_CLIENT_PASSWORD` | Mots de passe du seed. Les valeurs du tableau ci-dessus ne sont utilisées **qu'en développement**. |
| `ALLOW_DESTRUCTIVE_SEED` | `npm run db:seed` effectue un `TRUNCATE … CASCADE`. Avec `NODE_ENV=production`, le script s'arrête immédiatement sauf si cette variable vaut `1` (et les mots de passe ci-dessus sont alors exigés). |

Accès invité à une commande : le numéro de commande n'est **pas** un identifiant d'authentification. La page de confirmation exige soit une session propriétaire, soit la clé d'accès (`access_key`, 256 bits) remise à la création de la commande ; `/suivi` demande le numéro **et** l'e-mail (ou la clé). Les commandes créées avant l'ajout de `access_key` restent consultables via `/suivi`.

## Principes

- Tous les montants sont des entiers en **millimes** (1 DT = 1000).
- Animations : transform + opacity uniquement, `prefers-reduced-motion` respecté.
- Palette : papier / pierre / sable / encre + accent champagne. Aucune couleur violette ou verte vive.
- Copy en français ; structure i18n prête pour l'arabe (RTL).

## Validation

```bash
npx next typegen && npx tsc --noEmit && npm run build
```
