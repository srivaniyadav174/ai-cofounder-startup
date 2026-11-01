
import { useEffect, useState } from 'react';
import {
  CheckCircle2,
  Circle,
  Target,
  TrendingUp,
  FlaskConical,
  Boxes,
} from 'lucide-react';

const initialTasks = [
  {
    id: 'validation',
    title: 'Validate startup idea',
    category: 'Validation',
    icon: FlaskConical,
  },
  {
    id: 'mvp',
    title: 'Complete MVP plan',
    category: 'MVP',
    icon: Boxes,
  },
  {
    id: 'growth',
    title: 'Complete growth strategy',
    category: 'Growth',
    icon: TrendingUp,
  },
];

function getAutomaticTasks() {
  let validationCompleted = false;

  try {
    const experiments = JSON.parse(
      localStorage.getItem('validationExperiments') || '[]'
    );

    validationCompleted =
      Array.isArray(experiments) &&
      experiments.length > 0 &&
      experiments.every(
        (experiment) =>
          String(experiment.status || '').toUpperCase() ===
          'COMPLETED'
      );
  } catch {
    validationCompleted = false;
  }

  const mvpPlan = localStorage.getItem('mvpPlan') || '';
  const growthPlan = localStorage.getItem('growthPlan') || '';

  return [
    {
      ...initialTasks[0],
      completed: validationCompleted,
    },
    {
      ...initialTasks[1],
      completed: Boolean(mvpPlan.trim()),
    },
    {
      ...initialTasks[2],
      completed: Boolean(growthPlan.trim()),
    },
  ];
}

function ProgressTracker() {
  const [tasks, setTasks] = useState(getAutomaticTasks);

  useEffect(() => {
    function refreshProgress() {
      setTasks(getAutomaticTasks());
    }

    window.addEventListener('storage', refreshProgress);

    window.addEventListener(
      'startupProgressUpdated',
      refreshProgress
    );

    return () => {
      window.removeEventListener('storage', refreshProgress);

      window.removeEventListener(
        'startupProgressUpdated',
        refreshProgress
      );
    };
  }, []);

  const completed = tasks.filter(
    (task) => task.completed
  ).length;

  const total = tasks.length;

  const percentage =
    total > 0
      ? Math.round((completed / total) * 100)
      : 0;

  return (
    <section className="signal-card progress-tracker">
      <div className="signal-card-head">
        <div>
          <span className="signal-label">
            STARTUP PROGRESS
          </span>

          <h3>Your project journey</h3>
        </div>

        <span className="chart-chip">
          {percentage}% complete
        </span>
      </div>

      <div className="progress-summary">
        <div className="progress-number">
          {completed}
          <span> / {total} tasks</span>
        </div>

        <div
          className="progress-track"
          role="progressbar"
          aria-label="Startup task completion"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={percentage}
        >
          <div
            className="progress-fill"
            style={{
              width: `${percentage}%`,
            }}
          />
        </div>

        <p>
          {completed === total
            ? 'All listed tasks are completed.'
            : `${total - completed} tasks remaining`}
        </p>
      </div>

      <div className="progress-task-list">
        {tasks.map((task) => {
          const Icon = task.icon || Target;

          return (
            <div
              key={task.id}
              className={`progress-task ${
                task.completed ? 'completed' : ''
              }`}
            >
              <span className="progress-task-icon">
                <Icon size={17} />
              </span>

              <span className="progress-task-copy">
                <strong>{task.title}</strong>
                <small>{task.category}</small>
              </span>

              {task.completed ? (
                <CheckCircle2 size={20} />
              ) : (
                <Circle size={20} />
              )}
            </div>
          );
        })}
      </div>

      <p className="chart-footnote">
        Progress updates automatically when your plans are saved
        and validation experiments are completed.
      </p>
    </section>
  );
}

export default ProgressTracker;
