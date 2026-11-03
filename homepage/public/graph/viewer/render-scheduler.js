/** Render only while visible and something is changing. Timers never poll frames. */
export function createRenderScheduler({ resume, pause, now = () => performance.now(), setTimer = setTimeout, clearTimer = clearTimeout }) {
  let visible = true, contextAvailable = true, continuous = false, settled = false;
  let dragging = false, busyUntil = 0, timer = 0, running = null, destroyed = false;
  function reconcile() {
    clearTimer(timer);
    if (destroyed) return;
    const remaining = busyUntil - now();
    const next = visible && contextAvailable && (continuous || !settled || dragging || remaining > 0);
    if (next !== running) { running = next; (next ? resume : pause)(); }
    if (next && !continuous && settled && !dragging) timer = setTimer(reconcile, Math.max(1, remaining));
  }
  return {
    setVisible(value) { visible = value; reconcile(); },
    setContinuous(value) { continuous = value; reconcile(); },
    setSettled(value) { if (settled !== value) { settled = value; reconcile(); } },
    setDragging(value) { dragging = value; reconcile(); },
    setContextAvailable(value) { contextAvailable = value; reconcile(); },
    invalidate(duration = 100) { busyUntil = Math.max(busyUntil, now() + duration); reconcile(); },
    isRunning: () => running === true,
    snapshot: () => ({ visible, contextAvailable, continuous, settled, dragging, busyFor: Math.max(0, busyUntil - now()) }),
    destroy() { destroyed = true; clearTimer(timer); running = false; pause(); },
  };
}
