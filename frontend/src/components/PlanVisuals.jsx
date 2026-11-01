import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

export default function PlanVisuals({ title, data, dataKey = 'value' }) {
  if (!Array.isArray(data) || data.length === 0) {
    return null;
  }

  return (
    <section className="signal-card signal-chart-card plan-visual-card">
      <div className="signal-card-head">
        <div>
          <span className="signal-label">VISUAL OVERVIEW</span>
          <h3>{title}</h3>
        </div>

        <span className="chart-chip">AI PLAN</span>
      </div>

      <div style={{ width: '100%', height: 260, marginTop: 20 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 10, right: 12, left: 0, bottom: 10 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="name"
              tick={{ fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />

            <YAxis
              tick={{ fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />

            <Tooltip />

            <Bar
              dataKey={dataKey}
              fill="#0c8a7c"
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="chart-footnote">
        Based on the generated plan. Review recommendations before making decisions.
      </p>
    </section>
  );
}