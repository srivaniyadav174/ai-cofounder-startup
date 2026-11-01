
import { useState } from 'react';
import {
  Boxes,
  Sparkles,
  LoaderCircle,
  CheckCircle2,
  Target,
  ListChecks,
} from 'lucide-react';

import client from '../api/client';
import FormattedAIResult from '../components/FormattedAIResult';
import PlanVisuals from '../components/PlanVisuals';

// Extract actual feature counts from the AI-generated roadmap.
function getFeaturePriorityData(plan) {
  if (!plan || !plan.trim()) {
    return [];
  }

  const priorities = [
    {
      name: 'Must Have',
      pattern: /^must[\s-]*have$/i,
    },
    {
      name: 'Should Have',
      pattern: /^should[\s-]*have$/i,
    },
    {
      name: 'Later',
      pattern: /^later$/i,
    },
  ];

  const lines = plan.split(/\r?\n/);

  // Normalize Markdown headings and bold formatting.
  const normalizeHeading = (line) => {
    return line
      .trim()
      .replace(/^#{1,6}\s*/, '')
      .replace(/\*\*/g, '')
      .replace(/__/g, '')
      .replace(/:$/, '')
      .trim();
  };

  // Identify the priority section headings.
  const headingIndexes = [];

  lines.forEach((line, index) => {
    const normalized = normalizeHeading(line);

    const priorityIndex = priorities.findIndex((priority) =>
      priority.pattern.test(normalized)
    );

    if (priorityIndex !== -1) {
      headingIndexes.push({
        index,
        priorityIndex,
      });
    }
  });

  // Count features inside each priority section.
  return priorities.map((priority, priorityIndex) => {
    const heading = headingIndexes.find(
      (item) => item.priorityIndex === priorityIndex
    );

    if (!heading) {
      return {
        name: priority.name,
        value: 0,
      };
    }

    const nextHeading = headingIndexes.find(
      (item) => item.index > heading.index
    );

    const sectionEnd = nextHeading
      ? nextHeading.index
      : lines.length;

    const sectionLines = lines.slice(
      heading.index + 1,
      sectionEnd
    );

    // Count feature bullets, including bold feature names.
    const featureLines = sectionLines.filter((line) => {
      return /^\s*[-*+]\s+\S/.test(line);
    });

    return {
      name: priority.name,
      value: featureLines.length,
    };
  });
}

function MVPPlanner() {
  const [idea, setIdea] = useState('');
  const [customers, setCustomers] = useState('');
  const [budget, setBudget] = useState('Low budget');
  const [timeline, setTimeline] = useState('4 weeks');

  const [plan, setPlan] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const generatePlan = async (event) => {
    event.preventDefault();

    if (!idea.trim()) {
      setError('Please enter your startup idea.');
      return;
    }

    setError('');
    setPlan('');
    setLoading(true);

    const prompt = `
You are an experienced startup product manager and AI co-founder.

Create a practical, visually structured MVP roadmap.

Startup idea: ${idea}
Target customers: ${customers || 'Not specified'}
Available budget: ${budget}
Target timeline: ${timeline}

Organize the response into these sections:

1. MVP GOAL
Customer problem, product goal, and expected outcome.

2. CORE FEATURES
Essential features with priority:

### Must-Have
List the essential features as individual bullet points.

### Should-Have
List the useful features as individual bullet points.

### Later
List future features as individual bullet points.

IMPORTANT:
Keep these three priority headings exactly as written.
Use one bullet point for each individual feature.
Do not include development tasks under these priority sections.

3. DEVELOPMENT ROADMAP
Create a week-by-week roadmap.
For each week include:
- Main objective
- Tasks
- Deliverable
- Milestone

4. TECHNOLOGY STACK
Recommended frontend, backend, database, and tools.

5. CUSTOMER TESTING
Testing activities, feedback collection, and improvements.

6. SUCCESS METRICS
Provide measurable targets and KPIs.

7. RISKS
Main risks and practical solutions.

8. NEXT ACTIONS
The first five actions the founder should take.

Keep the plan realistic for a solo founder or small team.

IMPORTANT FORMATTING:
Use clear Markdown headings.
Use numbered lists and bullet points.
Use short, actionable statements.
Use tables for roadmap timelines when useful.
Avoid long paragraphs.
Avoid generic advice.
Make every action specific to the startup idea.
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

      const finalPlan =
        typeof reply === 'string' && reply.trim()
          ? reply
          : 'The AI returned an empty response. Please try again.';

      // Update the current page.
      setPlan(finalPlan);

      // Save only a valid AI-generated roadmap.
      if (typeof reply === 'string' && reply.trim()) {
        localStorage.setItem('mvpPlan', finalPlan);

        // Notify the Dashboard that the MVP plan was saved.
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
            'Could not generate the MVP plan. Check that the backend is running and try again.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const featureData = getFeaturePriorityData(plan);

  return (
    <main className="main-content mvp-planner-page">
      <header className="topbar">
        <div>
          <div className="breadcrumb">
            Workspace <span>/</span> MVP Planner
          </div>

          <h1>MVP Planner</h1>
        </div>
      </header>

      <section className="placeholder-panel mvp-planner-panel">
        <div className="placeholder-icon">
          <Boxes size={28} />
        </div>

        <h2>Build the smallest useful product</h2>

        <p>
          Turn your startup idea into a focused product roadmap.
          Build what customers need first and avoid wasting time
          on unnecessary features.
        </p>

        <form
          onSubmit={generatePlan}
          className="validation-form mvp-planner-form"
        >
          <div className="form-field">
            <label htmlFor="mvp-idea">
              What's your startup idea? *
            </label>

            <textarea
              id="mvp-idea"
              value={idea}
              onChange={(event) =>
                setIdea(event.target.value)
              }
              placeholder="Describe the product you want to build..."
              rows={3}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="mvp-customers">
              Who are your target customers?
            </label>

            <input
              id="mvp-customers"
              value={customers}
              onChange={(event) =>
                setCustomers(event.target.value)
              }
              placeholder="e.g. College students preparing for exams"
            />
          </div>

          <div className="form-field">
            <label htmlFor="mvp-budget">
              Available budget
            </label>

            <select
              id="mvp-budget"
              value={budget}
              onChange={(event) =>
                setBudget(event.target.value)
              }
            >
              <option>Low budget</option>
              <option>Moderate budget</option>
              <option>Flexible budget</option>
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="mvp-timeline">
              Target timeline
            </label>

            <select
              id="mvp-timeline"
              value={timeline}
              onChange={(event) =>
                setTimeline(event.target.value)
              }
            >
              <option>1 week</option>
              <option>2 weeks</option>
              <option>4 weeks</option>
              <option>8 weeks</option>
              <option>12 weeks</option>
            </select>
          </div>

          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="primary-button"
            disabled={loading || !idea.trim()}
          >
            {loading ? (
              <>
                <LoaderCircle size={17} className="spin" />
                Creating your roadmap...
              </>
            ) : (
              <>
                <Sparkles size={17} />
                Generate MVP roadmap
              </>
            )}
          </button>
        </form>
      </section>

      {loading && (
        <section className="placeholder-panel mvp-planner-loading">
          <LoaderCircle size={24} className="spin" />

          <p>
            Your AI co-founder is planning your MVP...
          </p>
        </section>
      )}

      {plan && (
        <section className="placeholder-panel mvp-planner-results">
          <div className="placeholder-icon">
            <CheckCircle2 size={28} />
          </div>

          <h2>Your MVP roadmap</h2>

          <p>
            Review your roadmap and adjust it based on real
            customer feedback.
          </p>

          <div className="mvp-results">
            <PlanVisuals
              title="Feature priority overview"
              data={featureData}
            />

            <div className="validation-results">
              <div className="section-note">
                <Target size={17} />
                Your product plan
              </div>

              <div className="validation-plan-text">
                <FormattedAIResult text={plan} />
              </div>
            </div>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={() => window.print()}
          >
            <ListChecks size={17} />
            Print or save roadmap
          </button>
        </section>
      )}
    </main>
  );
}

export default MVPPlanner;
