import { useEffect, useState } from 'react';

import { getUser, getEloHistory } from '../api/users';

// Loads ProfileCard data: the user (ELO + rank) and their rating history,
// fetched in parallel.
export function useProfile(username) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!username) return undefined;
    let active = true;
    Promise.all([getUser(username), getEloHistory(username)])
      .then(([user, history]) => active && setData({ user, history }))
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [username]);

  return { data, loading, error };
}
