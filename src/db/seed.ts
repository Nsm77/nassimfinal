import "dotenv/config";
import { randomBytes, scrypt as _scrypt } from "node:crypto";
import { promisify } from "node:util";
import { sql } from "drizzle-orm";
import { db, pool } from "./index";
import {
  addresses, articles, brands, categories, concerns, inventoryMovements, orderEvents, orderItems, orders,
  productConcerns, products, promotions, reviews, stores, users,
} from "./schema";
import { PRODUCT_IMAGES } from "./productImages";

const scrypt = promisify(_scrypt) as (p: string, s: string, n: number) => Promise<Buffer>;
async function hash(pw: string) {
  const salt = randomBytes(16).toString("hex");
  return `scrypt$${salt}$${(await scrypt(pw, salt, 64)).toString("hex")}`;
}
const slug = (s: string) =>
  s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

/**
 * This script TRUNCATEs every table. It is a development convenience, so make
 * running it against a real database a deliberate act rather than an accident:
 *   • NODE_ENV=production aborts unless ALLOW_DESTRUCTIVE_SEED=1 is also set.
 *   • when forced in production, the demo passwords are NOT used — real ones
 *     must be supplied, so no seeded admin ever carries a published credential.
 */
const IS_PROD_SEED = (process.env.NODE_ENV ?? "development") === "production";
const FORCED = process.env.ALLOW_DESTRUCTIVE_SEED === "1";

function assertSafeToSeed() {
  if (IS_PROD_SEED && !FORCED) {
    console.error("\n✖ Seed aborted — NODE_ENV=production.");
    console.error("  This script runs TRUNCATE … CASCADE on every table and would destroy live data.");
    console.error("  If you truly intend this, re-run with ALLOW_DESTRUCTIVE_SEED=1.\n");
    process.exit(1);
  }
  if (IS_PROD_SEED) {
    console.warn("⚠ ALLOW_DESTRUCTIVE_SEED=1 — wiping a production database.");
    for (const v of ["SEED_ADMIN_PASSWORD", "SEED_SUPPORT_PASSWORD"]) {
      if (!process.env[v]) {
        console.error(`✖ ${v} must be set: demo passwords are never used for production accounts.`);
        process.exit(1);
      }
    }
  } else {
    console.warn("⚠ Development seed — about to TRUNCATE all tables.");
  }
}

const demoPassword = (name: string, fallback: string) => {
  const v = process.env[name];
  if (v) return v;
  if (IS_PROD_SEED) {
    console.error(`✖ ${name} is required when seeding production.`);
    process.exit(1);
  }
  return fallback;
};

