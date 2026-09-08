import { ProductGridSkeleton } from "@/components/ui/primitives";
export default function Loading() {
  return (<div className="container-lux py-10 lg:py-14"><div className="skeleton h-3 w-32" /><div className="skeleton mt-6 h-12 w-72" /><div className="skeleton mt-4 h-4 w-96 max-w-full" /><div className="mt-12"><ProductGridSkeleton /></div></div>);
}
