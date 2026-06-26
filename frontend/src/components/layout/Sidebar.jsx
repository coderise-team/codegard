import React from 'react';
import Icons from '../Icons';

/**
 * Sidebar — left navigation panel.
 *
 * Props:
 *   nav      — array { id, label, icon }  (main items)
 *   navSub   — array { id, label, icon }  (bottom items: Settings, etc.)
 *   user     — { handle, rating, initials }
 *   activeId — id of the active item
 *   onNav    — (id: string) => void
 */
export default function Sidebar({ nav, navSub, user, activeId, onNav }) {
  return (
    <aside className="side">
      <div className="side-top">
        <a href="/" className="logo">
          <span className="mark">C</span>
          <span><span className="wm-a">Code</span><span className="wm-b">gard</span></span>
        </a>
      </div>

      <nav className="side-nav scroll">
        {nav.map((item) => {
          const Icon = Icons[item.icon] || Icons.grid;
          return (
            <button
              key={item.id}
              className={`nav-link${activeId === item.id ? ' is-active' : ''}`}
              onClick={() => onNav(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.id === 'contests' && <span className="nl-tag">LIVE</span>}
            </button>
          );
        })}
      </nav>

      <div className="side-foot">
        {navSub.map((item) => {
          const Icon = Icons[item.icon] || Icons.settings;
          return (
            <button
              key={item.id}
              className={`nav-link${activeId === item.id ? ' is-active' : ''}`}
              onClick={() => onNav(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
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
