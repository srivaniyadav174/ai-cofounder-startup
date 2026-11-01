import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Sparkles, ArrowRight, ShieldCheck, Lightbulb, Eye, EyeOff } from 'lucide-react';

export default function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/auth/register', {
        name: name.trim(),
        email: email.trim(),
        password,
      });
      const token = response.data?.access_token || response.data?.token;
      if (token) {
        localStorage.setItem('token', token);
        navigate('/login', { state: { message: 'Account created. Please sign in to continue.' } });
      } else {
        navigate('/login', { state: { message: 'Registration successful. Please sign in.' } });
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) setError(detail.map((item) => item.msg || 'Invalid input').join('. '));
      else if (typeof detail === 'string') setError(detail);
      else setError('Registration failed. Check the details and try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-showcase">
        <div className="auth-motion" aria-hidden="true"><span /><span /><span /><span /><i /><i /><i /></div>
        <Link to="/register" className="auth-brand"><span><Sparkles size={21} /></span><strong>AI Co-Founder</strong></Link>
        <div className="auth-showcase-content">
          <span className="auth-kicker"><span /> STARTUP INTELLIGENCE STUDIO</span>
          <h1>Your idea.<br /><span>A smarter start.</span></h1>
          <p>Build confidence in your startup decisions with a guided path from opportunity to validation and MVP.</p>
          <div className="auth-feature-list"><div><Lightbulb size={16} /><span>Discover opportunities</span></div><div><ShieldCheck size={16} /><span>Test your assumptions</span></div><div><ArrowRight size={16} /><span>Build what matters</span></div></div>
        </div>
        <div className="auth-showcase-footer">AI CO-FOUNDER FOR STARTUPS <span>•</span> TURN IDEAS INTO ACTION</div>
      </section>
      <section className="auth-form-side">
        <div className="auth-form-card">
          <div className="auth-mobile-brand"><span><Sparkles size={18} /></span> AI Co-Founder</div>
          <span className="auth-form-eyebrow">GET STARTED</span>
          <h2>Create your account</h2>
          <p className="auth-form-intro">Set up your founder workspace and start shaping your idea.</p>
          {error && <div className="auth-error" role="alert">{error}</div>}
          <form onSubmit={handleSubmit} className="auth-form">
            <label htmlFor="register-name">Full name</label>
            <input id="register-name" name="name" placeholder="Your full name" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" required />
            <label htmlFor="register-email">Email address</label>
            <input id="register-email" name="email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required />
            <label htmlFor="register-password">Password</label>
            <div className="auth-password-wrap"><input id="register-password" name="password" type={showPassword ? 'text' : 'password'} placeholder="At least 8 characters" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} autoComplete="new-password" required /><button type="button" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword(!showPassword)}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
            <button className="auth-submit" type="submit" disabled={loading}>{loading ? 'Creating account…' : 'Create account'} {!loading && <ArrowRight size={17} />}</button>
          </form>
          <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
          <div className="auth-security-note"><ShieldCheck size={14} /> Your account details stay in your workspace.</div>
        </div>
      </section>
    </main>
  );
}
