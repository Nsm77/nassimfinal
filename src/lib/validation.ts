import { z } from "zod";

const phone = z.string().trim().regex(/^(\+216)?[2-9]\d{7}$/, "Numéro tunisien invalide (8 chiffres)");
const email = z.string().trim().toLowerCase().email("Adresse e-mail invalide");
const password = z.string().min(8, "8 caractères minimum").max(128);

export const registerSchema = z.object({
  firstName: z.string().trim().min(2, "Prénom trop court").max(80),
  lastName: z.string().trim().min(2, "Nom trop court").max(80),
  email,
  phone: phone.optional().or(z.literal("")),
  password,
});
export const loginSchema = z.object({ email, password: z.string().min(1, "Mot de passe requis") });

export const profileSchema = z.object({
  firstName: z.string().trim().min(2).max(80),
  lastName: z.string().trim().min(2).max(80),
  phone: phone.optional().or(z.literal("")),
});
export const passwordChangeSchema = z.object({
  current: z.string().min(1, "Requis"),
  next: password,
});

export const addressSchema = z.object({
  fullName: z.string().trim().min(3, "Nom complet requis").max(160),
  phone,
  line1: z.string().trim().min(5, "Adresse trop courte").max(200),
  line2: z.string().trim().max(200).optional().or(z.literal("")),
  city: z.string().trim().min(2, "Ville requise").max(100),
  governorate: z.string().trim().min(2, "Gouvernorat requis").max(60),
  postalCode: z.string().trim().max(10).optional().or(z.literal("")),
});

export const cartLineSchema = z.object({ productId: z.number().int().positive(), quantity: z.number().int().min(1).max(20) });

export const checkoutSchema = z.object({
  email,
  address: addressSchema,
  shippingMethod: z.enum(["standard", "express", "pickup"]),
  storeId: z.number().int().positive().optional(),
  paymentMethod: z.enum(["cod", "bank_transfer", "card", "gift_card"]),
  promoCode: z.string().trim().max(40).optional().or(z.literal("")),
  giftWrap: z.boolean().default(false),
  giftMessage: z.string().trim().max(300).optional().or(z.literal("")),
  customerNote: z.string().trim().max(500).optional().or(z.literal("")),
  createAccount: z.boolean().default(false),
  accountPassword: z.string().max(128).optional().or(z.literal("")),
  idempotencyKey: z.string().min(8).max(64),
  lines: z.array(cartLineSchema).min(1, "Panier vide"),
});
export type CheckoutInput = z.infer<typeof checkoutSchema>;

export const reviewSchema = z.object({
  productId: z.number().int().positive(),
  rating: z.number().int().min(1).max(5),
  title: z.string().trim().max(160).optional().or(z.literal("")),
  body: z.string().trim().min(10, "10 caractères minimum").max(2000),
  authorName: z.string().trim().min(2).max(120),
});

export const productSchema = z.object({
  name: z.string().trim().min(2).max(200),
  slug: z.string().trim().min(2).max(160).regex(/^[a-z0-9-]+$/, "Slug invalide"),
  sku: z.string().trim().min(2).max(40),
  shortDescription: z.string().trim().max(300).optional().or(z.literal("")),
  description: z.string().trim().max(5000).optional().or(z.literal("")),
  ingredients: z.string().trim().max(3000).optional().or(z.literal("")),
  howToUse: z.string().trim().max(3000).optional().or(z.literal("")),
  brandId: z.number().int().positive().nullable(),
  categoryId: z.number().int().positive().nullable(),
  universeId: z.number().int().positive().nullable(),
  priceMillimes: z.number().int().min(0),
  compareAtMillimes: z.number().int().min(0).nullable(),
  stock: z.number().int().min(0),
  lowStockThreshold: z.number().int().min(0),
  volume: z.string().trim().max(40).optional().or(z.literal("")),
  image: z.string().trim().max(255).optional().or(z.literal("")),
  status: z.enum(["draft", "active", "archived"]),
  isFeatured: z.boolean(),
  isNew: z.boolean(),
  concernIds: z.array(z.number().int().positive()).default([]),
});

export const promotionSchema = z.object({
  code: z.string().trim().toUpperCase().min(3).max(40).regex(/^[A-Z0-9]+$/, "Lettres et chiffres uniquement"),
  label: z.string().trim().min(3).max(160),
  type: z.enum(["percent", "fixed", "free_shipping"]),
  value: z.number().int().min(0),
  minSubtotalMillimes: z.number().int().min(0),
  maxDiscountMillimes: z.number().int().min(0).nullable(),
  usageLimit: z.number().int().min(0).nullable(),
  perUserLimit: z.number().int().min(0),
  isActive: z.boolean(),
  endsAt: z.string().optional().or(z.literal("")),
});

export const stockAdjustSchema = z.object({
  productId: z.number().int().positive(),
  delta: z.number().int().refine((n) => n !== 0, "Quantité non nulle requise"),
  reason: z.string().trim().min(3, "Motif requis").max(200),
});

export const ticketSchema = z.object({
  name: z.string().trim().min(2).max(160),
  email,
  subject: z.string().trim().min(3).max(200),
  message: z.string().trim().min(10, "Message trop court").max(3000),
  orderNumber: z.string().trim().max(24).optional().or(z.literal("")),
});

export const newsletterSchema = z.object({ email });
export const orderStatusSchema = z.enum(["pending", "confirmed", "preparing", "shipped", "delivered", "cancelled", "returned"]);
// Server-action arguments are attacker-controlled regardless of their TS type,
// so enum-shaped inputs are validated before they reach the database.
export const userRoleSchema = z.enum(["customer", "support", "admin"]);
