
import { useState } from 'react';
import {
  TrendingUp,
  Sparkles,
  LoaderCircle,
  Target,
  Users,
  ChartNoAxesCombined,
} from 'lucide-react';

import client from '../api/client';
import FormattedAIResult from '../components/FormattedAIResult';
import PlanVisuals from '../components/PlanVisuals';

function getGrowthMetrics(result) {
  if (!result || !result.trim()) {
    return [];
  }

  const sections = [
    {
      name: 'Acquisition',
      patterns: [
        /customer acquisition channels/i,
        /acquisition channels/i,
        /marketing channels/i,
      ],
    },
    {
      name: 'Experiments',
      patterns: [
        /marketing experiments/i,
        /low-cost experiments/i,
        /growth experiments/i,
      ],
    },
    {
      name: 'Retention',
      patterns: [
        /customer retention/i,
        /retention strategies/i,
        /retention plan/i,
      ],
    },
    {
      name: 'Metrics',
      patterns: [
        /key metrics/i,
        /success metrics/i,
        /measurable targets/i,
      ],
    },
  ];

  const lines = result.split(/\r?\n/);

  return sections.map((section) => {
    const headingIndex = lines.findIndex((line) => {
      const normalized = line
        .trim()
        .replace(/^#{1,6}\s*/, '')
        .replace(/\*\*/g, '')
        .replace(/__/g, '')
        .replace(/^\d+[.)]\s*/, '')
        .replace(/:$/, '')
        .trim();

      return section.patterns.some((pattern) =>
        pattern.test(normalized)
      );
    });

    if (headingIndex === -1) {
      return {
        name: section.name,
        value: 0,
      };
    }

    const followingSection = lines.findIndex(
      (line, index) =>
        index > headingIndex &&
        /^\s*#{1,6}\s+/.test(line)
    );

    const sectionLines = lines.slice(
      headingIndex + 1,
      followingSection === -1
        ? lines.length
        : followingSection
    );

    const bullets = sectionLines.filter((line) =>
      /^\s*[-*+]\s+\S/.test(line)
    );

    return {
      name: section.name,
      value: bullets.length,
    };
  });
}

export default function Growth() {
  const [idea, setIdea] = useState('');
  const [customers, setCustomers] = useState('');
  const [stage, setStage] = useState('Pre-launch');
  const [budget, setBudget] = useState('Low budget');

  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateStrategy = async (e) => {
    e.preventDefault();

    if (!idea.trim()) {
      setError('Please describe your startup idea.');
      return;
    }

    setLoading(true);
    setError('');
    setResult('');

    const prompt = `Act as an experienced startup growth strategist.

Create a practical, realistic growth strategy for this startup.

Startup idea: ${idea}
Target customers: ${customers || 'Not specified'}
Current stage: ${stage}
Marketing budget: ${budget}

Include:

1. Growth goal
2. Ideal customer profile
3. Three customer acquisition channels
4. A practical 30-day action plan
5. Low-cost marketing experiments
6. Customer retention strategies
7. Key metrics and measurable targets
8. Risks and ways to reduce them

IMPORTANT FORMATTING:
Use clear Markdown headings.
Use these headings exactly:
## Customer Acquisition Channels
## Marketing Experiments
## Customer Retention
## Key Metrics

Under each heading, provide individual bullet points.

For Key Metrics, include measurable targets where possible.
For the 30-day plan, organize activities by week.

Use clear headings, specific actions, and realistic recommendations.
Prioritize affordable actions.
Do not invent achieved results or actual customer statistics.
`;

    try {
      const response = await client.post(
        '/ai/chat',
        {
          messages: [
            {
              role: 'user',
              content: prompt,
            },
          ],
        },
        {
          timeout: 180000,
        }
      );

      const reply = response.data?.reply;

      const finalResult =
        typeof reply === 'string' && reply.trim()
          ? reply
          : 'The AI returned an empty response. Please try again.';

      // Update the current page.
      setResult(finalResult);

      // Save and notify Dashboard only for a valid AI response.
      if (typeof reply === 'string' && reply.trim()) {
        localStorage.setItem('growthPlan', finalResult);

        window.dispatchEvent(
          new Event('startupProgressUpdated')
        );
      }
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError(
          'The AI is taking too long. Please try again.'
        );
      } else {
        setError(
          err.response?.data?.detail ||
            err.response?.data?.message ||
            err.message ||
            'Could not generate the growth strategy. Please try again.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const growthMetrics = getGrowthMetrics(result);

  return (
    <div className="validation-page">
      <div className="validation-header">
        <div>
          <p className="validation-eyebrow">
            GROW YOUR STARTUP
          </p>

          <h1>Growth Strategy</h1>

          <p>
            Find practical ways to reach customers, grow your
            audience, and turn your startup into a sustainable
            business.
          </p>
        </div>

        <div className="validation-icon">
          <TrendingUp size={30} />
        </div>
      </div>

      <div className="validation-layout">
        <form
          className="validation-form"
          onSubmit={generateStrategy}
        >
          <h2>
            <Target size={20} />
            Your growth plan
          </h2>

          <label className="form-field">
            <span>What's your startup idea? *</span>

            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="Describe your product or service..."
              rows={4}
              required
            />
          </label>

          <label className="form-field">
            <span>Who are your target customers?</span>

            <textarea
              value={customers}
              onChange={(e) =>
                setCustomers(e.target.value)
              }
              placeholder="Describe the people you want to reach..."
              rows={3}
            />
          </label>

          <label className="form-field">
            <span>Current startup stage</span>

            <select
              value={stage}
              onChange={(e) => setStage(e.target.value)}
            >
              <option>Idea stage</option>
              <option>Pre-launch</option>
              <option>Launched</option>
              <option>Getting first customers</option>
              <option>Growing existing sales</option>
            </select>
          </label>

          <label className="form-field">
            <span>Marketing budget</span>

            <select
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            >
              <option>Low budget</option>
              <option>Moderate budget</option>
              <option>Flexible budget</option>
            </select>
          </label>

          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="validation-submit"
            disabled={loading || !idea.trim()}
          >
            {loading ? (
              <>
                <LoaderCircle
                  className="spin"
                  size={18}
                />
                Creating your strategy...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Generate growth strategy
              </>
            )}
          </button>
        </form>

        <div className="validation-results">
          <h2>
            <ChartNoAxesCombined size={20} />
            Your growth strategy
          </h2>

          {!result && !loading && (
            <div className="validation-empty">
              <Users size={36} />

              <h3>
                Your next growth milestone starts here
              </h3>

              <p>
                Enter your startup details and generate a
                personalized 30-day growth plan.
              </p>
            </div>
          )}

          {loading && (
            <div className="validation-empty">
              <LoaderCircle
                className="spin"
                size={36}
              />

              <h3>Building your growth plan...</h3>

              <p>
                This may take a little time. Please wait.
              </p>
            </div>
          )}

          {result && (
            <>
              <PlanVisuals
                title="Growth metrics overview"
                data={growthMetrics}
              />

              <div className="validation-plan-text">
                <FormattedAIResult text={result} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