async function main() {
  assertSafeToSeed();
  console.log("→ Reset");
  await db.execute(sql`TRUNCATE TABLE
    loyalty_transactions, support_tickets, audit_logs, analytics_events, search_events, newsletter_subscribers,
    wishlist_items, order_events, order_items, orders, promotions, inventory_movements, reviews, product_concerns,
    products, concerns, categories, brands, articles, stores, addresses, sessions, users
    RESTART IDENTITY CASCADE`);

  console.log("→ Users");
  const ADMIN_PW = demoPassword("SEED_ADMIN_PASSWORD", "Admin123!");
  const SUPPORT_PW = demoPassword("SEED_SUPPORT_PASSWORD", "Support123!");
  const CLIENT_PW = demoPassword("SEED_CLIENT_PASSWORD", "Client123!");
  const [admin, support, customer] = await db.insert(users).values([
    { email: "admin@cleopatre.tn", passwordHash: await hash(ADMIN_PW), firstName: "Nour", lastName: "Ben Salah", role: "admin", phone: "71430500" },
    { email: "support@cleopatre.tn", passwordHash: await hash(SUPPORT_PW), firstName: "Sami", lastName: "Trabelsi", role: "support", phone: "71430501" },
    { email: "client@cleopatre.tn", passwordHash: await hash(CLIENT_PW), firstName: "Ines", lastName: "Mansour", role: "customer", phone: "22345678", loyaltyPoints: 42 },
  ]).returning();
  await db.insert(addresses).values({
    userId: customer.id, label: "Domicile", fullName: "Ines Mansour", phone: "22345678", line1: "12 rue des Jasmins", city: "Ezzahra", governorate: "Ben Arous", postalCode: "2034", isDefault: true,
  });

  console.log("→ Brands");
  const brandRows = await db.insert(brands).values([
    { slug: "la-roche-posay", name: "La Roche-Posay", country: "France", isFeatured: true, story: "Née d'une source thermale aux vertus apaisantes, La Roche-Posay conçoit des soins dermatologiques minimalistes, testés sur peaux sensibles, recommandés par plus de 90 000 dermatologues." },
    { slug: "avene", name: "Avène", country: "France", isFeatured: true, story: "Au cœur des Cévennes, l'Eau thermale d'Avène apaise les peaux les plus réactives depuis 1743. Une science de la douceur, formulée avec le strict nécessaire." },
    { slug: "vichy", name: "Vichy", country: "France", isFeatured: true, story: "L'eau volcanique de Vichy, riche en 15 minéraux, fortifie la peau et renforce sa barrière. Des soins efficaces, pensés pour toutes les étapes de la vie." },
    { slug: "bioderma", name: "Bioderma", country: "France", isFeatured: true, story: "Pionnière de l'écobiologie, Bioderma respecte l'écosystème naturel de la peau. Sa Sensibio H2O a inventé l'eau micellaire." },
    { slug: "nuxe", name: "Nuxe", country: "France", isFeatured: true, story: "L'alliance de la nature et du plaisir sensoriel. L'Huile Prodigieuse, culte depuis 1991, incarne le luxe accessible à la française." },
    { slug: "caudalie", name: "Caudalie", country: "France", isFeatured: true, story: "Née dans les vignobles bordelais, Caudalie puise dans les polyphénols de raisin des actifs antioxydants d'une rare pureté." },
    { slug: "uriage", name: "Uriage", country: "France", story: "L'Eau thermale d'Uriage, isotonique et riche en oligo-éléments, hydrate et apaise. Une douceur alpine pour toute la famille." },
    { slug: "svr", name: "SVR", country: "France", story: "Laboratoire dermatologique indépendant, SVR formule des soins sur-dosés en actifs, avec une exigence pharmaceutique." },
    { slug: "mustela", name: "Mustela", country: "France", story: "Depuis 1950, Mustela accompagne la peau des bébés et des mamans avec des formules d'origine naturelle, douces et sûres." },
    { slug: "ducray", name: "Ducray", country: "France", story: "Expert dermatologique du cuir chevelu et de la peau depuis 1930. Des soins ciblés, efficaces et respectueux." },
    { slug: "eucerin", name: "Eucerin", country: "Allemagne", story: "Cent ans de recherche dermatologique allemande au service de la peau sèche, sensible et sujette aux imperfections." },
    { slug: "filorga", name: "Filorga", country: "France", isFeatured: true, story: "Issue de la médecine esthétique, Filorga transpose l'expertise des laboratoires en soins anti-âge d'exception." },
    { slug: "isdin", name: "ISDIN", country: "Espagne", story: "Référence méditerranéenne de la photoprotection. Des textures invisibles qui réinventent le plaisir de se protéger." },
    { slug: "arkopharma", name: "Arkopharma", country: "France", story: "Leader de la phytothérapie, Arkopharma sélectionne des plantes d'origine contrôlée pour des compléments d'une grande pureté." },
    { slug: "klorane", name: "Klorane", country: "France", story: "La botanique au service des cheveux. Des shampooings emblématiques formulés autour d'une plante signature." },
    { slug: "cerave", name: "CeraVe", country: "États-Unis", story: "Développée avec des dermatologues, CeraVe restaure la barrière cutanée grâce à trois céramides essentiels." },
  ]).returning();
  const B = Object.fromEntries(brandRows.map((b) => [b.slug, b.id]));

  console.log("→ Universes & categories");
  const universeDefs = [
    { slug: "visage", name: "Visage", image: "/images/u-visage.jpg", description: "Nettoyants, sérums, hydratants et soins ciblés.", story: "Le visage se soigne avec patience. Nous avons sélectionné des formules précises, dosées avec justesse, pour une peau équilibrée saison après saison.", children: ["Nettoyants & démaquillants", "Sérums", "Hydratants", "Anti-âge", "Contour des yeux", "Peaux à imperfections"] },
    { slug: "corps", name: "Corps", image: "/images/u-corps.jpg", description: "Hydratation, douche, mains et soins spécifiques.", story: "Un rituel corps quotidien, pensé pour la peau du bassin méditerranéen : hydratation profonde, textures fondantes, parfums discrets.", children: ["Hydratants corps", "Douche & bain", "Mains & pieds", "Vergetures & fermeté"] },
    { slug: "cheveux", name: "Cheveux", image: "/images/u-cheveux.jpg", description: "Shampooings, soins, chute et cuir chevelu.", story: "Des cheveux sains commencent par un cuir chevelu apaisé. Notre sélection privilégie la botanique et la dermatologie.", children: ["Shampooings", "Après-shampooings & masques", "Anti-chute", "Cuir chevelu sensible"] },
    { slug: "solaire", name: "Solaire", image: "/images/u-solaire.jpg", description: "Protection très haute, après-soleil et autobronzants.", story: "Sous le soleil tunisien, la protection n'est pas une option. Des textures invisibles, résistantes à l'eau, pour toute la famille.", children: ["Protection visage", "Protection corps", "Après-soleil", "Enfants"] },
    { slug: "bebe-maman", name: "Bébé & Maman", image: "/images/u-bebe.jpg", description: "Toilette, change, hydratation et grossesse.", story: "La douceur comme seule exigence. Des formules sûres, d'origine naturelle, pour les premières années et la maternité.", children: ["Toilette bébé", "Change", "Soins maman"] },
    { slug: "complements", name: "Compléments", image: "/images/u-complements.jpg", description: "Vitalité, immunité, sommeil, beauté de l'intérieur.", story: "Compléter sans excès. Des actifs d'origine contrôlée, aux dosages utiles, conseillés par nos pharmaciens.", children: ["Vitalité & immunité", "Sommeil & stress", "Beauté in & out", "Digestion"] },
    { slug: "hygiene", name: "Hygiène & Bien-être", image: "/images/u-hygiene.jpg", description: "Bucco-dentaire, intime, déodorants et essentiels.", story: "Les essentiels du quotidien, choisis pour leur tolérance et leur efficacité, sans superflu.", children: ["Bucco-dentaire", "Hygiène intime", "Déodorants", "Premiers soins"] },
  ];
  const U: Record<string, number> = {};
  const C: Record<string, number> = {};
  let order = 0;
  for (const u of universeDefs) {
    const [row] = await db.insert(categories).values({ slug: u.slug, name: u.name, description: u.description, story: u.story, image: u.image, isUniverse: true, sortOrder: order++ }).returning();
    U[u.slug] = row.id;
    let i = 0;
    for (const c of u.children) {
      const s = slug(c);
      const [cr] = await db.insert(categories).values({ slug: s, name: c, parentId: row.id, image: u.image, sortOrder: i++, description: `${c} — sélection ${u.name.toLowerCase()} Cléopâtre.` }).returning();
      C[s] = cr.id;
    }
  }

  console.log("→ Concerns");
  const concernRows = await db.insert(concerns).values([
    { slug: "peau-sensible", name: "Peau sensible", intro: "Une peau sensible réagit vite : rougeurs, tiraillements, inconfort. La règle : moins d'ingrédients, plus de tolérance." },
    { slug: "peau-seche", name: "Peau sèche", intro: "La peau sèche manque de lipides. On restaure la barrière avec des céramides, du beurre de karité et de la glycérine." },
    { slug: "acne", name: "Imperfections & acné", intro: "Régulation du sébum, exfoliation douce et hydratation non comédogène : les trois piliers d'une peau nette." },
    { slug: "anti-age", name: "Anti-âge", intro: "Rétinol, vitamine C, acide hyaluronique et protection solaire quotidienne : l'essentiel, sans promesses excessives." },
    { slug: "taches", name: "Taches pigmentaires", intro: "Les taches se préviennent d'abord avec un SPF 50+. Les actifs éclaircissants font le reste, avec régularité." },
    { slug: "hydratation", name: "Hydratation", intro: "Une peau hydratée est une peau confortable, lumineuse et mieux protégée." },
    { slug: "chute-de-cheveux", name: "Chute de cheveux", intro: "Saisonnière ou réactionnelle, la chute se traite par cures : compléments ciblés et soins stimulants." },
    { slug: "pellicules", name: "Pellicules", intro: "Apaiser le cuir chevelu et réguler la flore : la clé d'un cuir chevelu net durablement." },
    { slug: "protection-solaire", name: "Protection solaire", intro: "Un SPF 50+ chaque matin est le geste anti-âge et anti-taches le plus efficace qui soit." },
    { slug: "immunite", name: "Immunité & vitalité", intro: "Vitamine C, D, zinc et probiotiques soutiennent les défenses naturelles en période de fatigue." },
    { slug: "sommeil", name: "Sommeil & stress", intro: "Mélatonine, magnésium et plantes apaisantes accompagnent un sommeil réparateur." },
  ]).returning();
  const K = Object.fromEntries(concernRows.map((c) => [c.slug, c.id]));

  console.log("→ Products");
  type P = [name: string, brand: string, universe: string, cat: string, price: number, compare: number | null, vol: string, concerns: string[], short: string, opts?: { featured?: boolean; isNew?: boolean; stock?: number }];
  const P: P[] = [
    // Visage
    ["Effaclar Gel Moussant Purifiant", "la-roche-posay", "visage", "nettoyants-demaquillants", 42_900, 47_500, "400 ml", ["acne", "peau-sensible"], "Nettoie en douceur les peaux grasses à tendance acnéique.", { featured: true }],
    ["Toleriane Dermo-Nettoyant", "la-roche-posay", "visage", "nettoyants-demaquillants", 49_900, null, "400 ml", ["peau-sensible"], "Démaquille et nettoie sans frotter les peaux intolérantes."],
    ["Sensibio H2O Eau Micellaire", "bioderma", "visage", "nettoyants-demaquillants", 38_500, 44_900, "500 ml", ["peau-sensible"], "L'originale. Démaquille et apaise en un seul geste.", { featured: true }],
    ["Sébium Gel Moussant", "bioderma", "visage", "nettoyants-demaquillants", 34_900, null, "500 ml", ["acne"], "Purifie sans dessécher les peaux mixtes à grasses."],
    ["Vinoclean Mousse Nettoyante", "caudalie", "visage", "nettoyants-demaquillants", 52_000, null, "150 ml", ["hydratation"], "Mousse onctueuse à la sève de vigne, pour un teint frais."],
    ["Hyalu B5 Sérum", "la-roche-posay", "visage", "serums", 129_000, 145_000, "30 ml", ["anti-age", "hydratation"], "Repulpe et répare avec deux acides hyaluroniques et vitamine B5.", { featured: true }],
    ["Minéral 89 Booster Quotidien", "vichy", "visage", "serums", 89_900, null, "50 ml", ["hydratation"], "89 % d'eau volcanique et acide hyaluronique pour fortifier la peau.", { featured: true }],
    ["Vinoperfect Sérum Éclat", "caudalie", "visage", "serums", 158_000, null, "30 ml", ["taches", "anti-age"], "62 fois plus efficace que la vitamine C sur les taches. Sans parfum."],
    ["Pure Vitamin C10 Sérum", "la-roche-posay", "visage", "serums", 119_000, null, "30 ml", ["anti-age", "taches"], "Vitamine C pure à 10 % pour un éclat renouvelé et des rides lissées."],
    ["Ampoules Concentrées C+", "svr", "visage", "serums", 98_000, 112_000, "30 ml", ["anti-age"], "Vitamine C stabilisée pour illuminer et protéger la peau."],
    ["NCEF-Reverse Crème Suprême", "filorga", "visage", "anti-age", 249_000, null, "50 ml", ["anti-age"], "Régénération cellulaire multi-corrective inspirée de la médecine esthétique.", { featured: true }],
    ["Time-Filler Crème Anti-rides", "filorga", "visage", "anti-age", 189_000, 215_000, "50 ml", ["anti-age"], "Corrige tous les types de rides, même celles d'expression."],
    ["Liftactiv Collagen Specialist", "vichy", "visage", "anti-age", 135_000, null, "50 ml", ["anti-age"], "Peptides et vitamine C pour relancer la production de collagène."],
    ["Resveratrol-Lift Crème Cachemire", "caudalie", "visage", "anti-age", 149_000, null, "50 ml", ["anti-age"], "Texture cachemire, resvératrol de vigne et acide hyaluronique."],
    ["Hydrance Aqua-Gel", "avene", "visage", "hydratants", 69_900, null, "50 ml", ["hydratation", "peau-sensible"], "Hydratation légère 3-en-1 : crème, masque de nuit et base éclat."],
    ["Toleriane Sensitive Crème", "la-roche-posay", "visage", "hydratants", 59_900, null, "40 ml", ["peau-sensible", "hydratation"], "Hydratant prébiotique pour peaux sensibles, sans parfum."],
    ["Crème Hydratante Visage", "cerave", "visage", "hydratants", 47_900, 54_000, "52 ml", ["peau-seche", "hydratation"], "Trois céramides essentiels et acide hyaluronique. Non comédogène.", { isNew: true }],
    ["Crème Prodigieuse Boost Gel-Baume", "nuxe", "visage", "hydratants", 84_000, null, "40 ml", ["hydratation"], "Repulpe et lisse avec la fleur de jasmin, parfum délicat."],
    ["Aquaphor Baume Réparateur", "eucerin", "visage", "hydratants", 39_900, null, "45 ml", ["peau-seche"], "Répare les peaux très sèches, gercées ou irritées."],
    ["Physiolift Yeux", "avene", "visage", "contour-des-yeux", 79_000, null, "15 ml", ["anti-age"], "Défroisse, décongestionne et illumine le regard."],
    ["Hyalu B5 Yeux", "la-roche-posay", "visage", "contour-des-yeux", 92_000, null, "15 ml", ["anti-age", "hydratation"], "Repulpe le contour des yeux et atténue les cernes."],
    ["Effaclar Duo+ M", "la-roche-posay", "visage", "peaux-a-imperfections", 62_900, 69_900, "40 ml", ["acne"], "Soin anti-imperfections corrigeant, désincrustant et anti-marques.", { featured: true }],
    ["Sébium Global", "bioderma", "visage", "peaux-a-imperfections", 58_000, null, "30 ml", ["acne"], "Soin intensif purifiant pour peaux à imperfections sévères."],
    ["Cleanance Comedomed", "avene", "visage", "peaux-a-imperfections", 61_000, null, "30 ml", ["acne", "peau-sensible"], "Concentré anti-imperfections au Comedoclastin™."],
    ["Normaderm Phytosolution", "vichy", "visage", "peaux-a-imperfections", 64_900, null, "50 ml", ["acne", "hydratation"], "Double correction : imperfections et barrière cutanée."],
    ["Sebiaclear Sérum", "svr", "visage", "peaux-a-imperfections", 71_000, null, "30 ml", ["acne", "taches"], "Réduit les imperfections et les marques en 7 jours."],
    // Corps
    ["Lipikar Baume AP+M", "la-roche-posay", "corps", "hydratants-corps", 79_900, 89_000, "400 ml", ["peau-seche", "peau-sensible"], "Baume relipidant triple action pour peaux très sèches, à tendance atopique.", { featured: true }],
    ["XeraCalm A.D Crème Relipidante", "avene", "corps", "hydratants-corps", 74_000, null, "400 ml", ["peau-seche"], "Apaise les démangeaisons et nourrit durablement."],
    ["Atoderm Intensive Baume", "bioderma", "corps", "hydratants-corps", 69_500, null, "500 ml", ["peau-seche"], "Anti-démangeaisons, ultra-apaisant, 24 h de confort."],
    ["Huile Prodigieuse", "nuxe", "corps", "hydratants-corps", 92_000, null, "100 ml", ["hydratation"], "L'huile sèche culte, multi-usages visage, corps et cheveux.", { featured: true }],
    ["Lotion Hydratante Corps", "cerave", "corps", "hydratants-corps", 49_900, null, "473 ml", ["peau-seche"], "Texture légère, céramides et acide hyaluronique, 24 h."],
    ["Bariéderm Cica-Crème", "uriage", "corps", "hydratants-corps", 32_000, null, "100 ml", ["peau-sensible"], "Répare, assainit et apaise les peaux abîmées."],
    ["Lipikar Syndet AP+", "la-roche-posay", "corps", "douche-bain", 44_900, null, "400 ml", ["peau-seche", "peau-sensible"], "Crème lavante relipidante anti-irritations."],
    ["Atoderm Huile de Douche", "bioderma", "corps", "douche-bain", 52_000, 58_000, "1 L", ["peau-seche"], "Huile ultra-nourrissante, mousse fine, sans savon."],
    ["Rêve de Miel Gel Douche Ultra-Riche", "nuxe", "corps", "douche-bain", 38_000, null, "400 ml", ["hydratation"], "Nettoie en douceur, parfum miel et fleurs délicat."],
    ["Crème Mains Cicaplast", "la-roche-posay", "corps", "mains-pieds", 22_900, null, "100 ml", ["peau-seche"], "Barrière réparatrice mains abîmées. Tenue jusqu'à 6 lavages."],
    ["Crème Mains Rêve de Miel", "nuxe", "corps", "mains-pieds", 24_500, null, "50 ml", ["peau-seche"], "Nourrit et répare les mains et ongles fragilisés."],
    ["Crème Pieds Réparatrice Urea 10%", "eucerin", "corps", "mains-pieds", 34_000, null, "100 ml", ["peau-seche"], "Hydratation intense pour pieds secs et calleux."],
    ["Huile Vergetures Bio", "mustela", "corps", "vergetures-fermete", 64_000, null, "105 ml", ["hydratation"], "Prévient l'apparition des vergetures, 99 % d'origine naturelle."],
    // Cheveux
    ["Shampooing à l'Avoine", "klorane", "cheveux", "shampooings", 29_900, null, "400 ml", ["peau-sensible"], "Ultra-doux, usage fréquent, toute la famille.", { featured: true }],
    ["Anaphase+ Shampooing", "ducray", "cheveux", "shampooings", 41_000, 45_500, "400 ml", ["chute-de-cheveux"], "Shampooing complément anti-chute, redonne force et volume."],
    ["Dercos Anti-Pelliculaire DS", "vichy", "cheveux", "shampooings", 44_900, null, "390 ml", ["pellicules"], "Élimine les pellicules et apaise le cuir chevelu."],
    ["Kelual DS Shampooing", "ducray", "cheveux", "shampooings", 39_000, null, "100 ml", ["pellicules"], "Traitant états pelliculaires sévères et démangeaisons."],
    ["Shampooing au Lait de Papyrus", "klorane", "cheveux", "shampooings", 31_500, null, "400 ml", ["hydratation"], "Nourrit et discipline les cheveux secs et ondulés."],
    ["Baume Après-Shampooing à la Mangue", "klorane", "cheveux", "apres-shampooings-masques", 34_900, null, "200 ml", ["hydratation"], "Nourrit et démêle les cheveux secs sans alourdir."],
    ["Masque Nutri-Réparateur", "nuxe", "cheveux", "apres-shampooings-masques", 58_000, 64_000, "125 ml", ["hydratation"], "Répare et sublime les cheveux abîmés, parfum floral."],
    ["Dercos Aminexil Clinical 5 Femme", "vichy", "cheveux", "anti-chute", 189_000, 210_000, "21 monodoses", ["chute-de-cheveux"], "Traitement anti-chute cliniquement prouvé en 6 semaines.", { featured: true }],
    ["Neoptide Expert Sérum", "ducray", "cheveux", "anti-chute", 165_000, null, "2 × 50 ml", ["chute-de-cheveux"], "Sérum densifiant anti-chute, résultats visibles en 3 mois."],
    ["Forcapil Cheveux & Ongles", "arkopharma", "cheveux", "anti-chute", 59_000, null, "180 gélules", ["chute-de-cheveux"], "Vitamines B, zinc et biotine pour des cheveux fortifiés."],
    ["Sensinol Shampooing Physioprotecteur", "ducray", "cheveux", "cuir-chevelu-sensible", 36_000, null, "200 ml", ["peau-sensible"], "Apaise immédiatement les démangeaisons du cuir chevelu."],
    // Solaire
    ["Anthelios UVMune 400 Fluide Invisible SPF50+", "la-roche-posay", "solaire", "protection-visage", 68_900, 76_000, "50 ml", ["protection-solaire", "taches"], "Protection ultra-large contre les UV ultra-longs. Fini invisible.", { featured: true }],
    ["Fotoprotector Fusion Water SPF50", "isdin", "solaire", "protection-visage", 74_000, null, "50 ml", ["protection-solaire"], "Texture ultra-légère, absorption immédiate, sans traces.", { isNew: true }],
    ["Photoderm Nude Touch SPF50+", "bioderma", "solaire", "protection-visage", 62_000, null, "40 ml", ["protection-solaire", "acne"], "Effet peau nue, matifiant, teinte universelle."],
    ["Capital Soleil UV-Age Daily SPF50+", "vichy", "solaire", "protection-visage", 66_500, null, "40 ml", ["protection-solaire", "anti-age"], "Fluide anti-photovieillissement, hydratant et léger."],
    ["Vinosun Crème Protectrice SPF50", "caudalie", "solaire", "protection-visage", 79_000, null, "50 ml", ["protection-solaire", "anti-age"], "Filtres résistants à l'eau, antioxydante, respectueuse des océans."],
    ["Anthelios Lait Hydratant SPF50+", "la-roche-posay", "solaire", "protection-corps", 82_000, 92_000, "250 ml", ["protection-solaire"], "Très haute protection corps, résistant à l'eau et au sable."],
    ["Fluide Minéral Corps SPF50+", "avene", "solaire", "protection-corps", 76_000, null, "100 ml", ["protection-solaire", "peau-sensible"], "100 % filtres minéraux pour peaux intolérantes."],
    ["Photoderm Spray SPF50+", "bioderma", "solaire", "protection-corps", 69_000, null, "200 ml", ["protection-solaire"], "Spray invisible, application facile, toute la famille."],
    ["Posthelios Gel-Crème Après-Soleil", "la-roche-posay", "solaire", "apres-soleil", 42_000, null, "200 ml", ["hydratation"], "Répare, apaise et prolonge le bronzage."],
    ["Lait Après-Soleil Réparateur", "avene", "solaire", "apres-soleil", 39_900, null, "200 ml", ["peau-sensible"], "Apaise immédiatement les peaux échauffées."],
    ["Anthelios Dermo-Pediatrics Lait SPF50+", "la-roche-posay", "solaire", "enfants", 84_000, null, "250 ml", ["protection-solaire"], "Très haute protection dès 3 ans, hypoallergénique."],
    ["Pediatrics Fusion Water SPF50", "isdin", "solaire", "enfants", 72_000, null, "50 ml", ["protection-solaire"], "Formule pédiatrique testée sous contrôle, sans picotements."],
    // Bébé
    ["Gel Lavant Doux", "mustela", "bebe-maman", "toilette-bebe", 31_900, 35_500, "500 ml", ["peau-sensible"], "Corps et cheveux, dès la naissance, 90 % d'origine naturelle.", { featured: true }],
    ["Eau Nettoyante Sans Rinçage", "mustela", "bebe-maman", "toilette-bebe", 28_500, null, "300 ml", ["peau-sensible"], "Nettoie et adoucit visage, corps et siège sans rinçage."],
    ["ABCDerm Moussant", "bioderma", "bebe-maman", "toilette-bebe", 33_000, null, "1 L", ["peau-sensible"], "Nettoyant ultra-doux corps et cheveux, sans savon."],
    ["Crème Change 1-2-3", "mustela", "bebe-maman", "change", 24_900, null, "100 ml", ["peau-sensible"], "Prévient, apaise et répare les rougeurs du siège."],
    ["Cicalfate+ Crème Réparatrice", "avene", "bebe-maman", "change", 27_000, null, "100 ml", ["peau-sensible"], "Répare et assainit les irritations. Toute la famille."],
    ["Baume Corps Maternité", "mustela", "bebe-maman", "soins-maman", 58_000, null, "200 ml", ["hydratation"], "Nourrit intensément, améliore élasticité et confort."],
    // Compléments
    ["Arkovital Pure Energy", "arkopharma", "complements", "vitalite-immunite", 38_000, null, "30 comprimés", ["immunite"], "Multivitamines 100 % d'origine végétale."],
    ["Vitamine D3 2000 UI", "arkopharma", "complements", "vitalite-immunite", 27_500, null, "60 capsules", ["immunite"], "Soutient l'immunité et le capital osseux."],
    ["Arkogélules Ginseng Bio", "arkopharma", "complements", "vitalite-immunite", 32_000, 36_000, "45 gélules", ["immunite"], "Tonus physique et intellectuel en période de fatigue."],
    ["Arkorelax Sommeil Fort 8h", "arkopharma", "complements", "sommeil-stress", 44_000, null, "15 comprimés", ["sommeil"], "Mélatonine à libération prolongée pour une nuit complète.", { isNew: true }],
    ["Arkogélules Magnésium Marin", "arkopharma", "complements", "sommeil-stress", 29_900, null, "60 gélules", ["sommeil", "immunite"], "Réduit la fatigue et soutient le système nerveux."],
    ["Skin Booster Collagène", "filorga", "complements", "beaute-in-out", 79_000, null, "30 sticks", ["anti-age"], "Collagène marin et acide hyaluronique pour une peau repulpée."],
    ["Arkogélules Charbon Végétal", "arkopharma", "complements", "digestion", 24_000, null, "45 gélules", ["immunite"], "Confort digestif et ventre plat."],
    // Hygiène
    ["Dentifrice Sensibilité", "eucerin", "hygiene", "bucco-dentaire", 14_900, null, "75 ml", ["peau-sensible"], "Protection des dents sensibles au quotidien."],
    ["Gyn-Phy Gel Intime", "uriage", "hygiene", "hygiene-intime", 26_000, null, "500 ml", ["peau-sensible"], "Toilette intime quotidienne, pH physiologique."],
    ["Déodorant 48h Anti-Traces", "vichy", "hygiene", "deodorants", 31_500, 34_900, "50 ml", ["peau-sensible"], "Anti-transpirant efficace, sans traces blanches."],
    ["Déodorant Roll-on Douceur", "avene", "hygiene", "deodorants", 27_900, null, "50 ml", ["peau-sensible"], "Sans sels d'aluminium, pour peaux sensibles."],
    ["Cicaplast Baume B5+", "la-roche-posay", "hygiene", "premiers-soins", 32_900, null, "100 ml", ["peau-sensible", "peau-seche"], "Baume réparateur apaisant multi-usages, toute la famille.", { featured: true }],
    ["Bariéderm Cica Spray", "uriage", "hygiene", "premiers-soins", 29_000, null, "100 ml", ["peau-sensible"], "Assainit et répare les zones abîmées, sans contact."],
  ];

  const imgFor: Record<string, string> = { visage: "/images/u-visage.jpg", corps: "/images/u-corps.jpg", cheveux: "/images/u-cheveux.jpg", solaire: "/images/u-solaire.jpg", "bebe-maman": "/images/u-bebe.jpg", complements: "/images/u-complements.jpg", hygiene: "/images/u-hygiene.jpg" };
  // Canonical per-product imagery lives in src/db/productImages.ts (auto-generated
  // by the image pipeline). Anything without an entry falls back to its universe
  // image and is reported by the audit as needing an image — never silently faked.
  const productIds: number[] = [];
  let n = 1;
  for (const [name, brand, universe, cat, price, compare, vol, ks, short, opts] of P) {
    const stock = opts?.stock ?? (n % 11 === 0 ? 0 : n % 7 === 0 ? 3 : 12 + (n * 7) % 40);
    const ratingCount = 4 + (n * 13) % 90;
    const ratingAvg = 400 + (n * 37) % 95;
    const [p] = await db.insert(products).values({
      slug: slug(`${brand}-${name}`), sku: `CL-${String(n).padStart(4, "0")}`, name, shortDescription: short,
      description: `${short} Formulé avec une exigence pharmaceutique, ce soin ${brand === "arkopharma" ? "complément" : "dermo-cosmétique"} s'intègre dans une routine simple et efficace. Sélectionné et conseillé par les pharmaciens Cléopâtre.`,
      ingredients: universe === "complements" ? "Actifs d'origine contrôlée, gélule végétale (HPMC), sans OGM, sans gluten." : "Aqua, Glycerin, Niacinamide, Sodium Hyaluronate, Panthenol, Ceramide NP, Tocopherol, Allantoin. Sans parabènes.",
      howToUse: universe === "complements" ? "1 à 2 gélules par jour au cours d'un repas avec un grand verre d'eau. Cure de 1 à 3 mois." : universe === "solaire" ? "Appliquer généreusement 15 minutes avant l'exposition. Renouveler toutes les 2 heures et après chaque baignade." : "Appliquer matin et/ou soir sur peau propre et sèche, en massant délicatement jusqu'à absorption.",
      brandId: B[brand], categoryId: C[cat], universeId: U[universe], priceMillimes: price, compareAtMillimes: compare, stock, lowStockThreshold: 5,
      image: PRODUCT_IMAGES[name]?.image ?? imgFor[universe], images: [PRODUCT_IMAGES[name]?.image ?? imgFor[universe]], volume: vol, status: "active", isFeatured: !!opts?.featured, isNew: !!opts?.isNew || n % 9 === 0,
      ratingAvg, ratingCount, salesCount: (n * 17) % 220,
    }).returning({ id: products.id });
    productIds.push(p.id);
    await db.insert(productConcerns).values(ks.map((k) => ({ productId: p.id, concernId: K[k] })));
    await db.insert(inventoryMovements).values({ productId: p.id, type: "in", quantity: stock, stockAfter: stock, reason: "Stock initial" });
    n++;
  }

  console.log("→ Promotions");
  await db.insert(promotions).values([
    { code: "BIENVENUE10", label: "-10 % sur votre première commande", type: "percent", value: 10, minSubtotalMillimes: 50_000, maxDiscountMillimes: 30_000, perUserLimit: 1 },
    { code: "SOLAIRE15", label: "-15 % sur l'univers Solaire", type: "percent", value: 15, minSubtotalMillimes: 0, universeId: U["solaire"], perUserLimit: 0 },
    { code: "LIVRAISON", label: "Livraison offerte", type: "free_shipping", value: 0, minSubtotalMillimes: 40_000, perUserLimit: 0 },
    { code: "CLEO20", label: "20 DT offerts dès 150 DT", type: "fixed", value: 20_000, minSubtotalMillimes: 150_000, perUserLimit: 2, usageLimit: 200 },
    { code: "ETE2024", label: "Offre expirée", type: "percent", value: 20, isActive: false, endsAt: new Date("2024-09-01") },
  ]);

  console.log("→ Stores");
  await db.insert(stores).values([
    { slug: "ezzahra", name: "Cléopâtre Ezzahra", address: "Avenue Habib Bourguiba, face à la municipalité", city: "Ezzahra", phone: "71450210", hours: "Lun–Sam 8h30–20h30 · Dim 9h–14h", mapsUrl: "https://maps.google.com/?q=Ezzahra+Tunisie" },
    { slug: "hammam-lif", name: "Cléopâtre Hammam-Lif", address: "Rue de la République, centre-ville", city: "Hammam-Lif", phone: "71290345", hours: "Lun–Sam 8h30–20h · Dim 9h–13h", mapsUrl: "https://maps.google.com/?q=Hammam-Lif+Tunisie" },
  ]);

  console.log("→ Orders");
  const addr = { fullName: "Ines Mansour", phone: "22345678", line1: "12 rue des Jasmins", city: "Ezzahra", governorate: "Ben Arous", postalCode: "2034" };
  const sample = [
    { number: "CL-240912-A1F3", status: "delivered" as const, days: 40, items: [[0, 1], [5, 1]] as [number, number][], promo: "BIENVENUE10" },
    { number: "CL-241003-B7C2", status: "shipped" as const, days: 3, items: [[26, 1], [39, 2]] as [number, number][], promo: null },
    { number: "CL-241010-D9E4", status: "pending" as const, days: 0, items: [[50, 1]] as [number, number][], promo: null },
  ];
  for (const s of sample) {
    const rows = await db.select().from(products).where(sql`id IN ${s.items.map(([i]) => productIds[i])}`);
    const lines = s.items.map(([i, q]) => { const p = rows.find((r) => r.id === productIds[i])!; return { p, q }; });
    const subtotal = lines.reduce((a, l) => a + l.p.priceMillimes * l.q, 0);
    const discount = s.promo ? Math.min(Math.floor(subtotal * 0.1), 30_000) : 0;
    const shipping = subtotal >= 99_000 ? 0 : 7_000;
    const created = new Date(Date.now() - s.days * 86_400_000);
    const [o] = await db.insert(orders).values({
      number: s.number, userId: customer.id, email: customer.email, phone: "22345678", status: s.status, paymentMethod: "cod",
      paymentStatus: s.status === "delivered" ? "paid" : "pending", shippingMethod: "standard", shippingAddress: addr,
      subtotalMillimes: subtotal, discountMillimes: discount, shippingMillimes: shipping, totalMillimes: subtotal - discount + shipping,
      promoCode: s.promo, createdAt: created, updatedAt: created, trackingCode: s.status === "shipped" ? "TN-4471-8820" : null,
    }).returning();
    await db.insert(orderItems).values(lines.map((l) => ({ orderId: o.id, productId: l.p.id, name: l.p.name, sku: l.p.sku, brandName: brandRows.find((b) => b.id === l.p.brandId)?.name, image: l.p.image, unitPriceMillimes: l.p.priceMillimes, quantity: l.q, lineTotalMillimes: l.p.priceMillimes * l.q })));
    const flow = ["pending", "confirmed", "preparing", "shipped", "delivered"] as const;
    const idx = flow.indexOf(s.status as (typeof flow)[number]);
    const msgs = ["Commande reçue", "Commande confirmée par notre équipe", "Préparation en cours en boutique", "Colis remis au transporteur", "Colis livré"];
    for (let i = 0; i <= idx; i++) {
      await db.insert(orderEvents).values({ orderId: o.id, status: flow[i], message: msgs[i], createdAt: new Date(created.getTime() + i * 6 * 3_600_000) });
    }
  }

  console.log("→ Reviews");
  const reviewTexts = [
    ["Texture parfaite", "Une texture légère qui pénètre vite. Ma peau est apaisée dès la première semaine.", 5],
    ["Efficace et doux", "Très bon rapport qualité-prix. Livraison rapide à Ezzahra, colis soigné.", 4],
    ["Je recommande", "Conseillé par la pharmacienne en boutique, je ne regrette pas. Résultat visible.", 5],
    ["Bien mais parfumé", "Efficace, mais j'aurais préféré une version sans parfum.", 3],
    ["Indispensable", "Je rachète à chaque fois. Le produit est authentique, date de péremption longue.", 5],
  ] as const;
  const names = ["Amira B.", "Yasmine K.", "Mehdi T.", "Salma R.", "Rim H.", "Khaled M."];
  let r = 0;
  for (const pid of productIds) {
    if (r % 2 === 0) {
      const [title, body, rating] = reviewTexts[r % reviewTexts.length];
      await db.insert(reviews).values({ productId: pid, authorName: names[r % names.length], rating, title, body, status: "approved", userId: r % 4 === 0 ? customer.id : null });
    }
    if (r % 9 === 0) {
      await db.insert(reviews).values({ productId: pid, authorName: names[(r + 2) % names.length], rating: 4, title: "En attente", body: "Très satisfaite de ce produit, l'emballage était impeccable.", status: "pending" });
    }
    r++;
  }

  console.log("→ Articles");
  await db.insert(articles).values([
    { slug: "routine-minimaliste-peau-sensible", title: "La routine minimaliste pour peau sensible", tag: "Visage", readMinutes: 5, image: "/images/u-visage.jpg", excerpt: "Trois gestes, pas un de plus. Comment simplifier pour apaiser durablement.", body: "Une peau sensible ne demande pas plus de produits, mais moins d'ingrédients.\n\nLe matin : un nettoyage à l'eau ou avec une eau micellaire douce, puis un hydratant sans parfum et un SPF 50+.\n\nLe soir : un nettoyant sans savon, puis le même hydratant. Une fois par semaine, un masque apaisant si besoin.\n\nÉvitez les gommages mécaniques, les huiles essentielles et l'alcool dénaturé. En cas de doute, demandez conseil à nos pharmaciens en boutique." },
    { slug: "choisir-sa-protection-solaire-en-tunisie", title: "Choisir sa protection solaire en Tunisie", tag: "Solaire", readMinutes: 6, image: "/images/u-solaire.jpg", excerpt: "Indice, texture, résistance à l'eau : le guide honnête pour un été serein.", body: "Sous nos latitudes, l'indice UV dépasse 9 de mai à septembre. Le SPF 50+ n'est pas un luxe.\n\nPour le visage, privilégiez un fluide invisible ou une texture teintée si vous avez des taches. Pour le corps, un lait ou un spray résistant à l'eau.\n\nLa quantité compte plus que la marque : deux doigts pour le visage, renouvelés toutes les deux heures.\n\nLes enfants ont besoin de formules pédiatriques, testées sur peaux fragiles, et d'ombre entre 12h et 16h." },
    { slug: "chute-de-cheveux-saisonniere", title: "Chute de cheveux saisonnière : agir sans paniquer", tag: "Cheveux", readMinutes: 4, image: "/images/u-cheveux.jpg", excerpt: "À l'automne, perdre jusqu'à 100 cheveux par jour est normal. Voici quand et comment agir.", body: "La chute saisonnière dure 4 à 6 semaines. Au-delà, ou si elle s'accompagne d'une fatigue inhabituelle, un bilan sanguin s'impose.\n\nUne cure de 3 mois associant un complément (biotine, zinc, fer si carence) et un sérum stimulant donne les meilleurs résultats.\n\nLavez vos cheveux avec un shampooing doux, sans frotter le cuir chevelu, et limitez la chaleur." },
    { slug: "vitamine-d-en-hiver", title: "Vitamine D : pourquoi en manquer même au soleil", tag: "Compléments", readMinutes: 3, image: "/images/u-complements.jpg", excerpt: "Paradoxe méditerranéen : ensoleillés mais carencés. Ce que disent les pharmaciens.", body: "Entre la protection solaire, les vêtements couvrants et la vie en intérieur, une majorité d'adultes présente un taux insuffisant en hiver.\n\nUne supplémentation quotidienne de 1000 à 2000 UI est simple, sûre et bien tolérée. Demandez conseil pour adapter la dose." },
  ]);

  console.log(`✓ Seed complete — ${productIds.length} products. Admin: admin@cleopatre.tn · Client: client@cleopatre.tn · Support: ${support.email}${IS_PROD_SEED ? " (passwords supplied via environment)" : " — demo passwords: Admin123! / Client123! / Support123!"}`);
  await pool.end();
}

main().catch(async (e) => { console.error(e); await pool.end(); process.exit(1); });
