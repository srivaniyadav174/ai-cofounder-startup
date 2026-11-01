import { useContext } from 'react';
import {
  Routes,
  Route,
  Navigate,
  Link,
  NavLink,
  Outlet,
} from 'react-router-dom';

import {
  LayoutDashboard,
  Lightbulb,
  FlaskConical,
  Boxes,
  TrendingUp,
  Bot,
  Settings as SettingsIcon,
  LogOut,
  Sparkles,
  ArrowUpRight,
  ChevronRight,
  Rocket,
  CircleHelp,
  UserRound,
  ShieldCheck,
  SlidersHorizontal,
} from 'lucide-react';

import { AuthContext } from './context/AuthContext';

import Validation from './pages/Validation';
import MVPPlanner from './pages/MVPPlanner';
import Growth from './pages/Growth';
import Opportunities from './pages/Opportunities';
import Assistant from './pages/Assistant';
import Login from './pages/Login';
import Register from './pages/Register';

import ProgressTracker from './components/ProgressTracker';


/* Read saved plans and calculate actual statistics */
function getSavedPlanStats() {
  const mvp = localStorage.getItem('mvpPlan') || '';
  const growth = localStorage.getItem('growthPlan') || '';

  const countItems = (text, heading) => {
    const lines = text.split('\n');
    let active = false;
    let count = 0;

    for (const line of lines) {
      const clean = line
        .replace(/^#+\s*/, '')
        .replace(/\*\*/g, '')
        .replace(/__/g, '')
        .trim()
        .replace(/:$/, '')
        .toLowerCase();

      if (clean === heading.toLowerCase()) {
        active = true;
        continue;
      }

      if (active && /^#{1,6}\s/.test(line.trim())) {
        break;
      }

      if (active && /^[-*•]\s+/.test(line.trim())) {
        count++;
      }
    }

    return count;
  };

  return {
    mvpSaved: Boolean(mvp.trim()),
    growthSaved: Boolean(growth.trim()),

    mustHave: countItems(mvp, 'Must-Have'),
    shouldHave: countItems(mvp, 'Should-Have'),
    later: countItems(mvp, 'Later'),

    acquisition: countItems(
      growth,
      'Customer Acquisition Channels'
    ),

    experiments: countItems(
      growth,
      'Marketing Experiments'
    ),

    retention: countItems(
      growth,
      'Customer Retention'
    ),

    metrics: countItems(
      growth,
      'Key Metrics'
    ),
  };
}


/* Protect dashboard pages */
function ProtectedRoute() {
  const { token } = useContext(AuthContext);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}


/* Dashboard layout */
function DashboardLayout() {
  const { logout, user, userLoading, userError } = useContext(AuthContext);

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard, number: '01' },
    { name: 'Opportunities', path: '/opportunities', icon: Lightbulb, number: '02' },
    { name: 'Validation Lab', path: '/validation', icon: FlaskConical, number: '03' },
    { name: 'MVP Planner', path: '/mvp', icon: Boxes, number: '04' },
    { name: 'Growth Strategy', path: '/growth', icon: TrendingUp, number: '05' },
    { name: 'AI Co-Founder', path: '/assistant', icon: Bot, number: '06' },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link to="/dashboard" className="brand">
          <span className="brand-icon">
            <Sparkles size={22} />
          </span>

          <span>
            <strong>AI Co-Founder</strong>
            <small>STARTUP INTELLIGENCE STUDIO</small>
          </span>
        </Link>

        <p className="sidebar-label">STARTUP WORKSPACE</p>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/dashboard'}
                className={({ isActive }) =>
                  `nav-item${isActive ? ' active' : ''}`
                }
              >
                <Icon size={18} />
                <span>{item.name}</span>
                <small>{item.number}</small>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="ai-partner-card">
            <div className="ai-partner-icon">
              <Sparkles size={18} />
            </div>

            <strong>Build with clarity</strong>

            <p>
              Turn your idea into a validated, focused startup.
            </p>

            <Link to="/assistant" className="ai-partner-link">
              Ask your AI co-founder <span>→</span>
            </Link>
          </div>

          <Link to="/settings" className="nav-item">
            <SettingsIcon size={18} />
            <span>Settings</span>
          </Link>

          <button
            type="button"
            className="nav-item sign-out-button"
            onClick={logout}
          >
            <LogOut size={18} />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-context">
            <span className="topbar-dot" />

            <strong>
              {user ? `Hi, ${user.name}` : 'Founder workspace'}
            </strong>

            <span className="topbar-divider">/</span>

            <span className="topbar-subtitle">
              Your startup journey, organized
            </span>
          </div>

          <div className="topbar-right">
            <span
              className={`workspace-status ${
                userError ? 'status-error' : ''
              }`}
            >
              <span />

              {userLoading
                ? 'Checking account'
                : userError
                  ? 'Connection issue'
                  : user
                    ? 'Account verified'
                    : 'Not signed in'}
            </span>

            <div className="user-avatar">
              {user?.name?.trim()?.charAt(0)?.toUpperCase() || (
                <UserRound size={16} />
              )}
            </div>
          </div>
        </header>

        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}


