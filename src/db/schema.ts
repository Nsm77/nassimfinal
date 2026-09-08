import { relations, sql } from "drizzle-orm";
import {
  boolean,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  primaryKey,
  serial,
  text,
  timestamp,
  uniqueIndex,
  varchar,
} from "drizzle-orm/pg-core";

/* ── Enums ─────────────────────────────────────────────── */
export const userRoleEnum = pgEnum("user_role", ["customer", "support", "admin"]);
export const productStatusEnum = pgEnum("product_status", ["draft", "active", "archived"]);
export const orderStatusEnum = pgEnum("order_status", [
  "pending",
  "confirmed",
  "preparing",
  "shipped",
  "delivered",
  "cancelled",
  "returned",
]);
export const paymentMethodEnum = pgEnum("payment_method", ["cod", "bank_transfer", "card", "gift_card"]);
export const paymentStatusEnum = pgEnum("payment_status", ["pending", "paid", "refunded", "failed"]);
export const shippingMethodEnum = pgEnum("shipping_method", ["standard", "express", "pickup"]);
export const promoTypeEnum = pgEnum("promo_type", ["percent", "fixed", "free_shipping"]);
export const reviewStatusEnum = pgEnum("review_status", ["pending", "approved", "rejected"]);
export const movementTypeEnum = pgEnum("movement_type", ["in", "out", "adjust", "sale", "restock", "return"]);
export const ticketStatusEnum = pgEnum("ticket_status", ["open", "answered", "closed"]);

const timestamps = {
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
};

/* ── Users & auth ──────────────────────────────────────── */
export const users = pgTable(
  "users",
  {
    id: serial("id").primaryKey(),
    email: varchar("email", { length: 255 }).notNull(),
    passwordHash: text("password_hash").notNull(),
    firstName: varchar("first_name", { length: 80 }).notNull(),
    lastName: varchar("last_name", { length: 80 }).notNull(),
    phone: varchar("phone", { length: 20 }),
    role: userRoleEnum("role").default("customer").notNull(),
    loyaltyPoints: integer("loyalty_points").default(0).notNull(),
    notes: text("notes"),
    ...timestamps,
  },
  (t) => [uniqueIndex("users_email_idx").on(t.email), index("users_role_idx").on(t.role)],
);

