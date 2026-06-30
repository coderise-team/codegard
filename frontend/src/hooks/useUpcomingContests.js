import { useCallback, useEffect, useState } from 'react';

import { getContests } from '../api/contests';

// Loads pending contests, soonest start first. `reload` bumps a trigger so the
// effect refetches (used after a join/leave to get fresh registration state).
export function useUpcomingContests() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    getContests({ status: 'pending' })
      .then((list) => {
        if (!active) return;
        const sorted = [...list].sort(
          (a, b) => new Date(a.start_time) - new Date(b.start_time)
        );
        setError(null);
        setData(sorted);
      })
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const reload = useCallback(() => setReloadKey((k) => k + 1), []);

  return { data, loading, error, reload };
}
