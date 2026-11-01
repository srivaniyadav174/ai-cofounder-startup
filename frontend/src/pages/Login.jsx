import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Link, useLocation } from 'react-router-dom';
import { ArrowRight, Eye, EyeOff, Sparkles, ShieldCheck, Compass, FlaskConical, Rocket, Lightbulb, Target } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [introStep, setIntroStep] = useState(0);
  const [showLogin, setShowLogin] = useState(false);
  const { login } = useContext(AuthContext);
  const location = useLocation();

  const handleSubmit = async (event) => {
    event.preventDefault(); setError(''); setLoading(true);
    try { await login(email, password); }
    catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Sign in failed. Check your email and password, then try again.');
    } finally { setLoading(false); }
  };

  const introSlides = [
    { eyebrow: 'STEP 01 · DISCOVER', title: <>Find your next<br/><em>big opportunity.</em></>, copy: 'Explore startup opportunities shaped around your interests, skills, and the problems worth solving.', tags: ['Explore ideas', 'Spot market needs'], icon: Lightbulb, scene: 'discover' },
    { eyebrow: 'STEP 02 · VALIDATE', title: <>Turn a spark into<br/><em>real evidence.</em></>, copy: 'Test your assumptions, understand your audience, and learn what customers actually need.', tags: ['Know your audience', 'Test assumptions'], icon: Target, scene: 'validate' },
    { eyebrow: 'STEP 03 · BUILD & GROW', title: <>Make your idea<br/><em>move forward.</em></>, copy: 'Plan a focused MVP, take practical steps, and grow with a clear startup roadmap.', tags: ['Plan your MVP', 'Grow with focus'], icon: Rocket, scene: 'build' },
  ];

  if (!showLogin) {
    const slide = introSlides[introStep];
    const SceneIcon = slide.icon;
    return (
      <main className="startup-onboarding">
        <header className="onboarding-topbar"><Link to="/login" className="onboarding-brand"><span><Sparkles size={19}/></span><strong>AI Co-Founder</strong></Link><button className="onboarding-skip" onClick={() => setShowLogin(true)}>Skip intro <ArrowRight size={15}/></button></header>
        <section className={`onboarding-stage scene-${slide.scene}`} key={introStep}>
          <div className="onboarding-copy"><span className="onboarding-eyebrow">{slide.eyebrow}</span><h1>{slide.title}</h1><p>{slide.copy}</p><div className="onboarding-tags">{slide.tags.map((tag,i)=><span key={tag}><b>0{i+1}</b>{tag}</span>)}</div>
            <div className="onboarding-controls"><div className="onboarding-dots">{introSlides.map((_,i)=><button key={i} aria-label={`Go to step ${i+1}`} className={i===introStep?'active':''} onClick={()=>setIntroStep(i)}/>)}</div><span className="onboarding-step-count">0{introStep+1} <i>/ 03</i></span><button className="onboarding-next" onClick={()=>introStep===2?setShowLogin(true):setIntroStep(introStep+1)}>{introStep===2?'Sign in':'Continue'} <ArrowRight size={17}/></button></div>
          </div>
          <div className={`onboarding-art onboarding-art-${slide.scene}`} aria-label="Animated startup illustration">
            <div className="onboarding-art-glow"/><div className="onboarding-orbit orbit-one"/><div className="onboarding-orbit orbit-two"/><div className="onboarding-orbit orbit-three"/>
            <div className="onboarding-illustration-card"><div className="illustration-topline"><span/><span/><span/></div><div className="illustration-main-icon"><SceneIcon size={52}/></div><div className="illustration-bars"><i/><i/><i/><i/><i/></div><div className="illustration-caption"><b>{slide.tags[0]}</b><small>{slide.tags[1]}</small></div></div>
            <span className="onboarding-float float-left"><Lightbulb size={18}/></span><span className="onboarding-float float-right"><Sparkles size={18}/></span><span className="onboarding-float float-bottom"><Rocket size={18}/></span><div className="onboarding-spark spark-a"/><div className="onboarding-spark spark-b"/><div className="onboarding-spark spark-c"/>
          </div>
        </section><footer className="onboarding-footer"><span>YOUR STARTUP, STEP BY STEP</span><span>Discover <b>·</b> Validate <b>·</b> Build <b>·</b> Grow</span></footer>
      </main>
    );
  }

  return (
    <main className="auth-page auth-unified">
      <div className="auth-unified-glow glow-one" aria-hidden="true" />
      <div className="auth-unified-glow glow-two" aria-hidden="true" />
      <header className="auth-unified-header">
        <Link to="/login" className="auth-unified-brand"><span><Sparkles size={19}/></span><strong>AI Co-Founder</strong></Link>
        <span className="auth-unified-header-note">YOUR STARTUP, IN FOCUS</span>
      </header>

      <section className="auth-unified-layout">
        <div className="auth-unified-copy">
          <span className="auth-unified-eyebrow"><i/> YOUR FOUNDER WORKSPACE</span>
          <h1>Your next move<br/><em>starts here.</em></h1>
          <p>One focused space to discover opportunities, validate your idea, plan your MVP, and grow with confidence.</p>
          <div className="auth-unified-steps">
            <div><span className="step-icon"><Compass size={16}/></span><span><b>Discover</b><small>Find your direction</small></span><span className="step-num">01</span></div>
            <div><span className="step-icon"><FlaskConical size={16}/></span><span><b>Validate</b><small>Test what matters</small></span><span className="step-num">02</span></div>
            <div><span className="step-icon"><Rocket size={16}/></span><span><b>Build</b><small>Make progress real</small></span><span className="step-num">03</span></div>
          </div>
          <div className="auth-unified-orbit" aria-hidden="true"><span className="orbit-ring ring-one"/><span className="orbit-ring ring-two"/><span className="orbit-ring ring-three"/><span className="orbit-center"><Sparkles size={25}/></span><i className="orbit-star star-one"/><i className="orbit-star star-two"/><i className="orbit-star star-three"/></div>
        </div>

        <div className="auth-unified-card">
          <div className="auth-card-topline"><span className="auth-card-mark"><Sparkles size={15}/></span><span>WELCOME BACK</span><span className="auth-card-live"><i/> SECURE ACCESS</span></div>
          <h2>Let’s make<br/><span>something matter.</span></h2>
          <p className="auth-unified-intro">Sign in and continue building your next big idea.</p>
          {location.state?.message && <div className="auth-success" role="status">{location.state.message}</div>}
          {error && <div className="auth-error" role="alert">{error}</div>}
          <form onSubmit={handleSubmit} className="auth-form auth-unified-form">
            <label htmlFor="login-email">Email address</label>
            <input id="login-email" type="email" placeholder="you@example.com" autoComplete="email" value={email} onChange={(e)=>setEmail(e.target.value)} required/>
            <div className="auth-unified-label-row"><label htmlFor="login-password">Password</label><span>YOUR ACCOUNT</span></div>
            <div className="auth-password-wrap"><input id="login-password" type={showPassword?'text':'password'} placeholder="Enter your password" autoComplete="current-password" value={password} onChange={(e)=>setPassword(e.target.value)} required/><button type="button" aria-label={showPassword?'Hide password':'Show password'} onClick={()=>setShowPassword(!showPassword)}>{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></div>
            <button className="auth-unified-submit" type="submit" disabled={loading}>{loading?'Signing in…':'Enter your workspace'} {!loading&&<ArrowRight size={17}/>}</button>
          </form>
          <div className="auth-unified-bottom"><p>New to AI Co-Founder? <Link to="/register">Create an account <ArrowRight size={13}/></Link></p><span><ShieldCheck size={13}/> Your workspace is private and secure.</span></div>
        </div>
      </section>
      <footer className="auth-unified-footer"><span>IDEA <b>→</b> INSIGHT <b>→</b> ACTION</span><span>BUILT FOR THE NEXT GENERATION OF FOUNDERS</span></footer>
    </main>
  );
}
