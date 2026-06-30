import client from './client';

// GET problems/recommended/ -> up to 6 unsolved problems for the current user
// ([{ id, title, difficulty, tags, acceptance }]), ordered easy -> hard.
export async function getRecommended() {
  const { data } = await client.get('problems/recommended/');
  return data;
}
