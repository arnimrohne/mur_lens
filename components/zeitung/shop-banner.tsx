import type { OberflaechenTexte } from '@/lib/zeitung/texte';

export const SHOP_URL = 'https://shop.morisyen.de/en-eur';

interface ShopBannerProps {
  texte: OberflaechenTexte;
}

/** Hinweis auf den eigenen Shop, als Werbung gekennzeichnet (Trennungsgebot, § 22 MStV). */
export function ShopBanner({ texte }: ShopBannerProps) {
  return (
    <aside className="gz-shop" aria-label={texte.shop.kennzeichnung}>
      <div className="gz-rahmen gz-shop-innen">
        <span className="gz-shop-kennzeichnung">{texte.shop.kennzeichnung}</span>
        <div className="gz-shop-text">
          <strong>{texte.shop.titel}</strong>
          <span>{texte.shop.text}</span>
        </div>
        <a className="gz-shop-knopf" href={SHOP_URL} target="_blank" rel="noopener">
          {texte.shop.knopf}
        </a>
      </div>
    </aside>
  );
}
