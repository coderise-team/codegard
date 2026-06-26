import { useEffect, useState } from 'react';

import { getUserStats } from '../api/users';

// Fetches dashboard quick stats (solved / contests / acceptance) for a user.
export function useUserStats(username) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!username) return undefined;
    let active = true;
    getUserStats(username)
      .then((stats) => active && setData(stats))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [username]);

  return { data, loading, error };
}
