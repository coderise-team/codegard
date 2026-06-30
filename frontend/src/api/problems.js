import client from './client';

// GET problems/recommended/ -> up to 6 unsolved problems for the current user
// ([{ id, title, difficulty, tags, acceptance }]), ordered easy -> hard.
export async function getRecommended() {
  const { data } = await client.get('problems/recommended/');
  return data;
}

// GET problems/daily/ -> today's shared daily challenge, or null when none is
// assigned yet ({ id, title, difficulty, tags, acceptance, solved_today }).
export async function getDaily() {
  const { data } = await client.get('problems/daily/');
  return data;
}
