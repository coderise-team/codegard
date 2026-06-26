import React from 'react';
import Icons from '../Icons';

/**
 * ActivityHeatmap — GitHub-style year calendar (intensity = problems solved/day).
 *
 * Props:
 *   activity — { weeks:[[cell|null ×7]…], months:[{i,label}], total, days }
 *              cell = { c: solved-count, t: "Jun 4" }.  Sunday-first columns.
 */
export default function ActivityHeatmap({ activity }) {
  const I = Icons;
  const weeks = activity.weeks;
  const months = activity.months || [];
  const W = weeks.length;
  const lvl = (c) => (c <= 0 ? 0 : c <= 2 ? 1 : c <= 4 ? 2 : c <= 6 ? 3 : 4);
  const dayLabel = { 1: 'Mon', 3: 'Wed', 5: 'Fri' };

  return (
    <section className="card act-card">
      <div className="card-hd">
        <span className="t"><I.flame size={16} /> Activity</span>
        <span className="act-sum"><b>{activity.total}</b> solved · 1 yr</span>
      </div>
      <div className="card-bd cal">
        <div className="cal-top">
          <span className="cal-corner" />
          <div className="cal-months">
            {months.map((m, idx) => {
              const next = months[idx + 1] ? months[idx + 1].i : W;
              return <span key={m.i} style={{ width: (next - m.i) * 14 }}>{m.label}</span>;
            })}
          </div>
          <div className="cal-days">
            {[0, 1, 2, 3, 4, 5, 6].map((r) => (
              <span key={r} style={{ gridRow: r + 1 }}>{dayLabel[r] || ''}</span>
            ))}
          </div>
          <div className="cal-grid">
            {weeks.map((w, wi) =>
              [0, 1, 2, 3, 4, 5, 6].map((di) => {
                const cell = w[di];
                return cell ? (
                  <i
                    key={`${wi}-${di}`}
                    className={`cc l${lvl(cell.c)}`}
                    title={`${cell.c === 0 ? 'No' : cell.c} solved · ${cell.t}`}
                  />
                ) : (
                  <i key={`${wi}-${di}`} className="cc empty" />
                );
              })
            )}
          </div>
        </div>
        <div className="cal-foot">
          <span>{activity.days} active days</span>
          <span className="cf-legend">
            Less <i className="cc l1" /><i className="cc l2" /><i className="cc l3" /><i className="cc l4" /> More
          </span>
        </div>
      </div>
    </section>
  );
}
