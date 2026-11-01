import { useMemo, useState } from 'react';
import { ArrowUpRight, BriefcaseBusiness, GraduationCap, HeartPulse, Leaf, ShoppingBag, Sparkles, Target, Users, Wallet, Wrench, ChevronDown, CheckCircle2 } from 'lucide-react';
import FormattedAIResult from './FormattedAIResult';

const iconSet = [BriefcaseBusiness, GraduationCap, HeartPulse, Leaf, ShoppingBag, Wrench, Target, Users];
const palettes = [
  { color: '#0F766E', soft: '#E5F5F1', glow: 'rgba(15,118,110,.16)' },
  { color: '#D97706', soft: '#FFF3DF', glow: 'rgba(217,119,6,.16)' },
  { color: '#2563EB', soft: '#EAF1FF', glow: 'rgba(37,99,235,.15)' },
  { color: '#7C3AED', soft: '#F1EAFE', glow: 'rgba(124,58,237,.15)' },
];

function splitOpportunities(text) {
  const lines = String(text || '').replace(/\r/g, '').split('\n');
  const chunks = [];
  let current = null;
  const headingPatterns = [
    /^\s*#{1,4}\s*(?:Opportunity|Startup opportunity|Startup idea|Idea)\s*(?:#?\d+)?\s*[:—–-]\s*(.+?)\s*#*\s*$/i,
    /^\s*(?:\*\*)?\s*(?:Opportunity|Startup idea|Idea)\s*(?:#?\d+)?\s*[:—–-]\s*(.+?)\s*(?:\*\*)?\s*$/i,
    /^\s*#{1,4}\s*(\d+)[.)]\s+(.+?)\s*#*\s*$/,
    /^\s*(?:\*\*)?\s*(\d+)[.)]\s+(.+?)\s*(?:\*\*)?\s*$/,
  ];
  for (const raw of lines) {
    const line = raw.trim();
    let title = '';
    for (const pattern of headingPatterns) {
      const match = line.match(pattern);
      if (match) { title = match[match.length - 1].replace(/\*\*/g, '').trim(); break; }
    }
    if (title && title.length < 120) {
      if (current) chunks.push(current);
      current = { title: title.replace(/^\*\*|\*\*$/g, '').trim(), body: [] };
    } else if (current) current.body.push(raw);
  }
  if (current) chunks.push(current);
  return chunks.filter((item) => item.title && item.body.join('').trim());
}

function categoryFor(text) {
  const value = text.toLowerCase();
  if (/education|student|school|learning|tutor|career/.test(value)) return { label: 'Education', Icon: GraduationCap };
  if (/health|clinic|wellness|medical|fitness/.test(value)) return { label: 'Health & wellness', Icon: HeartPulse };
  if (/farm|food|agri|sustain|climate|waste|energy/.test(value)) return { label: 'Sustainability', Icon: Leaf };
  if (/shop|retail|seller|commerce|marketplace/.test(value)) return { label: 'Commerce', Icon: ShoppingBag };
  if (/software|automation|developer|ai|tech|digital/.test(value)) return { label: 'Technology', Icon: Wrench };
  return { label: 'Business opportunity', Icon: BriefcaseBusiness };
}

export default function OpportunityVisualResults({ text }) {
  const cards = useMemo(() => splitOpportunities(text), [text]);
  const [expanded, setExpanded] = useState(0);
  if (!cards.length) {
    return <div className="opportunity-fallback-card"><div className="opportunity-fallback-orbit"><Sparkles size={23}/></div><div><span className="opportunity-card-kicker">AI DISCOVERY</span><h3>Your opportunity shortlist</h3><p>The AI returned a response that could not be separated into individual ideas yet. Here is the complete result, preserved without changing its meaning.</p><FormattedAIResult text={text}/></div></div>;
  }
  return <div className="opportunity-visual-layout">
    <div className="opportunity-visual-summary"><div className="opportunity-summary-mark"><Sparkles size={17}/></div><div><strong>{cards.length} opportunities discovered</strong><span>Choose a card to explore the details and first validation action.</span></div><div className="opportunity-summary-burst" aria-hidden="true"><i/><i/><i/><i/><i/></div></div>
    <div className="opportunity-visual-grid">
      {cards.map((card, index) => {
        const palette = palettes[index % palettes.length];
        const category = categoryFor(`${card.title}\n${card.body.join('\n')}`);
        const Icon = category.Icon || iconSet[index % iconSet.length];
        const isOpen = expanded === index;
        return <article className={`opportunity-visual-card ${isOpen ? 'is-expanded' : ''}`} style={{'--opp-accent': palette.color, '--opp-soft': palette.soft, '--opp-glow': palette.glow, '--opp-index': index}} key={`${card.title}-${index}`}>
          <button className="opportunity-card-toggle" type="button" aria-expanded={isOpen} onClick={() => setExpanded(isOpen ? -1 : index)}>
            <div className="opportunity-card-topline"><span className="opportunity-card-number">{String(index + 1).padStart(2, '0')}</span><span className="opportunity-card-category">{category.label}</span></div>
            <div className="opportunity-card-illustration"><span className="opportunity-card-icon"><Icon size={24}/></span><span className="opportunity-card-rings"/><span className="opportunity-card-spark"><Sparkles size={13}/></span><span className="opportunity-card-dot dot-one"/><span className="opportunity-card-dot dot-two"/></div>
            <h3>{card.title}</h3><div className="opportunity-card-bottom"><span>{isOpen ? 'Hide details' : 'Explore opportunity'} <ArrowUpRight size={14}/></span><ChevronDown size={16} className="opportunity-card-chevron"/></div>
          </button>
          <div className={`opportunity-card-details ${isOpen ? 'details-open' : ''}`} aria-hidden={!isOpen}><div className="opportunity-card-detail-inner"><div className="opportunity-detail-heading"><Target size={14}/><span>Opportunity brief</span></div><FormattedAIResult text={card.body.join('\n')}/><div className="opportunity-card-validation"><CheckCircle2 size={15}/><span>Start by testing the idea with real potential customers.</span></div></div></div>
        </article>;
      })}
    </div>
    <div className="opportunity-visual-note"><span><Wallet size={14}/></span><p>These are AI-generated directions, not verified market forecasts. Validate demand before investing.</p></div>
  </div>;
}
