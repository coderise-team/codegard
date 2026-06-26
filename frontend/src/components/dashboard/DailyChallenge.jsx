import React from 'react';
import Icons from '../Icons';

/**
 * DailyChallenge — daily problem + 14-day streak tracker.
 *
 * Props:
 *   daily — { title, difficulty, tags:[], points, acceptance,
 *            solvedToday, streak, history:[…] }  history: 1=solved, 0=miss, 2=today
 */
export default function DailyChallenge({ daily }) {
  const I = Icons;
  return (
    <section className="card">
      <div className="card-hd">
        <span className="t"><I.flame size={16} style={{ color: 'var(--tle)' }} /> Daily challenge</span>
        <button className="more">All <I.chevRight size={13} /></button>
      </div>
      <div className="card-bd">
        <div className="daily-top">
          <div className="dt-main">
            <div className="dt-title">{daily.title}</div>
            <div className="dt-sub">
              <span className={`df d-${daily.difficulty.toLowerCase()}`}>{daily.difficulty}</span>
              {daily.tags.map((t) => <span key={t} className="tag">{t}</span>)}
            </div>
            <div className="dt-acc">{daily.acceptance}% AC</div>
          </div>
          <div className="daily-flame">
            <I.flame size={22} />
            <span className="n">{daily.streak}</span>
            <span className="u">streak</span>
          </div>
        </div>

        <div className="streak-grid">
          {daily.history.map((v, i) => (
            <div
              key={i}
              className={`sd ${v === 1 ? 'on' : v === 2 ? 'today' : 'miss'}`}
              title={v === 1 ? 'Solved' : v === 2 ? 'Today' : 'Missed'}
            />
          ))}
        </div>

        <button className="btn btn-primary btn-block">
          <I.bolt size={15} /> {daily.solvedToday ? 'Solved today ✓' : `Solve for +${daily.points} pts`}
        </button>
      </div>
    </section>
  );
}
