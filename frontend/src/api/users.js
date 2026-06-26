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
