import client from './client';

// GET contests/my-history/ -> the authenticated user's finished contests,
// newest first (plain list, not paginated).
export async function getMyContestHistory() {
  const { data } = await client.get('contests/my-history/');
  return data;
}
