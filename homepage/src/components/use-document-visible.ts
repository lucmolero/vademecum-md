import { useSyncExternalStore } from 'react';

const subscribe = (notify: () => void) => {
  document.addEventListener('visibilitychange', notify);
  return () => document.removeEventListener('visibilitychange', notify);
};

/** Shared lifecycle signal for work that has no value in a background tab. */
export function useDocumentVisible() {
  return useSyncExternalStore(subscribe, () => !document.hidden, () => true);
}
