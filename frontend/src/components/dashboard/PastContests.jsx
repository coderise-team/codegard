import React from 'react';
import Icons from '../Icons';
import EmptyState from './EmptyState';

/**
 * PastContests — history of contests the user played.
 *
 * Props:
 *   items — [{ name, round, date, rank, delta, solved }]
 */
export default function PastContests({ items }) {
  const I = Icons;

  if (!items.length) {
    return (
      <EmptyState
        icon="trophy"
        title="No contests played"
        sub="Register for an upcoming round to start building your rating."
        cta="See upcoming"
      />
    );
  }

  return (
    <section className="card">
      <div className="card-hd">
        <span className="t"><I.trophy size={16} /> Contest history</span>
        <button className="more">All <I.chevRight size={13} /></button>
      </div>
      <div className="card-bd flush">
        <div className="rowlist">
          {items.map((c) => {
            const up = c.delta >= 0;
            return (
              <a key={c.name} className="lrow crow" href="#">
                <div className="lr-main">
                  <div className="lr-title">{c.name}</div>
                  <div className="lr-sub">
                    <span className="lr-num">{c.date}</span>
                    <span className="tag">{c.round}</span>
                    <span className="lr-num">Solved {c.solved}</span>
                  </div>
                </div>
                <div className="lr-right">
                  <span className="cc-rank">#{c.rank}</span>
                  <span className={`cc-delta ${up ? 'up' : 'down'}`}>{up ? '+' : ''}{c.delta}</span>
                </div>
              </a>
            );
          })}
        </div>
      </div>
    </section>
  );
}
