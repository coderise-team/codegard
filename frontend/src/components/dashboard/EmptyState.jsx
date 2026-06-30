import Icons from '../Icons';

/**
 * EmptyState — empty-card placeholder for lists with no data (new users).
 *
 * Props:
 *   icon  — key from Icons (default "doc")
 *   title — heading
 *   sub   — supporting line
 *   cta   — optional button label
 *   href  — button link (default "#")
 */
export default function EmptyState({
  icon = 'doc',
  title,
  sub,
  cta,
  href = '#',
}) {
  const Icon = Icons[icon] || Icons.doc;
  return (
    <section className="card">
      <div className="empty-card">
        <div className="ei">
          <Icon size={20} />
        </div>
        <div className="et">{title}</div>
        <div className="es">{sub}</div>
        {cta && (
          <a className="btn btn-primary btn-sm" href={href}>
            {cta}
          </a>
        )}
      </div>
    </section>
  );
}
