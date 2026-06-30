// Builds a GitHub-style heatmap structure from a sparse {YYYY-MM-DD: count} map.
// Output: { weeks:[[cell|null ×7]…], months:[{i,label}], total, days }
//   cell = { c: count, t: "Jun 4" }.  Columns are weeks, Sunday-first.

const MONTHS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
];

const pad = (n) => String(n).padStart(2, '0');
const isoDate = (d) =>
  `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

export function buildHeatmap(counts, weeksBack = 52) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Step by calendar days (setDate), never by a fixed 24h: a fixed-ms day drifts
  // across DST transitions (a 25h fall-back day lands the cursor at 23:00, so the
  // same Sunday is detected twice and a week column comes out a cell short).
  const start = new Date(today);
  start.setDate(start.getDate() - weeksBack * 7);
  start.setDate(start.getDate() - start.getDay()); // back to the week's Sunday

  const weeks = [];
  const months = [];
  let total = 0;
  let days = 0;
  let lastMonth = -1;

  const cur = new Date(start);
  while (cur <= today || cur.getDay() !== 0) {
    // Start a new column every Sunday; label it if a new month begins here.
    if (cur.getDay() === 0) {
      weeks.push([]);
      const month = cur.getMonth();
      if (month !== lastMonth && cur.getDate() <= 7) {
        months.push({ i: weeks.length - 1, label: MONTHS[month] });
        lastMonth = month;
      }
    }

    const week = weeks[weeks.length - 1];
    let cell = null;
    if (cur <= today) {
      const c = counts[isoDate(cur)] || 0;
      if (c > 0) {
        total += c;
        days += 1;
      }
      cell = { c, t: `${MONTHS[cur.getMonth()]} ${cur.getDate()}` };
    }
    week.push(cell);

    cur.setDate(cur.getDate() + 1);
  }

  return { weeks, months, total, days };
}
