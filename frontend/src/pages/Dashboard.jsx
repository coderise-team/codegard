import React, { useState, useEffect } from 'react';
import Sidebar from '../components/layout/Sidebar';
import Navbar from '../components/layout/Navbar';
import ProfileCard from '../components/dashboard/ProfileCard';
import ContestHero from '../components/dashboard/ContestHero';
import StatsStrip from '../components/dashboard/StatsStrip';
import Recommended from '../components/dashboard/Recommended';
import RecentSubmissions from '../components/dashboard/RecentSubmissions';
import ActivityHeatmap from '../components/dashboard/ActivityHeatmap';
import DailyChallenge from '../components/dashboard/DailyChallenge';
import UpcomingContests from '../components/dashboard/UpcomingContests';
import PastContests from '../components/dashboard/PastContests';
import './Dashboard.css';

/**
 * Dashboard — main page (SWAP layout, compact density, violet accent).
 *
 * Props:
 *   data — CODEGARD_HOME object (mock data or real API response)
 *
 * Example with React Router:
 *   <Route path="/dashboard" element={<Dashboard data={homeData} />} />
 */
export default function Dashboard({ data }) {
  const [activeNav, setActiveNav] = useState('home');

  // Contest state. Mock value is 'soon'; in production the backend
  // derives this from contest start/end timestamps. 'live' | 'soon' | 'none'.
  const contestState = 'soon';

  // Live countdown — tick both the live clock and the time-to-start.
  const [remaining, setRemaining] = useState(data.contest.remaining);
  const [startsIn, setStartsIn] = useState(data.contest.startsIn);
  useEffect(() => {
    const id = setInterval(() => {
      setRemaining((s) => (s > 0 ? s - 1 : 0));
      setStartsIn((s) => (s > 0 ? s - 1 : 0));
    }, 1000);
    return () => clearInterval(id);
  }, []);

  // Registration state (hero CTA + upcoming rows).
  const [heroReg, setHeroReg] = useState(false);
  const [regMap, setRegMap] = useState({});
  const toggleReg = (i) =>
    setRegMap((m) => ({ ...m, [i]: !(m[i] ?? data.upcoming[i].registered) }));

  const contest = { ...data.contest, startsIn };

  return (
    <div className="dash" data-density="compact">
      <Sidebar
        nav={data.nav}
        navSub={data.navSub}
        user={data.user}
        activeId={activeNav}
        onNav={setActiveNav}
      />

      <div className="main">
        <Navbar user={data.user} title="Dashboard" />

        <div className="canvas scroll">
          <div className="canvas-in">
            <div className="hello">
              <h1>Welcome back, <b>{data.user.handle}</b></h1>
            </div>

            <div className="lay-swap">
              <div className="top-band">
                <ProfileCard user={data.user} ratingHistory={data.ratingHistory} />
                <ContestHero
                  contest={contest}
                  state={contestState}
                  remaining={remaining}
                  registered={heroReg}
                  onRegister={() => setHeroReg(true)}
                />
              </div>

              <StatsStrip stats={data.quickStats} />

              <div className="cols">
                <div className="col-main">
                  <Recommended items={data.recommended} />
                  <RecentSubmissions submissions={data.recentSubmissions} />
                  <ActivityHeatmap activity={data.activity} />
                </div>
                <div className="col-rail">
                  <DailyChallenge daily={data.daily} />
                  <UpcomingContests contests={data.upcoming} regMap={regMap} onToggleReg={toggleReg} />
                  <PastContests items={data.pastContests} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
