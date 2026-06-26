import client from './client';

// GET users/{username}/stats/ -> { solved, contests, acceptance }
export async function getUserStats(username) {
  const { data } = await client.get(`users/${username}/stats/`);
  return data;
}

// GET users/{username}/activity/ -> sparse { "YYYY-MM-DD": submissions } map
// (only days with at least one submission are present).
export async function getUserActivity(username) {
  const { data } = await client.get(`users/${username}/activity/`);
  return data;
}

// GET users/{username}/ -> { username, elo_rating, rank, avatar, bio }
export async function getUser(username) {
  const { data } = await client.get(`users/${username}/`);
  return data;
}

// GET users/{username}/elo-history/ -> [{ rating, created_at }] oldest-first
export async function getEloHistory(username) {
  const { data } = await client.get(`users/${username}/elo-history/`);
  return data;
}
