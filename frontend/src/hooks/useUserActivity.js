import { useEffect, useState } from 'react';

import { getUserActivity } from '../api/users';

// Loads a user's per-day submission counts for the activity heatmap.
export function useUserActivity(username) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!username) return undefined;
    let active = true;
    setLoading(true);
    setError(null);
    getUserActivity(username)
      .then((counts) => active && setData(counts))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [username]);

  return { data, loading, error };
}
