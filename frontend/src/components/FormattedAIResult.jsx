import React from 'react';

function inlineFormat(text = '') {
  const safeText = String(text ?? '');
  const parts = safeText.split(/(\*\*[^*]+\*\*)/g);

  return parts.map((part, index) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={index}>{part.slice(2, -2)}</strong>
      : part
  );
}

export default function FormattedAIResult({ text }) {
  if (text == null || text === '') return null;

  const lines = String(text).replace(/\r/g, '').split('\n');
  const blocks = [];
  let list = [];

  const flushList = () => {
    if (list.length) {
      blocks.push(
        <ul className="ai-result-list" key={`list-${blocks.length}`}>
          {list.map((item, i) => (
            <li key={i}>{inlineFormat(item)}</li>
          ))}
        </ul>
      );
      list = [];
    }
  };

  lines.forEach((raw, index) => {
    const line = String(raw ?? '').trim();

    if (!line) {
      flushList();
      return;
    }

    const heading =
      line.match(/^(#{1,3})\s+(.+)$/) ||
      line.match(/^\*\*(.+?)\*\*:?$/);

    if (heading) {
      flushList();

      const title = heading[2] || heading[1];

      blocks.push(
        <h3 key={`h-${index}`}>
          {inlineFormat(title.replace(/:$/, ''))}
        </h3>
      );

      return;
    }

    const bullet = line.match(
      /^(?:[-*•]\s+|\d+[.)]\s+)(.+)$/
    );

    if (bullet) {
      list.push(bullet[1]);
      return;
    }

    flushList();

    blocks.push(
      <p key={`p-${index}`}>{inlineFormat(line)}</p>
    );
  });

  flushList();

  return <div className="ai-result-content">{blocks}</div>;
}