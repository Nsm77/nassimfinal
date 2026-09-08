export const GOVERNORATES = [
  "Ariana","Béja","Ben Arous","Bizerte","Gabès","Gafsa","Jendouba","Kairouan","Kasserine","Kébili",
  "Le Kef","Mahdia","La Manouba","Médenine","Monastir","Nabeul","Sfax","Sidi Bouzid","Siliana","Sousse",
  "Tataouine","Tozeur","Tunis","Zaghouan",
] as const;
export type Governorate = (typeof GOVERNORATES)[number];

export const CITIES: Partial<Record<Governorate, string[]>> = {
  "Ben Arous": ["Ezzahra","Hammam-Lif","Radès","Mégrine","Ben Arous","Boumhel","Mornag","Hammam Chott","Fouchana","El Mourouj"],
  Tunis: ["Tunis Centre","La Marsa","Carthage","Le Bardo","El Menzah","Lac 1","Lac 2","Bab Bhar","Sidi Bou Saïd","Montfleury"],
  Ariana: ["Ariana Ville","Ennasr","Raoued","La Soukra","Mnihla","Borj Louzir"],
  "La Manouba": ["Manouba","Denden","Douar Hicher","Oued Ellil"],
  Nabeul: ["Nabeul","Hammamet","Korba","Kélibia","Grombalia","Soliman"],
  Sousse: ["Sousse","Hammam Sousse","Msaken","Kalâa Kebira","Akouda"],
  Sfax: ["Sfax Ville","Sakiet Ezzit","Sakiet Eddaïer","Thyna"],
  Monastir: ["Monastir","Moknine","Ksar Hellal","Jemmal"],
  Bizerte: ["Bizerte","Menzel Bourguiba","Mateur","Ras Jebel"],
};

export function deliveryEstimate(governorate?: string, method: "standard" | "express" | "pickup" = "standard") {
  if (method === "pickup") return "Retrait sous 2 h en boutique";
  const grandTunis = ["Tunis", "Ariana", "Ben Arous", "La Manouba"];
  if (method === "express") return "Livraison sous 24 h";
  return governorate && grandTunis.includes(governorate) ? "Livraison 24–48 h" : "Livraison 48–72 h";
}
