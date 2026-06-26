import React from 'react';
import Icons from '../Icons';

/**
 * UpcomingContests — rail list of upcoming rounds with register toggle.
 *
 * Props:
 *   contests    — [{ name, round, startsIn, duration, registered, going }]
 *   regMap      — { [index]: boolean } registration overrides
 *   onToggleReg — (index: number) => void
 */
export default function UpcomingContests({ contests, regMap = {}, onToggleReg }) {
  const I = Icons;
  const dayLabel = (secs) => {
    const dd = new Date(Date.now() + secs * 1000);
    return { d: dd.getDate(), mo: dd.toLocaleString('en', { month: 'short' }) };
  };

  return (
    <section className="card">
      <div className="card-hd">
        <span className="t"><I.calendar size={16} /> Upcoming</span>
        <button className="more">Calendar <I.chevRight size={13} /></button>
      </div>
      <div className="card-bd flush">
        {contests.map((c, i) => {
          const reg = regMap[i] ?? c.registered;
          const dl = dayLabel(c.startsIn);
          return (
            <div className="up-row" key={c.name}>
              <div className="up-cal"><span className="d">{dl.d}</span><span className="mo">{dl.mo}</span></div>
              <div className="um">
                <div className="nm">{c.name}</div>
                <div className="mt"><span>{c.round}</span><span>· {c.duration}</span></div>
              </div>
              <div className="ua">
                {reg ? (
                  <span className="reg-pill done"><I.checkBold size={13} /> Going</span>
                ) : (
                  <button className="reg-pill go" onClick={() => onToggleReg(i)}><I.plus size={13} /> Register</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
