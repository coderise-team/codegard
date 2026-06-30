import { useEffect, useState } from 'react';

import { getRecommended } from '../api/problems';

// Loads personalised problem suggestions for the authenticated user.
export function useRecommended() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getRecommended()
      .then((items) => active && setData(items))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  return { data, loading, error };
}
