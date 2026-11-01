
import { useState } from 'react';
import {
  FlaskConical,
  Sparkles,
  LoaderCircle,
  Target,
  Users,
  CheckCircle2,
  Save,
  Search,
  Lightbulb,
  ArrowRight,
} from 'lucide-react';
import client from '../api/client';

export default function Validation() {
  const [idea, setIdea] = useState('');
  const [customers, setCustomers] = useState('');
  const [problem, setProblem] = useState('');
  const [startupId, setStartupId] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [progressStage, setProgressStage] = useState(0);
  const [savingIds, setSavingIds] = useState([]);

  const journeyStages = [
    {
      title: 'Shape the idea',
      detail: 'Capture the startup and customer context',
      icon: Target,
    },
    {
      title: 'Generate experiments',
      detail: 'Turn assumptions into testable actions',
      icon: Search,
    },
    {
      title: 'Review the plan',
      detail: 'Load experiments you can run and record',
      icon: Lightbulb,
    },
  ];

  // Sync validation progress with the Dashboard.
  function syncValidationProgress(items) {
    localStorage.setItem(
      'validationExperiments',
      JSON.stringify(items)
    );

    window.dispatchEvent(
      new Event('startupProgressUpdated')
    );
  }

  async function generatePlan(event) {
    event.preventDefault();

    if (loading) return;

    setLoading(true);
    setProgressStage(0);
    setError('');

    try {
      let currentStartupId = startupId;

      if (!currentStartupId) {
        const startupResponse = await client.post('/startups/', {
          name: idea.trim().slice(0, 150),
          description: [
            idea.trim(),
            problem.trim()
              ? `Problem: ${problem.trim()}`
              : '',
          ]
            .filter(Boolean)
            .join('\n\n'),
          industry: null,
          stage: 'Idea',
          target_market: customers.trim() || null,
          business_model: null,
        });

        currentStartupId = startupResponse.data.id;
        setStartupId(currentStartupId);
      }

      setProgressStage(1);

      try {
        await client.post(
          `/validation/${currentStartupId}/generate`
        );
      } catch (generationError) {
        if (generationError.response?.status !== 409) {
          throw generationError;
        }
      }

      setProgressStage(2);

      const experimentsResponse = await client.get(
        `/validation/${currentStartupId}/experiments`
      );

      const data = experimentsResponse.data;

      const savedExperiments = Array.isArray(data)
        ? data
        : Array.isArray(data?.experiments)
          ? data.experiments
          : [];

      setExperiments(savedExperiments);

      // Automatically update Dashboard progress.
      syncValidationProgress(savedExperiments);

      setProgressStage(3);

      if (savedExperiments.length === 0) {
        setError(
          'No experiments were returned by the backend.'
        );
      }
    } catch (err) {
      console.error('Validation generation failed:', err);

      if (err.response?.status === 401) {
        setError(
          'Your session may have expired. Please log in again.'
        );
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        setError(
          typeof detail === 'string'
            ? detail
            : JSON.stringify(detail)
        );
      } else if (!err.response) {
        setError(
          'Cannot reach the backend. Check that FastAPI is running.'
        );
      } else {
        setError(
          `Request failed (${err.response.status}).`
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function updateExperiment(experimentId, field, value) {
    setExperiments((current) =>
      current.map((experiment) =>
        experiment.id === experimentId
          ? { ...experiment, [field]: value }
          : experiment
      )
    );
  }

  async function saveExperiment(experiment) {
    if (savingIds.includes(experiment.id)) return;

    setSavingIds((current) => [
      ...current,
      experiment.id,
    ]);

    setError('');

    try {
      const response = await client.put(
        `/validation/experiments/${experiment.id}`,
        {
          status: experiment.status || 'PLANNED',
          result: experiment.result || '',
          learning: experiment.learning || '',
          next_action: experiment.next_action || '',
        }
      );

      // Use the edited experiment as the base so its values
      // remain available even if the API returns partial data.
      const updatedExperiment = {
        ...experiment,
        ...(response.data || {}),
      };

      const updatedExperiments = experiments.map((item) =>
        item.id === experiment.id
          ? updatedExperiment
          : item
      );

      setExperiments(updatedExperiments);

      // Persist the latest saved experiments.
      syncValidationProgress(updatedExperiments);
    } catch (err) {
      console.error('Saving experiment failed:', err);

      if (err.response?.status === 401) {
        setError(
          'Your session may have expired. Please log in again.'
        );
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        setError(
          typeof detail === 'string'
            ? detail
            : JSON.stringify(detail)
        );
      } else if (!err.response) {
        setError(
          'Cannot reach the backend. Check that FastAPI is running.'
        );
      } else {
        setError(
          `Could not save experiment (${err.response.status}).`
        );
      }
    } finally {
      setSavingIds((current) =>
        current.filter((id) => id !== experiment.id)
      );
    }
  }

  return (
    <main className="main-content">
      <header className="topbar">
        <div>
          <div className="breadcrumb">
            Workspace <span>/</span> Validation Lab
          </div>
          <h1>Validation Lab</h1>
        </div>
      </header>

      <section
        className={`validation-journey ${
          loading ? 'is-running' : ''
        }`}
        aria-live="polite"
      >
        <div className="validation-journey-copy">
          <span className="validation-eyebrow">
            <Sparkles size={14} /> IDEA → EVIDENCE
          </span>

          <h2>
            {loading
              ? 'Your idea is moving through validation'
              : experiments.length
                ? 'Your validation map is ready'
                : 'See your idea from a new angle'}
          </h2>

          <p>
            {loading
              ? 'Follow the real steps as your workspace prepares the experiment plan.'
              : experiments.length
                ? 'Your experiment plan is loaded. Open a card, run the test, and save what you learn.'
                : 'Turn assumptions into experiments, then use real results to decide what to build next.'}
          </p>
        </div>

        <div
          className="validation-journey-map"
          aria-label="Validation workflow"
        >
          <div className="validation-map-lines">
            <span />
            <span />
          </div>

          {journeyStages.map((stage, index) => {
            const Icon = stage.icon;

            const done =
              progressStage > index ||
              (!loading && experiments.length > 0);

            const active =
              loading && progressStage === index;

            return (
              <div
                className={`validation-map-node ${
                  done ? 'is-done' : ''
                } ${active ? 'is-active' : ''}`}
                key={stage.title}
              >
                <div className="validation-node-icon">
                  {done ? (
                    <CheckCircle2 size={18} />
                  ) : (
                    <Icon size={18} />
                  )}
                </div>

                <div className="validation-node-text">
                  <strong>{stage.title}</strong>
                  <small>{stage.detail}</small>
                </div>

                {index < journeyStages.length - 1 && (
                  <ArrowRight
                    className="validation-node-arrow"
                    size={15}
                  />
                )}
              </div>
            );
          })}
        </div>

        {loading && (
          <div className="validation-live-status">
            <span className="validation-live-dot" />

            {progressStage === 0
              ? 'Preparing your startup context…'
              : progressStage === 1
                ? 'Generating experiments…'
                : 'Loading your experiment plan…'}
          </div>
        )}
      </section>

      <section style={panelStyle}>
        <div style={headingStyle}>
          <div style={iconStyle}>
            <FlaskConical size={26} />
          </div>

          <div>
            <h2 style={{ margin: 0 }}>
              Test before you build
            </h2>

            <p
              style={{
                color: '#6b7280',
                marginBottom: 0,
              }}
            >
              Turn your assumptions into experiments and learn
              from potential customers before investing money.
            </p>
          </div>
        </div>

        <form onSubmit={generatePlan} style={{ marginTop: 28 }}>
          <label style={labelStyle}>
            <Target size={16} /> What's your startup idea?
          </label>

          <textarea
            value={idea}
            onChange={(event) =>
              setIdea(event.target.value)
            }
            placeholder="Describe the product or service you want to build..."
            rows={3}
            required
            disabled={Boolean(startupId)}
            style={fieldStyle}
          />

          <label style={labelStyle}>
            <Users size={16} /> Who are your target customers?
          </label>

          <textarea
            value={customers}
            onChange={(event) =>
              setCustomers(event.target.value)
            }
            placeholder="For example: local shop owners, college students, freelancers..."
            rows={2}
            disabled={Boolean(startupId)}
            style={fieldStyle}
          />

          <label style={labelStyle}>
            <CheckCircle2 size={16} /> What problem will you solve?
          </label>

          <textarea
            value={problem}
            onChange={(event) =>
              setProblem(event.target.value)
            }
            placeholder="What difficulty do these customers experience?"
            rows={3}
            disabled={Boolean(startupId)}
            style={fieldStyle}
          />

          <button
            type="submit"
            disabled={loading || experiments.length > 0}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 10,
              width: '100%',
              marginTop: 22,
              padding: 14,
              border: 0,
              borderRadius: 12,
              color: 'white',
              background: loading ? '#9ca3af' : '#6d28d9',
              cursor: loading ? 'wait' : 'pointer',
              fontSize: 15,
              fontWeight: 600,
            }}
          >
            {loading ? (
              <>
                <LoaderCircle size={19} />
                Saving startup and generating experiments...
              </>
            ) : experiments.length > 0 ? (
              'Experiments generated'
            ) : (
              <>
                <Sparkles size={19} />
                Generate validation experiments
              </>
            )}
          </button>
        </form>

        {error && (
          <p
            role="alert"
            style={{
              color: '#b91c1c',
              background: '#fef2f2',
              padding: 12,
              borderRadius: 10,
              marginTop: 20,
            }}
          >
            {error}
          </p>
        )}

        {experiments.length > 0 && (
          <section
            aria-live="polite"
            className="validation-results-panel"
          >
            <div className="validation-results-heading">
              <div>
                <span className="validation-eyebrow">
                  <Sparkles size={14} /> GENERATED PLAN
                </span>

                <h2>Your validation experiments</h2>

                <p>
                  Run these with real customers. Record observations
                  and save each experiment to keep your evidence
                  in one place.
                </p>
              </div>

              <div className="validation-count">
                <strong>{experiments.length}</strong>
                <span>experiments</span>
              </div>
            </div>

            <div className="validation-experiment-grid">
              {experiments.map((experiment, index) => (
                <article
                  className="validation-experiment-card"
                  key={experiment.id ?? index}
                >
                  <div className="validation-experiment-card-top">
                    <span className="validation-experiment-number">
                      {String(index + 1).padStart(2, '0')}
                    </span>

                    <span
                      className={`validation-status status-${String(
                        experiment.status || 'planned'
                      ).toLowerCase()}`}
                    >
                      {String(
                        experiment.status || 'PLANNED'
                      ).replaceAll('_', ' ')}
                    </span>
                  </div>

                  <h3>{experiment.title}</h3>

                  {experiment.hypothesis && (
                    <p>
                      <strong>Hypothesis:</strong>{' '}
                      {experiment.hypothesis}
                    </p>
                  )}

                  {experiment.description && (
                    <p>
                      <strong>How to test:</strong>{' '}
                      {experiment.description}
                    </p>
                  )}

                  {experiment.success_criteria && (
                    <p>
                      <strong>Success criteria:</strong>{' '}
                      {experiment.success_criteria}
                    </p>
                  )}

                  <label style={labelStyle}>
                    Experiment status
                  </label>

                  <select
                    value={experiment.status || 'PLANNED'}
                    onChange={(event) =>
                      updateExperiment(
                        experiment.id,
                        'status',
                        event.target.value
                      )
                    }
                    style={fieldStyle}
                  >
                    <option value="PLANNED">Planned</option>
                    <option value="IN_PROGRESS">
                      In progress
                    </option>
                    <option value="COMPLETED">
                      Completed
                    </option>
                    <option value="CANCELLED">
                      Cancelled
                    </option>
                  </select>

                  <label style={labelStyle}>
                    Actual result
                  </label>

                  <textarea
                    value={experiment.result || ''}
                    onChange={(event) =>
                      updateExperiment(
                        experiment.id,
                        'result',
                        event.target.value
                      )
                    }
                    placeholder="What happened when you ran this experiment? Record real observations, numbers, and customer responses."
                    rows={3}
                    style={fieldStyle}
                  />

                  <label style={labelStyle}>
                    What did you learn?
                  </label>

                  <textarea
                    value={experiment.learning || ''}
                    onChange={(event) =>
                      updateExperiment(
                        experiment.id,
                        'learning',
                        event.target.value
                      )
                    }
                    placeholder="What did this experiment teach you about your assumptions?"
                    rows={3}
                    style={fieldStyle}
                  />

                  <label style={labelStyle}>
                    Next action
                  </label>

                  <textarea
                    value={experiment.next_action || ''}
                    onChange={(event) =>
                      updateExperiment(
                        experiment.id,
                        'next_action',
                        event.target.value
                      )
                    }
                    placeholder="What will you do next based on this result?"
                    rows={2}
                    style={fieldStyle}
                  />

                  <button
                    type="button"
                    disabled={savingIds.includes(experiment.id)}
                    onClick={() => saveExperiment(experiment)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 8,
                      width: '100%',
                      marginTop: 16,
                      padding: 12,
                      border: 0,
                      borderRadius: 10,
                      color: 'white',
                      background: savingIds.includes(
                        experiment.id
                      )
                        ? '#9ca3af'
                        : '#6d28d9',
                      cursor: savingIds.includes(
                        experiment.id
                      )
                        ? 'wait'
                        : 'pointer',
                      fontSize: 14,
                      fontWeight: 600,
                    }}
                  >
                    {savingIds.includes(experiment.id) ? (
                      <>
                        <LoaderCircle size={17} />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save size={17} />
                        Save experiment
                      </>
                    )}
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>

      <p
        style={{
          maxWidth: 900,
          margin: '12px auto',
          color: '#6b7280',
          fontSize: 13,
        }}
      >
        A validation plan helps you gather evidence. It cannot
        guarantee that a startup will succeed.
      </p>
    </main>
  );
}

const panelStyle = {
  maxWidth: 900,
  margin: '0 auto',
  width: '100%',
  background: 'white',
  border: '1px solid #e5e7eb',
  borderRadius: 20,
  padding: 24,
  boxSizing: 'border-box',
};

const headingStyle = {
  display: 'flex',
  gap: 12,
  alignItems: 'center',
};

const iconStyle = {
  padding: 12,
  background: '#ede9fe',
  color: '#6d28d9',
  borderRadius: 12,
};

const labelStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: 7,
  fontWeight: 600,
  margin: '18px 0 8px',
};

const fieldStyle = {
  width: '100%',
  boxSizing: 'border-box',
  padding: 13,
  border: '1px solid #d1d5db',
  borderRadius: 10,
  fontSize: 15,
  fontFamily: 'inherit',
};
