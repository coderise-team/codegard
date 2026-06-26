import React from 'react';
import Icons from '../Icons';
import EmptyState from './EmptyState';

/**
 * RecentSubmissions — table of the user's latest submissions (across problems).
 *
 * Props:
 *   submissions — [{ id, title, verdict, lang, runtime, when, href }]
 */
export default function RecentSubmissions({ submissions }) {
  const I = Icons;

  if (!submissions.length) {
    return (
      <EmptyState
        icon="list"
        title="No submissions yet"
        sub="Solve your first problem to see your verdict history here."
        cta="Browse problems"
      />
    );
  }

  return (
    <section className="card">
      <div className="card-hd">
        <span className="t"><I.list size={16} /> Recent submissions</span>
        <button className="more">All <I.chevRight size={13} /></button>
      </div>
      <div className="card-bd flush">
        <table className="subtab">
          <thead>
            <tr>
              <th>Problem</th><th>Verdict</th><th>Lang</th><th>Runtime</th>
              <th style={{ textAlign: 'right' }}>When</th>
            </tr>
          </thead>
          <tbody>
            {submissions.map((s) => (
              <tr key={s.id} onClick={() => { if (s.href && s.href !== '#') window.location.href = s.href; }}>
                <td><span className="st-id">#{s.id}</span> &nbsp;<span className="st-title">{s.title}</span></td>
                <td><span className={`vd v-${s.verdict}`}>{s.verdict}</span></td>
                <td className="mono">{s.lang}</td>
                <td className="mono">{s.runtime}</td>
                <td className="st-when" style={{ textAlign: 'right' }}>{s.when}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
