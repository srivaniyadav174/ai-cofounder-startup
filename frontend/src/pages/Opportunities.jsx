import { useState } from 'react';
import { Lightbulb, Sparkles, ArrowRight, LoaderCircle, Target, Users, Wallet, Compass, RefreshCw } from 'lucide-react';
import client from '../api/client';
import OpportunityVisualResults from '../components/OpportunityVisualResults';

const steps = ['Understanding your founder profile', 'Exploring real-world problems', 'Preparing tailored opportunities'];

export default function Opportunities() {
  const [interests, setInterests] = useState('');
  const [skills, setSkills] = useState('');
  const [budget, setBudget] = useState('₹10,000–₹50,000');
  const [ideas, setIdeas] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [phase, setPhase] = useState(0);

  async function findIdeas(event) {
    event.preventDefault(); setError(''); setIdeas(''); setLoading(true); setPhase(0);
    const phaseTimer = setInterval(() => setPhase((p) => Math.min(p + 1, 2)), 4500);
    const prompt = `Act as my AI startup co-founder. Suggest 5 practical startup opportunities based on my profile.

My interests: ${interests.trim() || 'Not specified'}
My skills: ${skills.trim() || 'Not specified'}
My starting budget: ${budget}

Return exactly 5 opportunities, each with a clear Markdown heading in this format: ### Opportunity 1: [short title]. Under each heading use these labeled lines: **Target customers:**; **Problem:**; **Why it may fit:**; **First validation step:**. Keep each field concise and specific to my profile and budget. Do not invent market statistics, numerical match scores, or guarantees. Clearly label assumptions. The result must be easy to scan, not one long essay.`;
    try {
      const response = await client.post('/ai/chat', { messages: [{ role: 'user', content: prompt }] });
      setIdeas(response.data.reply || 'The AI returned an empty response. Please try again.');
    } catch (err) {
      setError(err.response?.status === 401 ? 'Your session may have expired. Please sign in again.' : 'Could not generate opportunities. Check that the backend and AI service are running, then try again.');
    } finally { clearInterval(phaseTimer); setLoading(false); }
  }

  return <div className="opportunities-page">
    <div className="opportunities-hero">
      <div className="opportunity-hero-copy"><span className="opportunity-eyebrow"><Sparkles size={14}/> OPPORTUNITY INTELLIGENCE</span><h1>Find a problem<br/><span>worth solving.</span></h1><p>Discover startup directions that fit your interests, skills, and resources—then validate before you build.</p><div className="opportunity-hero-pills"><span><Target size={14}/> Problem-first</span><span><Users size={14}/> Customer-led</span><span><Wallet size={14}/> Budget-aware</span></div></div>
      <div className="opportunity-hero-art" aria-hidden="true"><div className="op-art-orbit orbit-a"/><div className="op-art-orbit orbit-b"/><div className="op-art-center"><Lightbulb size={31}/></div><span className="op-art-node node-a"><Compass size={15}/></span><span className="op-art-node node-b"><Users size={15}/></span><span className="op-art-node node-c"><Target size={15}/></span><div className="op-art-caption">IDEA → INSIGHT</div></div>
    </div>
    <div className="opportunity-workspace">
      <section className="opportunity-form-card"><div className="opportunity-section-title"><span className="opportunity-icon"><Lightbulb size={20}/></span><div><span className="section-eyebrow">START WITH YOU</span><h2>Tell us about your founder profile</h2><p>We'll tailor the ideas to what you can realistically explore.</p></div></div>
      <form onSubmit={findIdeas} className="opportunity-form">
        <label htmlFor="opp-interests">What are you interested in?</label><textarea id="opp-interests" value={interests} onChange={e=>setInterests(e.target.value)} placeholder="Education, healthcare, AI, local businesses…" rows={3}/>
        <label htmlFor="opp-skills">What skills or experience do you have?</label><textarea id="opp-skills" value={skills} onChange={e=>setSkills(e.target.value)} placeholder="Coding, sales, design, teaching, marketing…" rows={3}/>
        <label htmlFor="opp-budget">What's your approximate starting budget?</label><select id="opp-budget" value={budget} onChange={e=>setBudget(e.target.value)}><option>Under ₹10,000</option><option>₹10,000–₹50,000</option><option>₹50,000–₹2 lakh</option><option>₹2 lakh+</option></select>
        <button type="submit" disabled={loading} className="opportunity-submit">{loading ? <><LoaderCircle size={17} className="spin-icon"/> Exploring your profile…</> : <><Sparkles size={17}/> Discover my opportunities <ArrowRight size={16}/></>}</button>
      </form>
      {loading && <div className="opportunity-progress" aria-live="polite"><div className="opportunity-progress-top"><span className="opportunity-pulse"/> AI opportunity scan <span>{Math.min(phase+1,3)} / 3</span></div><div className="opportunity-progress-track"><i style={{width:`${(phase+1)*33.333}%`}}/></div><p>{steps[phase]}</p><div className="opportunity-loading-dots"><i/><i/><i/></div></div>}
      {error && <div className="opportunity-error" role="alert"><strong>Could not complete the scan</strong><p>{error}</p><button type="button" onClick={()=>setError('')}><RefreshCw size={14}/> Dismiss</button></div>}
      </section>
      <aside className="opportunity-side-note"><span className="side-note-icon"><Target size={18}/></span><span className="section-eyebrow">HOW IT WORKS</span><h3>Ideas are a starting point—not a guarantee.</h3><p>We'll present opportunities with customer context and a first validation action. Market demand and success should be tested with real evidence.</p><div className="side-note-step"><span>01</span> Match your strengths</div><div className="side-note-step"><span>02</span> Surface customer problems</div><div className="side-note-step"><span>03</span> Suggest a low-cost test</div></aside>
    </div>
    {ideas && <section className="opportunity-results" aria-live="polite"><div className="opportunity-results-heading"><div><span className="section-eyebrow">YOUR AI-GENERATED SHORTLIST</span><h2>Opportunities to explore</h2><p>Review the ideas, then choose one to validate with real customers.</p></div><span className="results-status"><span/> Generated</span></div><div className="opportunity-result-content opportunity-visual-results"><OpportunityVisualResults text={ideas}/></div><div className="opportunity-results-footer"><Sparkles size={15}/> AI-generated suggestions · Validate demand before investing money.</div></section>}
  </div>;
}
