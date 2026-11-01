import { useState } from 'react';
import { MessageSquare, Send, Sparkles, User } from 'lucide-react';
import client from '../api/client';
import ProgressiveAIResult from '../components/ProgressiveAIResult';

const suggestions = [
  'Help me find a startup idea',
  'How do I validate my business idea?',
  'Help me plan my MVP',
  'How can I find my first customers?',
];

export default function Assistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi, founder! I’m your AI co-founder. Tell me what you want to build or choose a prompt below to get started.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  async function sendMessage(value = input) {
    const content = value.trim();
    if (!content || loading) return;

    const updatedMessages = [...messages, { role: 'user', content }];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      const apiMessages = updatedMessages.slice(-30).map(({ role, content }) => ({ role, content }));
      const response = await client.post('/ai/chat', { messages: apiMessages });
      setMessages((current) => [...current, { role: 'assistant', content: response.data.reply }]);
    } catch (error) {
      const detail = error.response?.data?.detail;
      const errorMessage = typeof detail === 'string'
        ? detail
        : error.response?.status === 401
          ? 'Your session may have expired. Please log in again, then retry.'
          : 'I couldn’t reach the AI service. Please check that your backend and Ollama are running, then try again.';
      setMessages((current) => [...current, { role: 'assistant', content: errorMessage }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="main-content">
      <header className="topbar">
        <div>
          <div className="breadcrumb">Workspace <span>/</span> AI Co-Founder</div>
          <h1>AI Co-Founder</h1>
        </div>
      </header>

      <section className="ai-studio-shell">
        <div className="ai-studio-header">
          <div className="ai-studio-heading-row">
            <div className="ai-studio-icon"><Sparkles size={23} /></div>
            <div className="ai-studio-title">
              <h2>Your startup thinking partner</h2>
              <p>Brainstorm, validate, plan, and take your next step.</p>
            </div>
            <div className="ai-orbit-visual" aria-hidden="true">
              <span className="ai-orbit-ring ring-one" />
              <span className="ai-orbit-ring ring-two" />
              <span className="ai-orbit-core"><Sparkles size={15} /></span>
              <i /><b />
            </div>
          </div>
          <div className="ai-studio-caption"><span className="ai-live-dot" /> AI workspace <span>·</span> Answers come from your connected model</div>
        </div>

        <div className="ai-chat-history" aria-live="polite">
          {messages.map((message, index) => (
            <div className={`ai-message-row ${message.role === 'user' ? 'from-user' : 'from-ai'}`} key={index}>
              <div className={`ai-message-avatar ${message.role === 'user' ? 'user-avatar' : 'assistant-avatar'}`}>
                {message.role === 'user' ? <User size={17} /> : <MessageSquare size={17} />}
              </div>
              <div className={`ai-message-bubble ${message.role === 'user' ? 'user-bubble' : 'assistant-bubble'}`}>
                {message.role === 'assistant' ? <ProgressiveAIResult text={message.content} /> : message.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="ai-thinking-card">
              <div className="ai-thinking-visual" aria-hidden="true"><span /><span /><span /><Sparkles size={16} /></div>
              <div className="ai-thinking-copy"><strong>Your co-founder is preparing a response</strong><p>Waiting for the connected AI model. The answer will appear here progressively.</p></div>
              <span className="ai-thinking-dots"><i /><i /><i /></span>
            </div>
          )}
        </div>

        <div className="ai-suggestion-row">
          {suggestions.map((suggestion) => (
            <button type="button" className="ai-suggestion-chip" key={suggestion} disabled={loading} onClick={() => sendMessage(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>

        <form className="ai-chat-composer" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}>
          <input
            aria-label="Message your AI co-founder"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Tell me about your startup idea..."
            disabled={loading}
          />
          <button type="submit" aria-label="Send message" disabled={!input.trim() || loading}>
            <Send size={19} />
          </button>
        </form>
      </section>

      <p className="ai-studio-footnote">Powered by your connected AI model through FastAPI and Ollama.</p>
    </main>
  );
}
