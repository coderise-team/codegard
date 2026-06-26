import { useEffect, useState } from 'react';

import { getMyContestHistory } from '../api/contests';

// Loads the authenticated user's finished contests (newest first).
export function useMyContestHistory() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    getMyContestHistory()
      .then((history) => active && setData(history))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  return { data, loading, error };
}
