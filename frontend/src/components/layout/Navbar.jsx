import Icons from '../Icons';

/**
 * Navbar — top dashboard bar (breadcrumb, search, notifications, user).
 *
 * Props:
 *   user        — { username, initials }
 *   title       — breadcrumb string (e.g. "Dashboard")
 *   onMenuClick — open the sidebar drawer (phone only; burger button)
 */
export default function Navbar({ user, title = 'Dashboard', onMenuClick }) {
  return (
    <header className="tbar">
      <button className="nav-burger icon-btn" title="Menu" onClick={onMenuClick}>
        <Icons.menu size={18} />
      </button>
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
          <div className="handle">{user?.username}</div>
        </div>
        <div className="avatar">{user?.initials}</div>
      </div>
    </header>
  );
}
