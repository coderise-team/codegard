import { useEffect, useState } from 'react';

import { getDaily } from '../api/problems';
import { getStreak } from '../api/users';

// Loads the Daily challenge block: today's problem and the user's streak,
// fetched in parallel.
export function useDailyChallenge(username) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!username) return undefined;
    let active = true;
    Promise.all([getDaily(), getStreak(username)])
      .then(([daily, streak]) => active && setData({ daily, streak }))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [username]);

  return { data, loading, error };
}