export const sessions = pgTable(
  "sessions",
  {
    id: varchar("id", { length: 64 }).primaryKey(),
    userId: integer("user_id")
      .references(() => users.id, { onDelete: "cascade" })
      .notNull(),
    expiresAt: timestamp("expires_at", { withTimezone: true }).notNull(),
    userAgent: text("user_agent"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("sessions_user_idx").on(t.userId), index("sessions_expires_idx").on(t.expiresAt)],
);

export const addresses = pgTable(
  "addresses",
  {
    id: serial("id").primaryKey(),
    userId: integer("user_id")
      .references(() => users.id, { onDelete: "cascade" })
      .notNull(),
    label: varchar("label", { length: 60 }).default("Domicile").notNull(),
    fullName: varchar("full_name", { length: 160 }).notNull(),
    phone: varchar("phone", { length: 20 }).notNull(),
    line1: varchar("line1", { length: 200 }).notNull(),
    line2: varchar("line2", { length: 200 }),
    city: varchar("city", { length: 100 }).notNull(),
    governorate: varchar("governorate", { length: 60 }).notNull(),
    postalCode: varchar("postal_code", { length: 10 }),
    isDefault: boolean("is_default").default(false).notNull(),
    ...timestamps,
  },
  (t) => [
    index("addresses_user_idx").on(t.userId),
    /*
     * Enforce "one default address per customer" in the database, not just in
     * application code — the clear-then-set sequence cannot leave two defaults
     * even if a writer crashes or bypasses the action.
     */
    uniqueIndex("addresses_one_default_idx").on(t.userId).where(sql`${t.isDefault}`),
  ],
);

/* ── Catalog ───────────────────────────────────────────── */
export const brands = pgTable(
  "brands",
  {
    id: serial("id").primaryKey(),
    slug: varchar("slug", { length: 120 }).notNull(),
    name: varchar("name", { length: 120 }).notNull(),
    country: varchar("country", { length: 60 }),
    story: text("story"),
    isFeatured: boolean("is_featured").default(false).notNull(),
    ...timestamps,
  },
  (t) => [uniqueIndex("brands_slug_idx").on(t.slug)],
);

export const categories = pgTable(
  "categories",
  {
    id: serial("id").primaryKey(),
    slug: varchar("slug", { length: 120 }).notNull(),
    name: varchar("name", { length: 120 }).notNull(),
    description: text("description"),
    story: text("story"),
    image: varchar("image", { length: 255 }),
    isUniverse: boolean("is_universe").default(false).notNull(),
    parentId: integer("parent_id"),
    sortOrder: integer("sort_order").default(0).notNull(),
    ...timestamps,
  },
  (t) => [
    uniqueIndex("categories_slug_idx").on(t.slug),
    index("categories_parent_idx").on(t.parentId),
    index("categories_universe_idx").on(t.isUniverse),
  ],
);

export const concerns = pgTable(
  "concerns",
  {
    id: serial("id").primaryKey(),
    slug: varchar("slug", { length: 120 }).notNull(),
    name: varchar("name", { length: 120 }).notNull(),
    intro: text("intro"),
    ...timestamps,
  },
  (t) => [uniqueIndex("concerns_slug_idx").on(t.slug)],
);

export const products = pgTable(
  "products",
  {
    id: serial("id").primaryKey(),
    slug: varchar("slug", { length: 160 }).notNull(),
    sku: varchar("sku", { length: 40 }).notNull(),
    name: varchar("name", { length: 200 }).notNull(),
    shortDescription: varchar("short_description", { length: 300 }),
    description: text("description"),
    ingredients: text("ingredients"),
    howToUse: text("how_to_use"),
    brandId: integer("brand_id").references(() => brands.id, { onDelete: "set null" }),
    categoryId: integer("category_id").references(() => categories.id, { onDelete: "set null" }),
    universeId: integer("universe_id").references(() => categories.id, { onDelete: "set null" }),
    priceMillimes: integer("price_millimes").notNull(),
    compareAtMillimes: integer("compare_at_millimes"),
    stock: integer("stock").default(0).notNull(),
    lowStockThreshold: integer("low_stock_threshold").default(5).notNull(),
    image: varchar("image", { length: 255 }),
    images: jsonb("images").$type<string[]>().default([]).notNull(),
    volume: varchar("volume", { length: 40 }),
    status: productStatusEnum("status").default("active").notNull(),
    isFeatured: boolean("is_featured").default(false).notNull(),
    isNew: boolean("is_new").default(false).notNull(),
    ratingAvg: integer("rating_avg").default(0).notNull(), // x100 (e.g. 460 = 4.6)
    ratingCount: integer("rating_count").default(0).notNull(),
    salesCount: integer("sales_count").default(0).notNull(),
    ...timestamps,
  },
  (t) => [
    uniqueIndex("products_slug_idx").on(t.slug),
    uniqueIndex("products_sku_idx").on(t.sku),
    index("products_brand_idx").on(t.brandId),
    index("products_category_idx").on(t.categoryId),
    index("products_universe_idx").on(t.universeId),
    index("products_status_idx").on(t.status),
    index("products_price_idx").on(t.priceMillimes),
    index("products_featured_idx").on(t.isFeatured),
  ],
);

export const productConcerns = pgTable(
  "product_concerns",
  {
    productId: integer("product_id")
      .references(() => products.id, { onDelete: "cascade" })
      .notNull(),
    concernId: integer("concern_id")
      .references(() => concerns.id, { onDelete: "cascade" })
      .notNull(),
  },
  (t) => [primaryKey({ columns: [t.productId, t.concernId] }), index("pc_concern_idx").on(t.concernId)],
);

export const reviews = pgTable(
  "reviews",
  {
    id: serial("id").primaryKey(),
    productId: integer("product_id")
      .references(() => products.id, { onDelete: "cascade" })
      .notNull(),
    userId: integer("user_id").references(() => users.id, { onDelete: "set null" }),
    authorName: varchar("author_name", { length: 120 }).notNull(),
    rating: integer("rating").notNull(),
    title: varchar("title", { length: 160 }),
    body: text("body").notNull(),
    status: reviewStatusEnum("status").default("pending").notNull(),
    reply: text("reply"),
    ...timestamps,
  },
  (t) => [index("reviews_product_idx").on(t.productId), index("reviews_status_idx").on(t.status)],
);

export const inventoryMovements = pgTable(
  "inventory_movements",
  {
    id: serial("id").primaryKey(),
    productId: integer("product_id")
      .references(() => products.id, { onDelete: "cascade" })
      .notNull(),
    type: movementTypeEnum("type").notNull(),
    quantity: integer("quantity").notNull(),
    stockAfter: integer("stock_after").notNull(),
    reason: varchar("reason", { length: 200 }),
    orderId: integer("order_id"),
    userId: integer("user_id"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("inv_product_idx").on(t.productId), index("inv_created_idx").on(t.createdAt)],
);

export const promotions = pgTable(
  "promotions",
  {
    id: serial("id").primaryKey(),
    code: varchar("code", { length: 40 }).notNull(),
    label: varchar("label", { length: 160 }).notNull(),
    type: promoTypeEnum("type").notNull(),
    value: integer("value").default(0).notNull(), // percent or millimes
    minSubtotalMillimes: integer("min_subtotal_millimes").default(0).notNull(),
    maxDiscountMillimes: integer("max_discount_millimes"),
    universeId: integer("universe_id").references(() => categories.id, { onDelete: "set null" }),
    usageLimit: integer("usage_limit"),
    usageCount: integer("usage_count").default(0).notNull(),
    perUserLimit: integer("per_user_limit").default(1).notNull(),
    startsAt: timestamp("starts_at", { withTimezone: true }),
    endsAt: timestamp("ends_at", { withTimezone: true }),
    isActive: boolean("is_active").default(true).notNull(),
    ...timestamps,
  },
  (t) => [uniqueIndex("promotions_code_idx").on(t.code), index("promotions_active_idx").on(t.isActive)],
);

/* ── Orders ────────────────────────────────────────────── */
export const orders = pgTable(
  "orders",
  {
    id: serial("id").primaryKey(),
    number: varchar("number", { length: 24 }).notNull(),
    idempotencyKey: varchar("idempotency_key", { length: 64 }),
    /**
     * Bearer token authorising guest access to this order (confirmation / tracking).
     * The public order `number` is NOT a credential: it is short, printable and
     * appears in e-mails, so knowing it must never reveal the order.
     * NULL on orders created before this column existed — those remain reachable
     * through /suivi with number + verified e-mail (the legacy path).
     */
    accessKey: varchar("access_key", { length: 64 }),
    userId: integer("user_id").references(() => users.id, { onDelete: "set null" }),
    email: varchar("email", { length: 255 }).notNull(),
    phone: varchar("phone", { length: 20 }).notNull(),
    status: orderStatusEnum("status").default("pending").notNull(),
    paymentMethod: paymentMethodEnum("payment_method").notNull(),
    paymentStatus: paymentStatusEnum("payment_status").default("pending").notNull(),
    shippingMethod: shippingMethodEnum("shipping_method").notNull(),
    shippingAddress: jsonb("shipping_address")
      .$type<{
        fullName: string;
        phone: string;
        line1: string;
        line2?: string;
        city: string;
        governorate: string;
        postalCode?: string;
      }>()
      .notNull(),
    storeId: integer("store_id"),
    subtotalMillimes: integer("subtotal_millimes").notNull(),
    discountMillimes: integer("discount_millimes").default(0).notNull(),
    shippingMillimes: integer("shipping_millimes").default(0).notNull(),
    giftWrapMillimes: integer("gift_wrap_millimes").default(0).notNull(),
    totalMillimes: integer("total_millimes").notNull(),
    promoCode: varchar("promo_code", { length: 40 }),
    giftWrap: boolean("gift_wrap").default(false).notNull(),
    giftMessage: varchar("gift_message", { length: 300 }),
    customerNote: text("customer_note"),
    internalNote: text("internal_note"),
    trackingCode: varchar("tracking_code", { length: 80 }),
    ...timestamps,
  },
  (t) => [
    uniqueIndex("orders_number_idx").on(t.number),
    uniqueIndex("orders_idem_idx").on(t.idempotencyKey),
    uniqueIndex("orders_access_key_idx").on(t.accessKey),
    index("orders_user_idx").on(t.userId),
    index("orders_status_idx").on(t.status),
    index("orders_created_idx").on(t.createdAt),
    index("orders_email_idx").on(t.email),
  ],
);

export const orderItems = pgTable(
  "order_items",
  {
    id: serial("id").primaryKey(),
    orderId: integer("order_id")
      .references(() => orders.id, { onDelete: "cascade" })
      .notNull(),
    productId: integer("product_id").references(() => products.id, { onDelete: "set null" }),
    // snapshot
    name: varchar("name", { length: 200 }).notNull(),
    sku: varchar("sku", { length: 40 }).notNull(),
    brandName: varchar("brand_name", { length: 120 }),
    image: varchar("image", { length: 255 }),
    unitPriceMillimes: integer("unit_price_millimes").notNull(),
    quantity: integer("quantity").notNull(),
    lineTotalMillimes: integer("line_total_millimes").notNull(),
  },
  (t) => [index("order_items_order_idx").on(t.orderId), index("order_items_product_idx").on(t.productId)],
);

export const orderEvents = pgTable(
  "order_events",
  {
    id: serial("id").primaryKey(),
    orderId: integer("order_id")
      .references(() => orders.id, { onDelete: "cascade" })
      .notNull(),
    status: orderStatusEnum("status").notNull(),
    message: varchar("message", { length: 300 }),
    actorId: integer("actor_id"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("order_events_order_idx").on(t.orderId)],
);

export const wishlistItems = pgTable(
  "wishlist_items",
  {
    userId: integer("user_id")
      .references(() => users.id, { onDelete: "cascade" })
      .notNull(),
    productId: integer("product_id")
      .references(() => products.id, { onDelete: "cascade" })
      .notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [primaryKey({ columns: [t.userId, t.productId] })],
);

/* ── Content ───────────────────────────────────────────── */
export const articles = pgTable(
  "articles",
  {
    id: serial("id").primaryKey(),
    slug: varchar("slug", { length: 160 }).notNull(),
    title: varchar("title", { length: 200 }).notNull(),
    excerpt: varchar("excerpt", { length: 400 }),
    body: text("body").notNull(),
    image: varchar("image", { length: 255 }),
    tag: varchar("tag", { length: 60 }),
    readMinutes: integer("read_minutes").default(4).notNull(),
    isPublished: boolean("is_published").default(true).notNull(),
    publishedAt: timestamp("published_at", { withTimezone: true }).defaultNow().notNull(),
    ...timestamps,
  },
  (t) => [uniqueIndex("articles_slug_idx").on(t.slug), index("articles_published_idx").on(t.isPublished)],
);

export const stores = pgTable("stores", {
  id: serial("id").primaryKey(),
  slug: varchar("slug", { length: 80 }).notNull().unique(),
  name: varchar("name", { length: 120 }).notNull(),
  address: varchar("address", { length: 240 }).notNull(),
  city: varchar("city", { length: 80 }).notNull(),
  phone: varchar("phone", { length: 20 }).notNull(),
  hours: varchar("hours", { length: 160 }).notNull(),
  mapsUrl: varchar("maps_url", { length: 300 }),
  isActive: boolean("is_active").default(true).notNull(),
  ...timestamps,
});

/* ── Telemetry & ops ───────────────────────────────────── */
export const searchEvents = pgTable(
  "search_events",
  {
    id: serial("id").primaryKey(),
    query: varchar("query", { length: 200 }).notNull(),
    resultsCount: integer("results_count").notNull(),
    userId: integer("user_id"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("search_query_idx").on(t.query), index("search_created_idx").on(t.createdAt)],
);

export const analyticsEvents = pgTable(
  "analytics_events",
  {
    id: serial("id").primaryKey(),
    name: varchar("name", { length: 80 }).notNull(),
    payload: jsonb("payload").$type<Record<string, unknown>>().default({}).notNull(),
    userId: integer("user_id"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("analytics_name_idx").on(t.name), index("analytics_created_idx").on(t.createdAt)],
);

export const auditLogs = pgTable(
  "audit_logs",
  {
    id: serial("id").primaryKey(),
    actorId: integer("actor_id"),
    action: varchar("action", { length: 80 }).notNull(),
    entity: varchar("entity", { length: 60 }).notNull(),
    entityId: varchar("entity_id", { length: 60 }),
    details: jsonb("details").$type<Record<string, unknown>>().default({}).notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("audit_entity_idx").on(t.entity, t.entityId), index("audit_created_idx").on(t.createdAt)],
);

export const supportTickets = pgTable(
  "support_tickets",
  {
    id: serial("id").primaryKey(),
    userId: integer("user_id").references(() => users.id, { onDelete: "set null" }),
    email: varchar("email", { length: 255 }).notNull(),
    name: varchar("name", { length: 160 }).notNull(),
    subject: varchar("subject", { length: 200 }).notNull(),
    message: text("message").notNull(),
    reply: text("reply"),
    status: ticketStatusEnum("status").default("open").notNull(),
    orderNumber: varchar("order_number", { length: 24 }),
    ...timestamps,
  },
  (t) => [index("tickets_status_idx").on(t.status)],
);

export const loyaltyTransactions = pgTable(
  "loyalty_transactions",
  {
    id: serial("id").primaryKey(),
    userId: integer("user_id")
      .references(() => users.id, { onDelete: "cascade" })
      .notNull(),
    points: integer("points").notNull(),
    reason: varchar("reason", { length: 160 }).notNull(),
    orderId: integer("order_id"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [
    index("loyalty_user_idx").on(t.userId),
    index("loyalty_order_idx").on(t.orderId),
    /*
     * Database-level idempotency for loyalty accounting:
     * at most one award (points > 0) and at most one reversal (points < 0)
     * per order, so a retried or duplicated status transition can never
     * grant or claw back points twice.
     */
    uniqueIndex("loyalty_order_award_idx").on(t.orderId).where(sql`${t.points} > 0`),
    uniqueIndex("loyalty_order_reversal_idx").on(t.orderId).where(sql`${t.points} < 0`),
  ],
);

export const newsletterSubscribers = pgTable("newsletter_subscribers", {
  id: serial("id").primaryKey(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

/**
 * Shared rate-limit counters.
 * Backed by PostgreSQL so limits hold across multiple app instances and
 * restarts; the in-memory limiter in `lib/rate-limit.ts` is only a fallback
 * for when the database is unreachable (e.g. local tooling).
 */
export const rateLimits = pgTable(
  "rate_limits",
  {
    key: varchar("key", { length: 190 }).primaryKey(),
    count: integer("count").default(0).notNull(),
    resetAt: timestamp("reset_at", { withTimezone: true }).notNull(),
  },
  (t) => [index("rate_limits_reset_idx").on(t.resetAt)],
);

/* ── Relations ─────────────────────────────────────────── */
export const usersRelations = relations(users, ({ many }) => ({
  addresses: many(addresses),
  orders: many(orders),
  reviews: many(reviews),
  wishlist: many(wishlistItems),
}));

export const brandsRelations = relations(brands, ({ many }) => ({ products: many(products) }));

export const categoriesRelations = relations(categories, ({ one, many }) => ({
  parent: one(categories, { fields: [categories.parentId], references: [categories.id], relationName: "tree" }),
  children: many(categories, { relationName: "tree" }),
  products: many(products, { relationName: "category" }),
}));

export const productsRelations = relations(products, ({ one, many }) => ({
  brand: one(brands, { fields: [products.brandId], references: [brands.id] }),
  category: one(categories, { fields: [products.categoryId], references: [categories.id], relationName: "category" }),
  universe: one(categories, { fields: [products.universeId], references: [categories.id], relationName: "universe" }),
  concerns: many(productConcerns),
  reviews: many(reviews),
}));

export const productConcernsRelations = relations(productConcerns, ({ one }) => ({
  product: one(products, { fields: [productConcerns.productId], references: [products.id] }),
  concern: one(concerns, { fields: [productConcerns.concernId], references: [concerns.id] }),
}));

export const ordersRelations = relations(orders, ({ one, many }) => ({
  user: one(users, { fields: [orders.userId], references: [users.id] }),
  items: many(orderItems),
  events: many(orderEvents),
}));

export const orderItemsRelations = relations(orderItems, ({ one }) => ({
  order: one(orders, { fields: [orderItems.orderId], references: [orders.id] }),
  product: one(products, { fields: [orderItems.productId], references: [products.id] }),
}));

export const orderEventsRelations = relations(orderEvents, ({ one }) => ({
  order: one(orders, { fields: [orderEvents.orderId], references: [orders.id] }),
}));

export const reviewsRelations = relations(reviews, ({ one }) => ({
  product: one(products, { fields: [reviews.productId], references: [products.id] }),
  user: one(users, { fields: [reviews.userId], references: [users.id] }),
}));

/* ── Types ─────────────────────────────────────────────── */
export type User = typeof users.$inferSelect;
export type Product = typeof products.$inferSelect;
export type Brand = typeof brands.$inferSelect;
export type Category = typeof categories.$inferSelect;
export type Concern = typeof concerns.$inferSelect;
export type Order = typeof orders.$inferSelect;
export type OrderItem = typeof orderItems.$inferSelect;
export type OrderEvent = typeof orderEvents.$inferSelect;
export type Promotion = typeof promotions.$inferSelect;
export type Review = typeof reviews.$inferSelect;
export type Article = typeof articles.$inferSelect;
export type Store = typeof stores.$inferSelect;
export type Address = typeof addresses.$inferSelect;
export type OrderStatus = (typeof orderStatusEnum.enumValues)[number];
