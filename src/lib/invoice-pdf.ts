import "server-only";
import type { Order, OrderItem } from "@/db/schema";
import { PAYMENT_LABELS, SHIPPING_LABELS } from "./order-constants";

/* ────────────────────────────────────────────────────────────
   Zero-dependency server-side PDF writer (PDF 1.4, A4, Helvetica
   with WinAnsiEncoding so French accents render correctly).
   Produces a genuine PDF document — not an HTML rename.
   ──────────────────────────────────────────────────────────── */

/** Helvetica glyph widths (1/1000 em) for WinAnsi-relevant chars. */
const W: Record<number, number> = {
  32: 278, 33: 278, 34: 355, 35: 556, 36: 556, 37: 889, 38: 667, 39: 191, 40: 333, 41: 333, 42: 389, 43: 584, 44: 278, 45: 333, 46: 278, 47: 278,
  48: 556, 49: 556, 50: 556, 51: 556, 52: 556, 53: 556, 54: 556, 55: 556, 56: 556, 57: 556, 58: 278, 59: 278, 60: 584, 61: 584, 62: 584, 63: 556,
  64: 1015, 65: 667, 66: 667, 67: 722, 68: 722, 69: 667, 70: 611, 71: 778, 72: 722, 73: 278, 74: 500, 75: 667, 76: 556, 77: 833, 78: 722, 79: 778,
  80: 667, 81: 778, 82: 722, 83: 667, 84: 611, 85: 722, 86: 667, 87: 944, 88: 667, 89: 667, 90: 611, 91: 278, 92: 278, 93: 278, 94: 469, 95: 556,
  96: 333, 97: 556, 98: 556, 99: 500, 100: 556, 101: 556, 102: 278, 103: 556, 104: 556, 105: 222, 106: 222, 107: 500, 108: 222, 109: 833, 110: 556,
  111: 556, 112: 556, 113: 556, 114: 333, 115: 500, 116: 278, 117: 556, 118: 500, 119: 722, 120: 500, 121: 500, 122: 500, 123: 334, 124: 260, 125: 334, 126: 584,
  160: 278, 171: 556, 183: 333, 187: 556, 192: 667, 194: 667, 200: 667, 201: 667, 202: 667, 206: 278, 207: 278, 212: 778, 217: 722, 224: 556, 226: 556, 231: 500,
  232: 556, 233: 556, 234: 556, 238: 222, 244: 556, 249: 556, 251: 556, 140: 944, 156: 833, 145: 191, 146: 191, 147: 333, 148: 333, 150: 556, 151: 1000, 133: 889,
};

/** Map a JS string to WinAnsi bytes; unknown glyphs become "?". */
function winAnsi(s: string): Buffer {
  const out: number[] = [];
  for (const ch of s) {
    const c = ch.codePointAt(0)!;
    if (c < 128 || (c >= 160 && c < 256)) out.push(c);
    else if (c === 0x2019) out.push(146);
    else if (c === 0x2018) out.push(145);
    else if (c === 0x201c) out.push(147);
    else if (c === 0x201d) out.push(148);
    else if (c === 0x2013) out.push(150);
    else if (c === 0x2014) out.push(151);
    else if (c === 0x2026) out.push(133);
    else if (c === 0x0152) out.push(140);
    else if (c === 0x0153) out.push(156);
    else out.push(63);
  }
  return Buffer.from(out);
}

function textWidth(s: string, size: number): number {
  let w = 0;
  for (const ch of s) w += W[ch.codePointAt(0)!] ?? 556;
  return (w * size) / 1000;
}

function pdfEscape(b: Buffer): string {
  return b.toString("latin1").replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
}

type Op = string;
class Page {
  ops: Op[] = [];
  text(x: number, y: number, size: number, str: string, opts: { bold?: boolean; color?: [number, number, number]; align?: "left" | "right" | "center"; maxWidth?: number } = {}) {
    const [r, g, b] = opts.color ?? [0.13, 0.12, 0.11];
    let dx = x;
    if (opts.align === "right") dx = x - textWidth(str, size);
    if (opts.align === "center") dx = x - textWidth(str, size) / 2;
    this.ops.push(`${r} ${g} ${b} rg BT /${opts.bold ? "F2" : "F1"} ${size} Tf ${dx.toFixed(2)} ${y.toFixed(2)} Td (${pdfEscape(winAnsi(str))}) Tj ET`);
  }
  line(x1: number, y1: number, x2: number, y2: number, w = 0.6, color: [number, number, number] = [0.82, 0.79, 0.74]) {
    const [r, g, b] = color;
    this.ops.push(`${r} ${g} ${b} RG ${w} w ${x1} ${y1} m ${x2} ${y2} l S`);
  }
  rect(x: number, y: number, w: number, h: number, color: [number, number, number]) {
    const [r, g, b] = color;
    this.ops.push(`${r} ${g} ${b} rg ${x} ${y} ${w} ${h} re f`);
  }
  content(): string {
    return this.ops.join("\n");
  }
}

