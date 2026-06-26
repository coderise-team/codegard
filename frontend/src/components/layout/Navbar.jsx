import Icons from '../Icons';

/**
 * Navbar — top dashboard bar (breadcrumb, search, notifications, user).
 *
 * Props:
 *   user  — { handle, rating, rank, initials }
 *   title — breadcrumb string (e.g. "Dashboard")
 */
export default function Navbar({ user, title = 'Dashboard' }) {
  return (
    <header className="tbar">
      <div className="crumb">{title}</div>
      <div className="tbar-spacer" />

      <div className="gsearch">
        <Icons.search size={15} />
        <input placeholder="Search problems, users, contests…" />
        <span className="kbd">/</span>
      </div>

      <button className="icon-btn" title="Notifications">
        <Icons.bell size={17} />
        <span className="nd" />
      </button>

      <div className="user-chip">
        <div className="meta">
          <div className="handle">{user.handle}</div>
          <div className="rating">{user.rating} · {user.rank}</div>
        </div>
        <div className="avatar">{user.initials}</div>
      </div>
    </header>
  );
}
