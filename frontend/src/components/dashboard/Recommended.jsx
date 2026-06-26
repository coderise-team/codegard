import Icons from '../Icons';

/**
 * Recommended — list of suggested problems (by weak tags / next tier).
 *
 * Props:
 *   items — [{ id, title, difficulty, tags:[], acc, reason, href }]
 */
export default function Recommended({ items }) {
  const I = Icons;
  return (
    <section className="card">
      <div className="card-hd">
        <span className="t"><I.sparkle size={16} /> Recommended for you</span>
        <button className="more">Problemset <I.chevRight size={13} /></button>
      </div>
      <div className="card-bd flush">
        <div className="rowlist">
          {items.map((p) => (
            <a key={p.id} className="lrow" href={p.href}>
              <span className="lr-id">#{p.id}</span>
              <div className="lr-main">
                <div className="lr-title">{p.title}</div>
                <div className="lr-sub">
                  <span className={`df d-${p.difficulty.toLowerCase()}`}>{p.difficulty}</span>
                  {p.tags.map((t) => <span key={t} className="tag">{t}</span>)}
                </div>
              </div>
              <div className="lr-right">
                <span className="lr-reason">{p.reason}</span>
                <span className="lr-num">{p.acc}%</span>
                <I.chevRight size={16} className="chev" />
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
