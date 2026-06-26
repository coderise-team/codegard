import Icons from '../Icons';
import EmptyState from './EmptyState';
import { useUpcomingContests } from '../../hooks/useUpcomingContests';
import { joinContest, leaveContest } from '../../api/contests';
import { formatDuration } from '../../utils/time';

const MAX_ROWS = 4;

const dayCell = (iso) => {
  const d = new Date(iso);
  return { d: d.getDate(), mo: d.toLocaleString('en', { month: 'short' }) };
};

/**
 * UpcomingContests — rail list of pending rounds with a register toggle.
 * Register / Going call the join / leave endpoints, then refetch.
 */
export default function UpcomingContests() {
  const I = Icons;
  const { data, loading, error, reload } = useUpcomingContests();

  const toggle = async (c) => {
    try {
      if (c.is_joined) await leaveContest(c.id);
      else await joinContest(c.id);
      reload();
    } catch {
      // leave the row as-is on failure
    }
  };

  if (data && data.length === 0) {
    return (
      <EmptyState
        icon="calendar"
        title="No upcoming contests"
        sub="New rounds will show up here once they are scheduled."
      />
    );
  }

  return (
    <section className="card">
      <div className="card-hd">
        <span className="t"><I.calendar size={16} /> Upcoming</span>
        <button className="more">Calendar <I.chevRight size={13} /></button>
      </div>
      <div className="card-bd flush">
        {loading && <div className="list-msg">Loading…</div>}
        {error && <div className="list-msg">Couldn’t load contests.</div>}
        {data &&
          data.slice(0, MAX_ROWS).map((c) => {
            const dl = dayCell(c.start_time);
            return (
              <div className="up-row" key={c.id}>
                <div className="up-cal">
                  <span className="d">{dl.d}</span>
                  <span className="mo">{dl.mo}</span>
                </div>
                <div className="um">
                  <div className="nm">{c.title}</div>
                  <div className="mt">
                    <span>{c.subtitle}</span>
                    <span>· {formatDuration(c.start_time, c.end_time)}</span>
                  </div>
                </div>
                <div className="ua">
                  {c.is_joined ? (
                    <button className="reg-pill done" onClick={() => toggle(c)}>
                      <I.checkBold size={13} /> Going
                    </button>
                  ) : (
                    <button className="reg-pill go" onClick={() => toggle(c)}>
                      <I.plus size={13} /> Register
                    </button>
                  )}
                </div>
              </div>
            );
          })}
      </div>
    </section>
  );
}
