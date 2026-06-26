import React from 'react';
import Icons from '../Icons';

/** Gradient rating ring */
function RatingRing({ user }) {
  const R = 86;
  const C = 2 * Math.PI * R;
  const { floor, ceil } = user.nextTier;
  const frac = Math.max(0, Math.min(1, (user.rating - floor) / (ceil - floor)));
  const off = C * (1 - frac);

  return (
    <div className="ring-wrap">
      <svg viewBox="0 0 200 200" aria-hidden="true">
        <defs>
          <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="var(--gold-hi)" />
            <stop offset="1" stopColor="var(--gold)" />
          </linearGradient>
        </defs>
        <circle className="track" cx="100" cy="100" r={R} strokeWidth="14" />
        <circle
          className="meter"
          cx="100" cy="100" r={R}
          strokeWidth="14"
          strokeDasharray={C}
          strokeDashoffset={off}
        />
      </svg>
      <div className="ring-center">
        <div className="elo">{user.rating}</div>
        <div className="lab">ELO Rating</div>
        <div className="rk">{user.rank}</div>
      </div>
    </div>
  );
}

/** Rating-history sparkline */
function Sparkline({ history }) {
  const W = 300, H = 56, pad = 4;
  const rs = history.map((h) => h.r);
  const min = Math.min(...rs), max = Math.max(...rs);
  const span = max - min || 1;
  const x = (i) => pad + (i * (W - 2 * pad)) / (history.length - 1);
  const y = (r) => pad + (1 - (r - min) / span) * (H - 2 * pad);
  const line = history.map((h, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(h.r).toFixed(1)}`).join(' ');
  const area = `${line} L${x(history.length - 1).toFixed(1)} ${H} L${x(0).toFixed(1)} ${H} Z`;
  const last = history[history.length - 1];

  return (
    <div className="spark">
      <div className="shd">
        <span className="k">Rating · last {history.length}</span>
        <span className="v">{min}–{max}</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
        <defs>
          <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="var(--gold)" stopOpacity="0.22" />
            <stop offset="1" stopColor="var(--gold)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path className="ar" d={area} />
        <path className="ln" d={line} vectorEffect="non-scaling-stroke" />
        <circle className="dot-now" cx={x(history.length - 1)} cy={y(last.r)} r="3.5" vectorEffect="non-scaling-stroke" />
      </svg>
    </div>
  );
}

/**
 * ProfileCard — standing card with ELO ring, tier progress and sparkline.
 *
 * Props:
 *   user          — { handle, rating, rank, globalRank, maxRating, delta, nextTier:{ name, floor, ceil } }
 *   ratingHistory — [{ c, r, d }]  (oldest → newest)
 */
export default function ProfileCard({ user, ratingHistory }) {
  const up = user.delta >= 0;
  const { floor, ceil, name } = user.nextTier;

  return (
    <section className="card profile">
      <div className="card-hd">
        <span className="t"><Icons.award size={16} /> Your standing</span>
        <button className="more">Profile <Icons.chevRight size={13} /></button>
      </div>
      <div className="card-bd">
        <RatingRing user={user} />
        <div className="pmeta">
          <div className="pname">
            {user.handle}
            <span className={`pdelta ${up ? 'up' : 'down'}`}>
              {up ? <Icons.arrowUp size={12} /> : <Icons.arrowDown size={12} />}
              {up ? '+' : ''}{user.delta}
            </span>
          </div>
          <div className="ptier">Global rank <b>#{user.globalRank}</b> · max {user.maxRating}</div>

          <div className="tier-bar">
            <div className="lbl"><span>{floor}</span><span>→ {name}</span><span>{ceil}</span></div>
            <div className="track">
              <div className="fill" style={{ width: `${((user.rating - floor) / (ceil - floor)) * 100}%` }} />
            </div>
          </div>

          <Sparkline history={ratingHistory} />
        </div>
      </div>
    </section>
  );
}
