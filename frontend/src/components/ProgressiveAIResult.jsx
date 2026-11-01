import { useEffect, useState } from 'react';
import FormattedAIResult from './FormattedAIResult';

/** Reveals the real server response progressively; it does not simulate model steps. */
export default function ProgressiveAIResult({ text }) {
  const [visibleLength, setVisibleLength] = useState(0);
  const source = String(text ?? '');
  const shouldAnimate = source.length > 0 && source.length <= 3600;

  useEffect(() => {
    setVisibleLength(0);
    if (!shouldAnimate) {
      setVisibleLength(source.length);
      return undefined;
    }

    let position = 0;
    const interval = window.setInterval(() => {
      position = Math.min(source.length, position + 8);
      setVisibleLength(position);
      if (position >= source.length) window.clearInterval(interval);
    }, 18);

    return () => window.clearInterval(interval);
  }, [source, shouldAnimate]);

  const isRevealing = shouldAnimate && visibleLength < source.length;
  const displayed = shouldAnimate ? source.slice(0, visibleLength) : source;

  return (
    <div className={isRevealing ? 'ai-progressive-reveal is-revealing' : 'ai-progressive-reveal'}>
      <FormattedAIResult text={displayed} />
      {isRevealing && <span className="ai-reveal-cursor" aria-hidden="true" />}
    </div>
  );
}
