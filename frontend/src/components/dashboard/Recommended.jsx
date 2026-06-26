import EmptyState from './EmptyState';

/**
 * Recommended — personalised problem suggestions.
 *
 * STUB: there's no recommendation endpoint on the backend yet (problems now
 * expose tags + acceptance, but the "recommended for you" logic doesn't exist).
 * Shown as a placeholder until that lands; remove this stub then.
 */
export default function Recommended() {
  return (
    <EmptyState
      icon="sparkle"
      title="Recommended for you"
      sub="Coming soon — personalised problem suggestions aren't available yet."
    />
  );
}
