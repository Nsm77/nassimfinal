import type { SVGProps } from "react";

export type IconProps = SVGProps<SVGSVGElement> & { size?: number; title?: string; strokeWidth?: number };

function Base({ size = 20, title, children, strokeWidth = 1.5, ...rest }: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={title ? undefined : true}
      role={title ? "img" : undefined}
      focusable="false"
      {...rest}
    >
      {title ? <title>{title}</title> : null}
      {children}
    </svg>
  );
}

export const SearchIcon = (p: IconProps) => (
  <Base {...p}><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></Base>
);
export const CartIcon = (p: IconProps) => (
  <Base {...p}><path d="M5 7h15l-1.5 9h-12z" /><path d="M5 7 4 3H2" /><circle cx="9" cy="20" r="1" /><circle cx="17" cy="20" r="1" /></Base>
);
export const BagIcon = (p: IconProps) => (
  <Base {...p}><path d="M5 8h14l-1 12H6z" /><path d="M9 8V6a3 3 0 0 1 6 0v2" /></Base>
);
export const HeartIcon = (p: IconProps & { filled?: boolean }) => {
  const { filled, ...rest } = p;
  return (
    <Base {...rest} fill={filled ? "currentColor" : "none"}>
      <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" />
    </Base>
  );
};
export const UserIcon = (p: IconProps) => (
  <Base {...p}><circle cx="12" cy="8" r="4" /><path d="M4 20c0-3.3 3.6-5 8-5s8 1.7 8 5" /></Base>
);
export const MenuIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 7h16M4 12h16M4 17h16" /></Base>
);
export const CloseIcon = (p: IconProps) => (
  <Base {...p}><path d="m6 6 12 12M18 6 6 18" /></Base>
);
export const ChevronDownIcon = (p: IconProps) => (
  <Base {...p}><path d="m6 9 6 6 6-6" /></Base>
);
export const ChevronRightIcon = (p: IconProps) => (
  <Base {...p}><path d="m9 6 6 6-6 6" /></Base>
);
export const ChevronLeftIcon = (p: IconProps) => (
  <Base {...p}><path d="m15 6-6 6 6 6" /></Base>
);
export const ArrowRightIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 12h16M14 6l6 6-6 6" /></Base>
);
export const ArrowLeftIcon = (p: IconProps) => (
  <Base {...p}><path d="M20 12H4M10 6l-6 6 6 6" /></Base>
);
export const StarIcon = (p: IconProps & { filled?: boolean }) => {
  const { filled, ...rest } = p;
  return (
    <Base {...rest} fill={filled ? "currentColor" : "none"}>
      <path d="m12 3 2.7 5.7 6.3.8-4.6 4.3 1.2 6.2L12 17l-5.6 3 1.2-6.2L3 9.5l6.3-.8z" />
    </Base>
  );
};
export const CheckIcon = (p: IconProps) => (
  <Base {...p}><path d="m5 12 5 5L20 7" /></Base>
);
export const PlusIcon = (p: IconProps) => (
  <Base {...p}><path d="M12 5v14M5 12h14" /></Base>
);
export const MinusIcon = (p: IconProps) => (
  <Base {...p}><path d="M5 12h14" /></Base>
);
export const TruckIcon = (p: IconProps) => (
  <Base {...p}><path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z" /><circle cx="7" cy="18" r="1.5" /><circle cx="17" cy="18" r="1.5" /></Base>
);
export const ShieldIcon = (p: IconProps) => (
  <Base {...p}><path d="M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6z" /><path d="m9 12 2 2 4-4" /></Base>
);
export const PackageIcon = (p: IconProps) => (
  <Base {...p}><path d="m12 3 8 4v10l-8 4-8-4V7z" /><path d="M4 7l8 4 8-4M12 11v10" /></Base>
);
export const StoreIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 10 5.5 4h13L20 10" /><path d="M4 10c0 1.7 1.3 3 3 3s2.5-1.3 2.5-3c0 1.7 1.2 3 2.5 3s2.5-1.3 2.5-3c0 1.7 1.3 3 3 3s3-1.3 3-3" /><path d="M5 13v7h14v-7M10 20v-5h4v5" /></Base>
);
export const PhoneIcon = (p: IconProps) => (
  <Base {...p}><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" /></Base>
);
export const MailIcon = (p: IconProps) => (
  <Base {...p}><rect x="3" y="5" width="18" height="14" /><path d="m3 7 9 6 9-6" /></Base>
);
export const MapPinIcon = (p: IconProps) => (
  <Base {...p}><path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z" /><circle cx="12" cy="10" r="2" /></Base>
);
export const ClockIcon = (p: IconProps) => (
  <Base {...p}><circle cx="12" cy="12" r="8" /><path d="M12 8v4l3 2" /></Base>
);
export const FilterIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 6h16M7 12h10M10 18h4" /></Base>
);
export const SortIcon = (p: IconProps) => (
  <Base {...p}><path d="M7 4v16M7 20l-3-3M7 20l3-3M17 20V4M17 4l-3 3M17 4l3 3" /></Base>
);
export const GiftIcon = (p: IconProps) => (
  <Base {...p}><rect x="4" y="10" width="16" height="10" /><path d="M3 7h18v3H3zM12 7v13M12 7c-2-3-6-3-6-.5S10 7 12 7zm0 0c2-3 6-3 6-.5S14 7 12 7z" /></Base>
);
export const InfoIcon = (p: IconProps) => (
  <Base {...p}><circle cx="12" cy="12" r="8.5" /><path d="M12 11v5M12 8h.01" /></Base>
);
export const WarningIcon = (p: IconProps) => (
  <Base {...p}><path d="M12 4 3 20h18z" /><path d="M12 10v4M12 17h.01" /></Base>
);
export const LeafIcon = (p: IconProps) => (
  <Base {...p}><path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z" /><path d="M5 19c3-4 6-7 10-9" /></Base>
);
export const DropIcon = (p: IconProps) => (
  <Base {...p}><path d="M12 3s6 7 6 11.5a6 6 0 0 1-12 0C6 10 12 3 12 3z" /></Base>
);
export const SunIcon = (p: IconProps) => (
  <Base {...p}><circle cx="12" cy="12" r="4" /><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4" /></Base>
);
export const LockIcon = (p: IconProps) => (
  <Base {...p}><rect x="5" y="11" width="14" height="10" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></Base>
);
export const LogoutIcon = (p: IconProps) => (
  <Base {...p}><path d="M10 4H5v16h5M14 8l4 4-4 4M18 12H9" /></Base>
);
export const ExternalIcon = (p: IconProps) => (
  <Base {...p}><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6" /></Base>
);
export const TrashIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6" /></Base>
);
export const EditIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 20h4l11-11-4-4L4 16z" /><path d="m13 7 4 4" /></Base>
);
export const DownloadIcon = (p: IconProps) => (
  <Base {...p}><path d="M12 4v11M7 11l5 5 5-5M4 20h16" /></Base>
);
export const HomeIcon = (p: IconProps) => (
  <Base {...p}><path d="m3 11 9-7 9 7v9h-6v-6H9v6H3z" /></Base>
);
export const ChartIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 20V4M4 20h16M8 16v-5M12 16V8M16 16v-3" /></Base>
);
export const TagIcon = (p: IconProps) => (
  <Base {...p}><path d="M3 12V4h8l10 10-8 8z" /><circle cx="7.5" cy="8.5" r="1" /></Base>
);
export const UsersIcon = (p: IconProps) => (
  <Base {...p}><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20c0-3 3-5 6.5-5s6.5 2 6.5 5" /><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 15c2.2.6 3.5 2.2 3.5 4.5" /></Base>
);
export const ChatIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 5h16v11H9l-5 4z" /></Base>
);
export const BookIcon = (p: IconProps) => (
  <Base {...p}><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z" /><path d="M4 19V5M8 3v16" /></Base>
);
export const ListIcon = (p: IconProps) => (
  <Base {...p}><path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01" /></Base>
);
export const BoxesIcon = (p: IconProps) => (
  <Base {...p}><rect x="3" y="12" width="8" height="8" /><rect x="13" y="12" width="8" height="8" /><rect x="8" y="4" width="8" height="8" /></Base>
);
export const SparkIcon = (p: IconProps) => (
  <Base {...p}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6.5 6.5 9 9M15 15l2.5 2.5M6.5 17.5 9 15M15 9l2.5-2.5" /></Base>
);
export const CardIcon = (p: IconProps) => (
  <Base {...p}><rect x="3" y="6" width="18" height="12" /><path d="M3 10h18M7 15h4" /></Base>
);
export const BankIcon = (p: IconProps) => (
  <Base {...p}><path d="m3 9 9-5 9 5H3zM5 9v8M10 9v8M14 9v8M19 9v8M3 20h18" /></Base>
);
export const CashIcon = (p: IconProps) => (
  <Base {...p}><rect x="3" y="7" width="18" height="10" /><circle cx="12" cy="12" r="2.5" /><path d="M6 10h.01M18 14h.01" /></Base>
);
export const RefreshIcon = (p: IconProps) => (
  <Base {...p}><path d="M20 12a8 8 0 0 1-14.5 4.6M4 12a8 8 0 0 1 14.5-4.6M18 3v4.5h-4.5M6 21v-4.5h4.5" /></Base>
);
export const EyeIcon = (p: IconProps) => (
  <Base {...p}><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z" /><circle cx="12" cy="12" r="3" /></Base>
);
export const LogoMark = ({ size = 28, ...rest }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true" focusable="false" {...rest}>
    <circle cx="16" cy="16" r="14.5" stroke="currentColor" strokeWidth="1" />
    <path d="M20.5 11.5c-1-1.3-2.5-2-4.3-2-3.6 0-6.2 2.8-6.2 6.5s2.6 6.5 6.2 6.5c1.8 0 3.3-.7 4.3-2" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
    <circle cx="22" cy="16" r="1" fill="currentColor" />
  </svg>
);