/* Dashboard overview */
function Overview() {
  const { user, showGreeting } = useContext(AuthContext);

  const stats = getSavedPlanStats();

  const mvpTotal =
    stats.mustHave + stats.shouldHave + stats.later;

  const growthTotal =
    stats.acquisition +
    stats.experiments +
    stats.retention +
    stats.metrics;

  const workflow = [
    {
      number: '01',
      title: 'Discover opportunities',
      description: 'Explore problems worth solving and find a startup direction.',
      path: '/opportunities',
      icon: Lightbulb,
      tag: 'IDEATION',
      tone: 'amber',
    },
    {
      number: '02',
      title: 'Validate your idea',
      description: 'Turn assumptions into experiments and collect real-world evidence.',
      path: '/validation',
      icon: FlaskConical,
      tag: 'RESEARCH',
      tone: 'blue',
    },
    {
      number: '03',
      title: 'Plan your MVP',
      description: 'Prioritize the smallest useful product and map the build.',
      path: '/mvp',
      icon: Boxes,
      tag: 'BUILD',
      tone: 'violet',
    },
    {
      number: '04',
      title: 'Grow your startup',
      description: 'Create a practical plan to reach and retain early customers.',
      path: '/growth',
      icon: TrendingUp,
      tag: 'LAUNCH',
      tone: 'green',
    },
  ];

  return (
    <div className="dashboard-page">

      {/* Welcome hero */}
      <section className="welcome-hero">
        <div className="hero-copy">
          <div className="hero-kicker">
            <Sparkles size={14} /> YOUR AI-POWERED STARTUP STUDIO
          </div>

          {showGreeting && user?.name ? (
            <h1 className="personal-greeting">
              Hi, {user.name}
              <br />
              <span>let's build your idea.</span>
            </h1>
          ) : (
            <h1>
              From bold idea
              <br />
              <span>to real business.</span>
            </h1>
          )}

          <p>
            Your AI co-founder helps you explore, validate, build, and grow—with
            a clear next step at every stage.
          </p>

          <div className="hero-actions">
            <Link to="/opportunities" className="hero-primary">
              <Rocket size={17} /> Start building <ArrowUpRight size={16} />
            </Link>

            <Link to="/assistant" className="hero-secondary">
              Talk to AI co-founder <ChevronRight size={16} />
            </Link>
          </div>
        </div>

        <div
          className="founder-scene"
          aria-label="Illustration of a startup team planning together"
        >
          <div className="scene-window">
            <span />
            <span />
            <span />
          </div>

          <div className="scene-board">
            <b>BIG IDEAS</b>
            <i />
            <i />
            <i />
            <small>PLAN · TEST · BUILD</small>
          </div>

          <div className="scene-team">
            <div className="scene-person person-one">
              <span className="person-hair" />
              <span className="person-face" />
              <span className="person-body" />
            </div>

            <div className="scene-person person-two">
              <span className="person-hair" />
              <span className="person-face" />
              <span className="person-body" />
            </div>

            <div className="scene-person person-three">
              <span className="person-hair" />
              <span className="person-face" />
              <span className="person-body" />
            </div>
          </div>

          <div className="scene-table">
            <span className="scene-laptop" />
            <span className="scene-cup" />
            <span className="scene-note note-a" />
            <span className="scene-note note-b" />
          </div>

          <div className="scene-caption">
            <span className="scene-caption-dot" />
            YOUR NEXT BIG THING <b>01 — 04</b>
          </div>
        </div>
      </section>


      {/* Startup workflow */}
      <section className="overview-section">
        <div className="section-heading">
          <div>
            <span className="section-eyebrow">THE WORKFLOW</span>
            <h2>Your startup, step by step</h2>
          </div>

          <span className="section-side-note">
            A clear path from idea to launch
          </span>
        </div>

        <div className="workflow-grid">
          {workflow.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                to={item.path}
                className="workflow-card"
                key={item.number}
              >
                <div className="workflow-card-top">
                  <span className="workflow-number">{item.number}</span>

                  <span className={`workflow-icon ${item.tone}`}>
                    <Icon size={19} />
                  </span>
                </div>

                <span className="workflow-tag">{item.tag}</span>

                <h3>{item.title}</h3>

                <p>{item.description}</p>

                <div className="workflow-link">
                  Open workspace <ArrowUpRight size={15} />
                </div>
              </Link>
            );
          })}
        </div>
      </section>


      {/* Startup Progress Tracker */}
      <section className="overview-section">
        <div className="section-heading">
          <div>
            <span className="section-eyebrow">STARTUP PROGRESS</span>
            <h2>Your project completion</h2>
          </div>

          <span className="section-side-note">
            Track completed and remaining tasks
          </span>
        </div>

        <ProgressTracker />
      </section>


      {/* Founder signals */}
      <section className="founder-insights">
        <div className="section-heading insight-heading">
          <div>
            <span className="section-eyebrow">FOUNDER SIGNALS</span>
            <h2>See your startup at a glance</h2>
          </div>

          <span className="section-side-note">
            Evidence first · no invented success scores
          </span>
        </div>

        <div className="insight-dashboard-grid">

          {/* Startup journey */}
          <article className="signal-card signal-main-card">
            <div className="signal-card-head">
              <div>
                <span className="signal-label">YOUR STARTUP JOURNEY</span>
                <h3>From idea to evidence</h3>
              </div>

              <span className="signal-badge">
                <span /> Workspace overview
              </span>
            </div>

            <div
              className="journey-visual"
              role="img"
              aria-label="Startup workflow from idea to validation, MVP, and growth"
            >
              <div className="journey-line">
                <span className="journey-progress" />
              </div>

              <div className="journey-step active">
                <span className="journey-node">
                  <Lightbulb size={17} />
                </span>
                <strong>Idea</strong>
                <small>Explore</small>
              </div>

              <div className="journey-step">
                <span className="journey-node">
                  <FlaskConical size={17} />
                </span>
                <strong>Validate</strong>
                <small>Gather evidence</small>
              </div>

              <div className="journey-step">
                <span className="journey-node">
                  <Boxes size={17} />
                </span>
                <strong>Build</strong>
                <small>Plan MVP</small>
              </div>

              <div className="journey-step">
                <span className="journey-node">
                  <TrendingUp size={17} />
                </span>
                <strong>Grow</strong>
                <small>Reach customers</small>
              </div>
            </div>

            <div className="signal-note">
              <CircleHelp size={15} />
              Complete each stage to turn assumptions into measurable signals.
            </div>
          </article>


          {/* Validation framework */}
          <article className="signal-card signal-chart-card">
            <div className="signal-card-head">
              <div>
                <span className="signal-label">VALIDATION FRAMEWORK</span>
                <h3>What to measure</h3>
              </div>

              <span className="chart-chip">4 signals</span>
            </div>

            <div
              className="signal-bars"
              aria-label="Four validation dimensions awaiting evidence"
            >
              <div className="signal-bar-row">
                <span>Problem</span>
                <div className="signal-track">
                  <i className="bar-purple" />
                </div>
                <b>—</b>
              </div>

              <div className="signal-bar-row">
                <span>Demand</span>
                <div className="signal-track">
                  <i className="bar-blue" />
                </div>
                <b>—</b>
              </div>

              <div className="signal-bar-row">
                <span>Pricing</span>
                <div className="signal-track">
                  <i className="bar-orange" />
                </div>
                <b>—</b>
              </div>

              <div className="signal-bar-row">
                <span>Competition</span>
                <div className="signal-track">
                  <i className="bar-green" />
                </div>
                <b>—</b>
              </div>
            </div>

            <p className="chart-footnote">
              Evidence scores appear after you record real experiment results.
            </p>
          </article>

        </div>


        {/* Saved plans statistics */}
        <div className="section-heading insight-heading">
          <div>
            <span className="section-eyebrow">YOUR SAVED WORK</span>
            <h2>Plans & priorities</h2>
          </div>

          <span className="section-side-note">
            Counts from your saved AI-generated plans
          </span>
        </div>

        <div className="insight-dashboard-grid">

          {/* MVP plan */}
          <article className="signal-card signal-chart-card">
            <div className="signal-card-head">
              <div>
                <span className="signal-label">MVP PLANNER</span>
                <h3>Product priorities</h3>
              </div>

              <span className="chart-chip">
                {stats.mvpSaved ? `${mvpTotal} items` : 'Not saved'}
              </span>
            </div>

            {stats.mvpSaved ? (
              <>
                <div className="signal-bars">
                  <div className="signal-bar-row">
                    <span>Must-Have</span>
                    <div className="signal-track">
                      <i
                        className="bar-purple"
                        style={{
                          width: `${mvpTotal ? (stats.mustHave / mvpTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <b>{stats.mustHave}</b>
                  </div>

                  <div className="signal-bar-row">
                    <span>Should-Have</span>
                    <div className="signal-track">
                      <i
                        className="bar-blue"
                        style={{
                          width: `${mvpTotal ? (stats.shouldHave / mvpTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <b>{stats.shouldHave}</b>
                  </div>

                  <div className="signal-bar-row">
                    <span>Later</span>
                    <div className="signal-track">
                      <i
                        className="bar-orange"
                        style={{
                          width: `${mvpTotal ? (stats.later / mvpTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <b>{stats.later}</b>
                  </div>
                </div>

                <p className="chart-footnote">
                  {mvpTotal} saved feature priorities across your MVP plan.
                </p>
              </>
            ) : (
              <div className="signal-note">
                <CircleHelp size={15} />
                Generate and save your MVP plan to see feature priorities here.
              </div>
            )}

            <Link to="/mvp" className="workflow-link">
              Open MVP Planner <ArrowUpRight size={15} />
            </Link>
          </article>


          {/* Growth plan */}
          <article className="signal-card signal-chart-card">
            <div className="signal-card-head">
              <div>
                <span className="signal-label">GROWTH STRATEGY</span>
                <h3>Growth activities</h3>
              </div>

              <span className="chart-chip">
                {stats.growthSaved ? `${growthTotal} items` : 'Not saved'}
              </span>
            </div>

            {stats.growthSaved ? (
              <>
                <div className="signal-bars">
                  <div className="signal-bar-row">
                    <span>Acquisition</span>
                    <div className="signal-track">
                      <i
                        className="bar-purple"
                        style={{
                          width: `${growthTotal ? (stats.acquisition / growthTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <b>{stats.acquisition}</b>
                  </div>

                  <div className="signal-bar-row">
                    <span>Experiments</span>
                    <div className="signal-track">
                      <i
                        className="bar-blue"
                        style={{
                          width: `${growthTotal ? (stats.experiments / growthTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <b>{stats.experiments}</b>
                  </div>

                  <div className="signal-bar-row">
                    <span>Retention</span>
                    <div className="signal-track">
                      <i
                        className="bar-green"
                        style={{
                          width: `${growthTotal ? (stats.retention / growthTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <b>{stats.retention}</b>
                  </div>

                  <div className="signal-bar-row">
                    <span>Key Metrics</span>
                    <div className="signal-track">
                      <i
                        className="bar-orange"
                        style={{
                          width: `${growthTotal ? (stats.metrics / growthTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <b>{stats.metrics}</b>
                  </div>
                </div>

                <p className="chart-footnote">
                  {growthTotal} saved growth activities across your strategy.
                </p>
              </>
            ) : (
              <div className="signal-note">
                <CircleHelp size={15} />
                Generate and save your growth strategy to see activities here.
              </div>
            )}

            <Link to="/growth" className="workflow-link">
              Open Growth Strategy <ArrowUpRight size={15} />
            </Link>
          </article>

        </div>
      </section>


      {/* Bottom guidance */}
      <section className="bottom-insight">
        <div className="insight-icon">
          <CircleHelp size={20} />
        </div>

        <div>
          <strong>Not sure where to begin?</strong>
          <p>
            Share your idea with your AI co-founder and get a practical
            recommendation for your next move.
          </p>
        </div>

        <Link to="/assistant">
          Get guidance <ChevronRight size={16} />
        </Link>
      </section>

    </div>
  );
}


/* Settings page */
function SettingsPage() {
  const {
    user,
    userLoading,
    userError,
    showGreeting,
    updateShowGreeting,
    logout,
  } = useContext(AuthContext);

  return (
    <div className="settings-page dashboard-page">
      <div className="settings-heading">
        <div>
          <span className="section-eyebrow">PERSONALIZE YOUR SPACE</span>
          <h1>Settings</h1>
          <p>Manage your account display and session.</p>
        </div>

        <div className="settings-heading-icon">
          <SlidersHorizontal size={22} />
        </div>
      </div>

      <section className="settings-card">
        <div className="settings-card-heading">
          <span className="settings-icon">
            <UserRound size={18} />
          </span>

          <div>
            <h2>Account profile</h2>
            <p>Your signed-in account details</p>
          </div>
        </div>

        <div className="settings-profile">
          <div className="settings-avatar">
            {user?.name?.trim()?.charAt(0)?.toUpperCase() || 'U'}
          </div>

          <div>
            <strong>
              {userLoading
                ? 'Loading profile…'
                : user?.name || 'Account name unavailable'}
            </strong>

            <span>
              {user?.email ||
                (userError ? 'Could not verify account' : '—')}
            </span>
          </div>

          <span
            className={`settings-pill ${
              userError ? 'settings-pill-error' : ''
            }`}
          >
            <span />

            {userLoading
              ? 'Checking'
              : userError
                ? 'Unavailable'
                : 'Verified'}
          </span>
        </div>
      </section>

      <section className="settings-card">
        <div className="settings-card-heading">
          <span className="settings-icon">
            <Sparkles size={18} />
          </span>

          <div>
            <h2>Dashboard preferences</h2>
            <p>Choose what you see when you open your workspace</p>
          </div>
        </div>

        <label className="settings-toggle-row">
          <span>
            <strong>Personal greeting</strong>
            <small>
              Show your name on the dashboard welcome section.
            </small>
          </span>

          <input
            type="checkbox"
            checked={showGreeting}
            onChange={(event) =>
              updateShowGreeting(event.target.checked)
            }
          />
        </label>
      </section>

      <section className="settings-card">
        <div className="settings-card-heading">
          <span className="settings-icon">
            <ShieldCheck size={18} />
          </span>

          <div>
            <h2>Session & security</h2>
            <p>Sign out of this account on this browser</p>
          </div>
        </div>

        <div className="settings-session-row">
          <div>
            <strong>Current session</strong>
            <span>
              {userError
                ? 'Account verification failed'
                : userLoading
                  ? 'Verifying your session'
                  : 'Signed in to AI Co-Founder'}
            </span>
          </div>

          <button
            type="button"
            className="settings-signout"
            onClick={logout}
          >
            Sign out
          </button>
        </div>
      </section>

      <p className="settings-footnote">
        AI Co-Founder for Startups · Your account details are read from the
        connected backend.
      </p>
    </div>
  );
}


/* Application routes */
function App() {
  const { token } = useContext(AuthContext);

  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          token
            ? <Navigate to="/dashboard" replace />
            : <Login />
        }
      />

      <Route
        path="/register"
        element={
          token
            ? <Navigate to="/dashboard" replace />
            : <Register />
        }
      />

      {/* Protected dashboard routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Overview />} />
          <Route path="/opportunities" element={<Opportunities />} />
          <Route path="/validation" element={<Validation />} />
          <Route path="/mvp" element={<MVPPlanner />} />
          <Route path="/growth" element={<Growth />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>

      {/* Default routes */}
      <Route
        path="/"
        element={
          <Navigate
            to={token ? '/dashboard' : '/login'}
            replace
          />
        }
      />

      <Route
        path="*"
        element={
          <Navigate
            to={token ? '/dashboard' : '/login'}
            replace
          />
        }
      />
    </Routes>
  );
}

export default App;