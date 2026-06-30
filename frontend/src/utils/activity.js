// Builds a GitHub-style heatmap structure from a sparse {YYYY-MM-DD: count} map.
// Output: { weeks:[[cell|null ×7]…], months:[{i,label}], total, days }
//   cell = { c: count, t: "Jun 4" }.  Columns are weeks, Sunday-first.

const DAY_MS = 86400000;
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

  const start = new Date(today.getTime() - weeksBack * 7 * DAY_MS);
  start.setDate(start.getDate() - start.getDay()); // back to the week's Sunday

  const weeks = [];
  const months = [];
  let total = 0;
  let days = 0;
  let lastMonth = -1;

  let cur = new Date(start);
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

    cur = new Date(cur.getTime() + DAY_MS);
  }

  return { weeks, months, total, days };
}
