import React from 'react';
import Icons from '../Icons';

export function fmtCountdown(total) {
  if (total < 0) total = 0;
  const d = Math.floor(total / 86400);
  const h = Math.floor((total % 86400) / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const p = (n) => String(n).padStart(2, '0');
  return (d > 0 ? `${d}d ` : '') + `${p(h)}:${p(m)}:${p(s)}`;
}

/**
 * ContestHero — hero card for the current / upcoming contest.
 *
 * Props:
 *   contest    — { name, round, startsIn, duration, registeredCount, yourRank, yourScore, solved, problems:[{id,title,points,status,href}] }
 *   state      — 'live' | 'soon' | 'none'
 *   remaining  — live countdown (seconds)
 *   registered — boolean (soon state)
 *   onRegister — () => void
 */
export default function ContestHero({ contest, state, remaining, registered, onRegister }) {
  const I = Icons;
  const urgent = state === 'live' && remaining < 5 * 60;
  const badge = state === 'live'
    ? <span className="hbadge live"><span className="d" /> Live now</span>
    : state === 'soon'
      ? <span className="hbadge soon"><I.clock size={13} /> Starts soon</span>
      : <span className="hbadge none">No live contest</span>;

  const clockVal = state === 'live' ? remaining : contest.startsIn;
  const clockLbl = state === 'live' ? 'Ends in' : state === 'soon' ? 'Starts in' : 'Next contest in';

  return (
    <section className="hero">
      <div className="hero-hd">
        {badge}
        {state === 'soon' && (
          <span className="reg-chip"><I.users size={14} /> <b>{contest.registeredCount.toLocaleString()}</b> registered</span>
        )}
        {state === 'live' && (
          <span className="reg-chip"><I.users size={14} /> <b>{contest.registeredCount.toLocaleString()}</b> competing</span>
        )}
      </div>

      <div className="hero-title">{contest.name}</div>
      <div className="hero-round">{contest.round}</div>

      <div className="hero-meta">
        <div className="m">
          <div className="k">{clockLbl}</div>
          <div className={`v clock${urgent ? ' urgent' : ''}`}>{fmtCountdown(clockVal)}</div>
        </div>
        <div className="m"><div className="k">Duration</div><div className="v">{contest.duration}</div></div>
        <div className="m"><div className="k">Problems</div><div className="v">{contest.problems.length}</div></div>
        {state === 'live' && (
          <div className="m"><div className="k">Your rank</div><div className="v">#{contest.yourRank}</div></div>
        )}
      </div>

      {state === 'live' ? (
        <>
          <div className="hero-probs">
            {contest.problems.map((p) => {
              const St = p.status === 'solved' ? I.checkBold
                : p.status === 'attempted' ? I.bolt
                : p.status === 'locked' ? null : I.chevRight;
              return (
                <a key={p.id} className={`hpip s-${p.status}`} href={p.href}>
                  <span className="lid">{p.id}</span>
                  <span className="ld">
                    <span className="nm">{p.title}</span>
                    <span className="pt">{p.points} pts</span>
                  </span>
                  <span
                    className="stx"
                    style={{ color: p.status === 'solved' ? 'var(--ac)' : p.status === 'attempted' ? 'var(--tle)' : 'var(--fg3)' }}
                  >
                    {St && <St size={15} />}
                  </span>
                </a>
              );
            })}
          </div>
          <div className="hero-foot">
            <div className="hero-stand">
              <div className="s"><div className="k">Score</div><div className="v"><span className="pl">{contest.yourScore}</span></div></div>
              <div className="s"><div className="k">Solved</div><div className="v">{contest.solved}/{contest.problems.length}</div></div>
            </div>
            <div className="hero-cta">
              <a className="btn btn-primary" href="#"><I.play size={15} /> Enter round</a>
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="hero-preview">
            <span className="pv-k">Problems</span>
            <div className="pv-pips">
              {contest.problems.map((p) => <span key={p.id} className="pv-pip">{p.id}</span>)}
            </div>
            <span className="pv-note">revealed when the round starts</span>
          </div>
          <div className="hero-foot">
            <div className="hero-stand">
              <div className="s"><div className="k">Format</div><div className="v">{contest.round.split(' · ')[1] || 'Rated'}</div></div>
              <div className="s"><div className="k">Going</div><div className="v">{contest.registeredCount.toLocaleString()}</div></div>
            </div>
            <div className="hero-cta">
              {state === 'soon' ? (
                registered
                  ? <span className="reg-pill done"><I.checkBold size={14} /> Registered</span>
                  : <button className="btn btn-primary" onClick={onRegister}><I.flag size={15} /> Register</button>
              ) : (
                <a className="btn btn-primary" href="#"><I.trophy size={15} /> Browse contests</a>
              )}
              <a className="btn" href="#">Problems</a>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
