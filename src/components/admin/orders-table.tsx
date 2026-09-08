"use client";
import Link from "next/link";
import { useState } from "react";
import { formatDT } from "@/lib/money";
import { formatDateTime } from "@/lib/utils";
import type { Order } from "@/db/schema";
import { StatusBadge, Table } from "./ui";
import { BulkBar } from "./order-controls";
export function OrdersTable({ rows }: { rows: Order[] }) {
  const [sel, setSel] = useState<number[]>([]);
  const toggle = (id: number) => setSel((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  return (<>
    <BulkBar ids={sel} onDone={() => setSel([])} />
    <Table head={["", "N°", "Client", "Téléphone", "Total", "Paiement", "Statut", "Date"]}>{rows.map((o) => <tr key={o.id} className="hover:bg-admin-panel"><td className="px-4 py-3"><input type="checkbox" checked={sel.includes(o.id)} onChange={() => toggle(o.id)} aria-label={`Sélectionner ${o.number}`} className="h-4 w-4 accent-champagne" /></td><td className="px-4 py-3"><Link href={`/admin/commandes/${o.id}`} className="font-mono text-xs hover:underline">{o.number}</Link></td><td className="px-4 py-3">{o.shippingAddress.fullName}<br /><span className="text-xs text-admin-muted">{o.shippingAddress.city}</span></td><td className="px-4 py-3 tabular-nums">{o.phone}</td><td className="px-4 py-3 tabular-nums">{formatDT(o.totalMillimes)}</td><td className="px-4 py-3 text-xs text-admin-muted">{o.paymentMethod} · {o.paymentStatus}</td><td className="px-4 py-3"><StatusBadge s={o.status} /></td><td className="px-4 py-3 text-xs text-admin-muted">{formatDateTime(o.createdAt)}</td></tr>)}</Table>
    {rows.length === 0 && <p className="p-6 text-center text-sm text-admin-muted">Aucune commande.</p>}
  </>);
}
