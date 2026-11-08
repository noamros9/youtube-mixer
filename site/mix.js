// Fisher-Yates shuffle (copy).
export function shuffle(xs, rand = Math.random) {
  const a = [...xs];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// Variety first: deal videos round-robin across channels (random channel order,
// random video order within each channel), so no prolific channel takes over.
export function mix(videos, channelOf, rand = Math.random) {
  const byChannel = new Map();
  for (const v of shuffle(videos, rand)) {
    const c = channelOf(v);
    if (!byChannel.has(c)) byChannel.set(c, []);
    byChannel.get(c).push(v);
  }
  let queues = shuffle([...byChannel.values()], rand);
  const out = [];
  while (queues.length) {
    for (const q of queues) out.push(q.pop());
    queues = queues.filter(q => q.length);
  }
  return out;
}
