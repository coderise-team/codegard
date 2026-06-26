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
  return (
    <div className="dash" data-density="compact">
      <Sidebar user={data.user} />

      <div className="main">
        <Navbar user={data.user} title="Dashboard" />

        <div className="canvas scroll">
          <div className="canvas-in">
            <div className="hello">
              <h1>Welcome back, <b>{data.user.handle}</b></h1>
            </div>

            <div className="lay-swap">
              <div className="top-band">
                <ProfileCard />
                <ContestHero />
              </div>

              <StatsStrip />

              <div className="cols">
                <div className="col-main">
                  <Recommended />
                  <RecentSubmissions />
                  <ActivityHeatmap />
                </div>
                <div className="col-rail">
                  <DailyChallenge />
                  <UpcomingContests />
                  <PastContests />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
