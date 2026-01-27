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

  // List detection patterns
  const UNORDERED_LIST_REGEX = /^[*\-+]\s/;
  const ORDERED_LIST_REGEX = /^\d+\.\s/;

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
  let listType: 'ul' | 'ol' | null = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code blocks (```)
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        // Remove trailing newline from code block content
        const trimmedCode = codeBlockContent.trimEnd();
        processedLines.push(`<pre><code>${trimmedCode}</code></pre>`);
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
    const trimmedLine = line.trim();
    if (inList && !trimmedLine.match(UNORDERED_LIST_REGEX) && !trimmedLine.match(ORDERED_LIST_REGEX)) {
      processedLines.push(`</${listType}>`);
      inList = false;
      listType = null;
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
      if (!inList || listType !== 'ul') {
        if (inList) {
          processedLines.push(`</${listType}>`);
        }
        processedLines.push('<ul>');
        inList = true;
        listType = 'ul';
      }
      processedLines.push(`<li>${unorderedListMatch[1]}</li>`);
      continue;
    }

    // Ordered lists (1., 2., etc.)
    const orderedListMatch = line.match(/^\d+\.\s+(.+)$/);
    if (orderedListMatch) {
      if (!inList || listType !== 'ol') {
        if (inList) {
          processedLines.push(`</${listType}>`);
        }
        processedLines.push('<ol>');
        inList = true;
        listType = 'ol';
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
    processedLines.push(`</${listType}>`);
  }

  html = processedLines.join('\n');

  // Inline markdown (process in order to avoid conflicts)
  // Bold first (**text** or __text__) - don't cross line boundaries
  html = html.replace(/\*\*([^\n*]+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^\n_]+?)__/g, '<strong>$1</strong>');

  // Then italic (*text* or _text_) - don't cross line boundaries
  html = html.replace(/\*([^\n*]+?)\*/g, '<em>$1</em>');
  html = html.replace(/_([^\n_]+?)_/g, '<em>$1</em>');

  // Inline code (`code`) - don't cross line boundaries
  html = html.replace(/`([^`\n]+?)`/g, '<code>$1</code>');

  // Links ([text](url)) - validate URL for security
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, text, url) => {
    // Only allow safe protocols
    const sanitizedUrl = url.match(/^https?:\/\/|^mailto:/) ? url : '#';
    return `<a href="${sanitizedUrl}" target="_blank" rel="noopener noreferrer">${text}</a>`;
  });

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
