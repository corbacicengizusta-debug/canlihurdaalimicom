import { useEffect, useMemo, useState } from 'react';

type Trend = 'up' | 'down' | 'same';

type Item = {
  n: string;
  p: number;
  change?: Trend;
  percent?: number;
};

type Category = {
  t: string;
  i: Item[];
};

type PricePayload = {
  updated_at?: string;
  data?: Category[];
};

const TL_FORMAT = new Intl.NumberFormat('tr-TR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function formatTl(value: number) {
  return `₺${TL_FORMAT.format(value)}`;
}

function getTrendMeta(item: Item) {
  const percent = Number(item.percent || 0).toFixed(2);
  if (item.change === 'up') {
    return { className: 'up' as const, arrow: '▲', label: `+%${percent}` };
  }
  if (item.change === 'down') {
    return { className: 'down' as const, arrow: '▼', label: `-%${percent}` };
  }
  return { className: 'same' as const, arrow: '•', label: 'SABİT' };
}

export default function App() {
  const [payload, setPayload] = useState<PricePayload>({ data: [] });
  const [search, setSearch] = useState('');
  const [now, setNow] = useState(new Date());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await fetch(`/fiyatlar.json?v=${Date.now()}`, { cache: 'no-store' });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const json = (await response.json()) as PricePayload;
        setPayload({
          updated_at: json.updated_at,
          data: Array.isArray(json.data) ? json.data : [],
        });
      } catch (err) {
        console.error(err);
        setError('Veri yüklenemedi. public/fiyatlar.json dosyasını kontrol et.');
      } finally {
        setLoading(false);
      }
    };

    void loadData();

    const clock = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(clock);
  }, []);

  const filteredCategories = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('tr-TR');
    const data = payload.data ?? [];

    if (!query) return data;

    return data
      .map((category) => {
        const categoryMatch = category.t.toLocaleLowerCase('tr-TR').includes(query);
        const items = category.i.filter((item) => {
          if (categoryMatch) return true;
          return item.n.toLocaleLowerCase('tr-TR').includes(query);
        });

        return items.length ? { ...category, i: items } : null;
      })
      .filter(Boolean) as Category[];
  }, [payload.data, search]);

  const summary = useMemo(() => {
    let categoryCount = payload.data?.length ?? 0;
    let itemCount = 0;
    let up = 0;
    let down = 0;
    let same = 0;

    for (const category of payload.data ?? []) {
      for (const item of category.i) {
        itemCount += 1;
        if (item.change === 'up') up += 1;
        else if (item.change === 'down') down += 1;
        else same += 1;
      }
    }

    return { categoryCount, itemCount, up, down, same };
  }, [payload.data]);

  const tickerItems = useMemo(() => {
    const flat = (payload.data ?? [])
      .flatMap((category) => category.i.map((item) => ({ ...item, category: category.t })))
      .filter((item) => item.change === 'up' || item.change === 'down')
      .sort((a, b) => Number(b.percent || 0) - Number(a.percent || 0));

    if (!flat.length) {
      return [{ n: 'Piyasa listesi aktif', p: 0, change: 'same' as Trend, percent: 0, category: 'CANLI AKIŞ' }];
    }

    return flat.slice(0, 18);
  }, [payload.data]);

  const strongest = useMemo(() => {
    const flat = (payload.data ?? []).flatMap((category) =>
      category.i.map((item) => ({ ...item, category: category.t })),
    );
    const sorted = [...flat].sort((a, b) => b.p - a.p);
    return {
      highest: sorted[0],
      lowest: sorted[sorted.length - 1],
    };
  }, [payload.data]);

  return (
    <div className="page-shell">
      <div className="ambient ambient-1" />
      <div className="ambient ambient-2" />

      <div className="container">
        <header className="hero-card">
          <div className="hero-main">
            <div className="hero-accent" />
            <div>
              <p className="eyebrow">TÜRKİYE GENELİ CANLI HURDA BORSASI</p>
              <h1>Canlı Hurda Fiyatları</h1>
              <p className="hero-text">
                Düzenli sütun yapısı, anlık borsa görünümü, kayan fiyat bandı ve kategori bazlı
                okunabilir fiyat panelleri.
              </p>
            </div>
          </div>

          <div className="hero-side">
            <div className="digital-clock">{now.toLocaleTimeString('tr-TR')}</div>
            <div className="digital-date">
              {now.toLocaleDateString('tr-TR', {
                weekday: 'long',
                day: '2-digit',
                month: 'long',
                year: 'numeric',
              })}
            </div>
            <div className="updated-badge">
              Son güncelleme: {payload.updated_at || 'Bilinmiyor'}
            </div>
          </div>
        </header>

        <section className="market-strip">
          <div className="market-strip-track">
            {[...tickerItems, ...tickerItems].map((item, index) => {
              const trend = getTrendMeta(item);
              return (
                <div className={`ticker-pill ${trend.className}`} key={`${item.category}-${item.n}-${index}`}>
                  <span className="ticker-category">{item.category}</span>
                  <strong>{item.n}</strong>
                  {item.change === 'same' ? (
                    <span className="ticker-value">Liste aktif</span>
                  ) : (
                    <span className="ticker-value">
                      {trend.arrow} {trend.label} • {formatTl(item.p)}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </section>

        <section className="summary-grid">
          <article className="summary-card glow-green">
            <span>Kategori</span>
            <strong>{summary.categoryCount}</strong>
          </article>
          <article className="summary-card">
            <span>Toplam fiyat</span>
            <strong>{summary.itemCount}</strong>
          </article>
          <article className="summary-card glow-up">
            <span>Yükselen</span>
            <strong>{summary.up}</strong>
          </article>
          <article className="summary-card glow-down">
            <span>Düşen</span>
            <strong>{summary.down}</strong>
          </article>
          <article className="summary-card">
            <span>Sabit</span>
            <strong>{summary.same}</strong>
          </article>
        </section>

        <section className="spotlight-grid">
          <article className="spotlight-card spotlight-positive">
            <span>En yüksek fiyat</span>
            <strong>{strongest.highest ? strongest.highest.n : '—'}</strong>
            <p>
              {strongest.highest
                ? `${strongest.highest.category} • ${formatTl(strongest.highest.p)}`
                : 'Veri yok'}
            </p>
          </article>
          <article className="spotlight-card spotlight-neutral">
            <span>En düşük fiyat</span>
            <strong>{strongest.lowest ? strongest.lowest.n : '—'}</strong>
            <p>
              {strongest.lowest
                ? `${strongest.lowest.category} • ${formatTl(strongest.lowest.p)}`
                : 'Veri yok'}
            </p>
          </article>
          <article className="spotlight-card spotlight-search">
            <label htmlFor="search-input">Fiyat veya kategori ara</label>
            <input
              id="search-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Bakır, kablo, krom, motor..."
            />
          </article>
        </section>

        {loading ? <div className="state-box">Veriler yükleniyor...</div> : null}
        {error ? <div className="state-box error">{error}</div> : null}

        {!loading && !error ? (
          <main className="price-grid">
            {filteredCategories.length ? (
              filteredCategories.map((category) => (
                <section className="price-card" key={category.t}>
                  <div className="price-card-head">
                    <div>
                      <h2>{category.t}</h2>
                      <span>{category.i.length} kalem</span>
                    </div>
                    <div className="mini-pulse" />
                  </div>

                  <div className="price-card-body">
                    {category.i.map((item, index) => {
                      const trend = getTrendMeta(item);
                      const buyPrice = item.p * 0.88;
                      return (
                        <article className="price-row" key={`${category.t}-${item.n}-${index}`}>
                          <div className="price-row-left">
                            <h3>{item.n}</h3>
                            <p>Alım referansı: {formatTl(buyPrice)}</p>
                          </div>

                          <div className="price-row-right">
                            <strong>{formatTl(item.p)}</strong>
                            <span>TL / KG</span>
                            <div className={`trend-badge ${trend.className}`}>
                              <span>{trend.arrow}</span>
                              <span>{trend.label}</span>
                            </div>
                          </div>
                        </article>
                      );
                    })}
                  </div>
                </section>
              ))
            ) : (
              <div className="state-box">Aramaya uygun sonuç bulunamadı.</div>
            )}
          </main>
        ) : null}
      </div>
    </div>
  );
}
