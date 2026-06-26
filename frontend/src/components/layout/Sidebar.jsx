import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import Icons from '../Icons';

// App navigation — static app sections, not API data.
// Pages other than Dashboard are delivered in their own PRs.
const NAV = [
  { label: 'Dashboard', icon: 'home', to: '/' },
  { label: 'Problems', icon: 'grid', to: '/problems' },
  { label: 'Contests', icon: 'trophy', to: '/contests' },
  { label: 'Standings', icon: 'chart', to: '/standings' },
  { label: 'Practice', icon: 'target', to: '/practice' },
  { label: 'Groups', icon: 'users', to: '/groups' },
];

const NAV_SUB = [{ label: 'Settings', icon: 'settings', to: '/settings' }];

const linkClass = ({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`;

/**
 * Sidebar — left navigation panel.
 *
 * Props:
 *   user — { handle, rating, initials }  (bottom mini card)
 */
export default function Sidebar({ user }) {
  return (
    <aside className="side">
      <div className="side-top">
        <Link to="/" className="logo">
          <span className="mark">C</span>
          <span><span className="wm-a">Code</span><span className="wm-b">gard</span></span>
        </Link>
      </div>

      <nav className="side-nav scroll">
        {NAV.map((item) => {
          const Icon = Icons[item.icon] || Icons.grid;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={linkClass}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="side-foot">
        {NAV_SUB.map((item) => {
          const Icon = Icons[item.icon] || Icons.settings;
          return (
            <NavLink key={item.to} to={item.to} className={linkClass}>
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}

        <div className="nav-mini">
          <div className="avatar">{user.initials}</div>
          <div className="mid">
            <div className="h">{user.handle}</div>
            <div className="r">{user.rating}</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