export function dt(millimes: number): string {
  const v = Math.round(millimes) / 1000;
  return v.toLocaleString("fr-FR", { minimumFractionDigits: 3, maximumFractionDigits: 3 }).replace(/\u202f/g, " ") + " DT";
}

function wrap(s: string, size: number, maxW: number): string[] {
  const words = s.split(/\s+/);
  const lines: string[] = [];
  let cur = "";
  for (const w of words) {
    const t = cur ? cur + " " + w : w;
    if (textWidth(t, size) <= maxW) cur = t;
    else {
      if (cur) lines.push(cur);
      cur = w;
    }
  }
  if (cur) lines.push(cur);
  return lines;
}

const PAGE_W = 595;
const PAGE_H = 842;
const M = 48; // margin
const INK: [number, number, number] = [0.13, 0.12, 0.11];
const MUTED: [number, number, number] = [0.45, 0.43, 0.4];
const GOLD: [number, number, number] = [0.72, 0.58, 0.34];
const LINE: [number, number, number] = [0.85, 0.82, 0.77];

export function buildInvoicePdf(o: Order & { items: OrderItem[] }): Buffer {
  const pages: Page[] = [];
  let page = new Page();
  pages.push(page);

  const footer = (p: Page) => {
    p.line(M, 36, PAGE_W - M, 36, 0.6, LINE);
    p.text(PAGE_W / 2, 26, 7.5, "Cléopâtre — Espace Santé Beauté · Tunis, Tunisie · 71 450 210", { align: "center", color: MUTED });
  };

  /* Header */
  page.rect(0, PAGE_H - 92, PAGE_W, 92, [0.97, 0.96, 0.94]);
  page.text(M, PAGE_H - 46, 21, "CLÉOPÂTRE", { bold: true, color: INK });
  page.text(M, PAGE_H - 62, 8, "ESPACE SANTÉ BEAUTÉ", { color: GOLD });
  page.text(PAGE_W - M, PAGE_H - 42, 13, "FACTURE", { bold: true, align: "right", color: INK });
  page.text(PAGE_W - M, PAGE_H - 58, 9, `N° ${o.number}`, { align: "right", color: INK });
  page.text(PAGE_W - M, PAGE_H - 71, 8.5, `Date : ${new Date(o.createdAt).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" })}`, { align: "right", color: MUTED });

  let y = PAGE_H - 122;

  /* Client + livraison */
  page.text(M, y, 8, "CLIENT", { bold: true, color: GOLD });
  page.text(M, y - 14, 10, o.shippingAddress.fullName, { bold: true, color: INK });
  page.text(M, y - 27, 8.5, o.email, { color: MUTED });
  page.text(M, y - 39, 8.5, `Tél. ${o.phone}`, { color: MUTED });

  page.text(320, y, 8, "LIVRAISON", { bold: true, color: GOLD });
  const addr = [o.shippingAddress.line1, o.shippingAddress.line2, `${o.shippingAddress.city} — ${o.shippingAddress.governorate}${o.shippingAddress.postalCode ? " (" + o.shippingAddress.postalCode + ")" : ""}`].filter(Boolean) as string[];
  addr.forEach((l, i) => page.text(320, y - 14 - i * 12, 8.5, l, { color: MUTED }));
  page.text(320, y - 14 - addr.length * 12, 8.5, SHIPPING_LABELS[o.shippingMethod], { color: INK });

  y -= 62;
  page.line(M, y, PAGE_W - M, y, 0.8, LINE);
  y -= 20;

  /* Table header */
  const colRef = 320, colQty = 396, colPu = 452, colTot = PAGE_W - M;
  page.rect(M, y - 14, PAGE_W - 2 * M, 18, [0.94, 0.92, 0.89]);
  page.text(M + 4, y - 3, 8, "PRODUIT", { bold: true, color: INK });
  page.text(colRef, y - 3, 8, "RÉF.", { bold: true, color: INK });
  page.text(colQty, y - 3, 8, "QTÉ", { bold: true, align: "right", color: INK });
  page.text(colPu, y - 3, 8, "PRIX UNIT.", { bold: true, align: "right", color: INK });
  page.text(colTot, y - 3, 8, "TOTAL", { bold: true, align: "right", color: INK });
  y -= 26;

  const newPageIfNeeded = (need: number) => {
    if (y - need > 60) return;
    footer(page);
    page = new Page();
    pages.push(page);
    y = PAGE_H - 60;
  };

  for (const it of o.items) {
    const nameLines = wrap(it.name, 8.5, colRef - M - 24);
    const rowH = Math.max(nameLines.length * 11, 14);
    newPageIfNeeded(rowH + 8);
    nameLines.forEach((l, i) => page.text(M + 4, y - i * 11, 8.5, l, { color: INK }));
    page.text(colRef, y, 7.5, (it.sku ?? "—").slice(0, 16), { color: MUTED });
    page.text(colQty, y, 8.5, String(it.quantity), { align: "right", color: INK });
    page.text(colPu, y, 8.5, dt(it.unitPriceMillimes), { align: "right", color: INK });
    page.text(colTot, y, 8.5, dt(it.lineTotalMillimes), { align: "right", bold: true, color: INK });
    y -= rowH + 6;
    page.line(M, y + 2, PAGE_W - M, y + 2, 0.4, [0.9, 0.88, 0.84]);
    y -= 6;
  }

  /* Totals */
  y -= 6;
  newPageIfNeeded(96);
  const tx = 356;
  const row = (label: string, val: string, strong = false, neg = false) => {
    page.text(tx, y, strong ? 10 : 8.5, label, { bold: strong, color: strong ? INK : MUTED });
    page.text(PAGE_W - M, y, strong ? 10 : 8.5, (neg ? "−" : "") + val, { align: "right", bold: strong, color: strong ? INK : neg ? [0.2, 0.45, 0.3] : INK });
    y -= strong ? 16 : 13;
  };
  row("Sous-total", dt(o.subtotalMillimes));
  if (o.discountMillimes > 0) row(`Remise${o.promoCode ? ` (${o.promoCode})` : ""}`, dt(o.discountMillimes), false, true);
  row("Livraison", o.shippingMillimes ? dt(o.shippingMillimes) : "Offerte");
  if (o.giftWrapMillimes > 0) row("Emballage cadeau", dt(o.giftWrapMillimes));
  page.line(tx - 8, y + 6, PAGE_W - M, y + 6, 0.8, LINE);
  y -= 6;
  row("TOTAL TTC", dt(o.totalMillimes), true);

  y -= 10;
  page.text(M, y, 8, "MODE DE PAIEMENT", { bold: true, color: GOLD });
  page.text(M, y - 13, 9, PAYMENT_LABELS[o.paymentMethod], { color: INK });
  page.text(M, y - 26, 8, "Document généré automatiquement à la confirmation de commande — ne pas utiliser comme preuve de paiement.", { color: MUTED });

  footer(page);

  /* ── Assemble ── */
  const objs: string[] = [];
  const pageObjNums: number[] = [];
  // obj 1 catalog, 2 pages, 3 F1, 4 F2; then per page: page obj + content obj
  const fontF1 = 3, fontF2 = 4;
  let n = 5;
  const pageObjs: string[] = [];
  const contentObjs: string[] = [];
  for (const p of pages) {
    const contentNum = n + 1;
    pageObjNums.push(n);
    pageObjs.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PAGE_W} ${PAGE_H}] /Resources << /Font << /F1 ${fontF1} 0 R /F2 ${fontF2} 0 R >> >> /Contents ${contentNum} 0 R >>`);
    const stream = p.content();
    contentObjs.push(`<< /Length ${Buffer.byteLength(stream, "latin1")} >>\nstream\n${stream}\nendstream`);
    n += 2;
  }
  objs[1] = `<< /Type /Catalog /Pages 2 0 R >>`;
  objs[2] = `<< /Type /Pages /Kids [${pageObjNums.map((x) => `${x} 0 R`).join(" ")}] /Count ${pages.length} >>`;
  objs[3] = `<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>`;
  objs[4] = `<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>`;
  pageObjNums.forEach((num, i) => {
    objs[num] = pageObjs[i];
    objs[num + 1] = contentObjs[i];
  });

  let out = "%PDF-1.4\n";
  const offsets: number[] = [];
  for (let i = 1; i < n; i++) {
    offsets[i] = Buffer.byteLength(out, "latin1");
    out += `${i} 0 obj\n${objs[i]}\nendobj\n`;
  }
  const xrefPos = Buffer.byteLength(out, "latin1");
  out += `xref\n0 ${n}\n0000000000 65535 f \n`;
  for (let i = 1; i < n; i++) out += `${String(offsets[i]).padStart(10, "0")} 00000 n \n`;
  out += `trailer\n<< /Size ${n} /Root 1 0 R >>\nstartxref\n${xrefPos}\n%%EOF`;
  return Buffer.from(out, "latin1");
}
