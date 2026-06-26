import client from './client';

// GET submissions/ -> paginated list of the authenticated user's submissions,
// newest first. Returns the results array.
export async function getSubmissions() {
  const { data } = await client.get('submissions/');
  return data.results;
}
