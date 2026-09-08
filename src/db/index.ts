import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "./schema";

const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) throw new Error("DATABASE_URL is required");

const globalForDb = globalThis as typeof globalThis & { __cleopatrePool?: Pool };

export const pool =
  globalForDb.__cleopatrePool ??
  new Pool({ connectionString: databaseUrl, max: 10 });

if (process.env.NODE_ENV !== "production") globalForDb.__cleopatrePool = pool;

export const db = drizzle(pool, { schema });
export type Db = typeof db;
export type Tx = Parameters<Parameters<Db["transaction"]>[0]>[0];
