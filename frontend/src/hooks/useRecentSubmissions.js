import { useEffect, useState } from 'react';

import { getSubmissions } from '../api/submissions';

// Loads the authenticated user's latest submissions (newest first).
export function useRecentSubmissions() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    getSubmissions()
      .then((subs) => active && setData(subs))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  return { data, loading, error };
}
