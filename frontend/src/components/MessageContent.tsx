import React from 'react';
import './MessageContent.css';

interface MessageContentProps {
  content: string;
}

/**
 * Escapes HTML special characters to prevent XSS
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Parses markdown and ExpressionText highlights into HTML
 * Supports: headings, lists, bold, italic, code, blockquotes, links
 * Preserves ExpressionText format: [[phrase::meaning]]
 */
function parseMarkdown(content: string): string {
  let html = content;

  // First, protect ExpressionText highlights from markdown processing
  const expressionTexts: string[] = [];
  html = html.replace(/\[\[(.+?)::(.+?)\]\]/g, (match) => {
    const index = expressionTexts.push(match) - 1;
    return `§§§EXPR${index}§§§`;
  });

  // Escape HTML to prevent XSS
  html = escapeHtml(html);

  // Parse markdown (process line by line for block elements)
  const lines = html.split('\n');
  const processedLines: string[] = [];
  let inCodeBlock = false;
  let codeBlockContent = '';
  let inList = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code blocks (```)
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        processedLines.push(`<pre><code>${codeBlockContent}</code></pre>`);
        codeBlockContent = '';
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBlockContent += line + '\n';
      continue;
    }

    // Close list if we're no longer in list items
    if (inList && !line.trim().match(/^[*\-+]\s/) && !line.trim().match(/^\d+\.\s/)) {
      processedLines.push('</ul>');
      inList = false;
    }

    // Headings (# - ######)
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = headingMatch[2];
      processedLines.push(`<h${level}>${text}</h${level}>`);
      continue;
    }

    // Unordered lists (*, -, +)
    const unorderedListMatch = line.match(/^[*\-+]\s+(.+)$/);
    if (unorderedListMatch) {
      if (!inList) {
        processedLines.push('<ul>');
        inList = true;
      }
      processedLines.push(`<li>${unorderedListMatch[1]}</li>`);
      continue;
    }

    // Ordered lists (1., 2., etc.)
    const orderedListMatch = line.match(/^\d+\.\s+(.+)$/);
    if (orderedListMatch) {
      if (!inList) {
        processedLines.push('<ol>');
        inList = true;
      }
      processedLines.push(`<li>${orderedListMatch[1]}</li>`);
      continue;
    }

    // Blockquotes (>)
    const blockquoteMatch = line.match(/^>\s*(.*)$/);
    if (blockquoteMatch) {
      processedLines.push(`<blockquote>${blockquoteMatch[1]}</blockquote>`);
      continue;
    }

    // Empty line
    if (line.trim() === '') {
      processedLines.push('<br />');
      continue;
    }

    // Regular line
    processedLines.push(line);
  }

  // Close list if still open
  if (inList) {
    processedLines.push('</ul>');
  }

  html = processedLines.join('\n');

  // Inline markdown (bold, italic, code, links)
  // Bold (**text** or __text__)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

  // Italic (*text* or _text_)
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.+?)_/g, '<em>$1</em>');

  // Inline code (`code`)
  html = html.replace(/`(.+?)`/g, '<code>$1</code>');

  // Links ([text](url))
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Restore ExpressionText highlights and convert to interactive elements
  html = html.replace(/§§§EXPR(\d+)§§§/g, (_, index) => {
    const expr = expressionTexts[parseInt(index)];
    const match = expr.match(/\[\[(.+?)::(.+?)\]\]/);
    if (match) {
      const phrase = match[1];
      const meaning = match[2];
      return `<span class="expression-text" data-meaning="${escapeHtml(meaning)}" title="${escapeHtml(meaning)}">${escapeHtml(phrase)}</span>`;
    }
    return expr;
  });

  return html;
}

const MessageContent: React.FC<MessageContentProps> = ({ content }) => {
  const htmlContent = parseMarkdown(content);

  return (
    <div
      className="message-content-markdown"
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
};

export default MessageContent;
