import React from 'react';
import Icons from '../Icons';

/**
 * StatsStrip — 3-up row of quick stat cards.
 *
 * Props:
 *   stats — [{ k: label, v: value, icon: key from Icons }]
 */
export default function StatsStrip({ stats }) {
  return (
    <div className="stats3">
      {stats.map((s) => {
        const Icon = Icons[s.icon] || Icons.checkBold;
        return (
          <div className="stat" key={s.k}>
            <div className="si"><Icon size={18} /></div>
            <div>
              <div className="sv">{s.v}</div>
              <div className="sk">{s.k}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
