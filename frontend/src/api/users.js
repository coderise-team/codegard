import client from './client';

// GET users/{username}/stats/ -> { solved, contests, acceptance }
export async function getUserStats(username) {
  const { data } = await client.get(`users/${username}/stats/`);
  return data;
}
