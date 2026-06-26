import { useAuthStore } from '../store/authStore';

// Avatar badge initials: first two letters of the username.
function initialsOf(username) {
  return username.slice(0, 2).toUpperCase();
}

/**
 * Current user for the page shell (sidebar + navbar). Comes straight from the
 * auth store — no extra request, since the shell only needs name + initials.
 */
export function useCurrentUser() {
  const username = useAuthStore((s) => s.user?.username);
  if (!username) return null;
  return { username, initials: initialsOf(username) };
}
