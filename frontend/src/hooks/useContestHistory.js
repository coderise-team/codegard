import { useEffect, useState } from 'react';

import { getContestHistory } from '../api/users';

// Loads a user's finished contests (newest first).
export function useContestHistory(username) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!username) return undefined;
    let active = true;
    getContestHistory(username)
      .then((history) => active && setData(history))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [username]);

  return { data, loading, error };
}
