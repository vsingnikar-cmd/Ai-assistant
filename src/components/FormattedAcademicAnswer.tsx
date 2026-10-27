/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Check,
  Copy,
  Lightbulb,
  AlertTriangle,
  BookOpen,
  Code2,
  Table as TableIcon,
  ChevronRight,
  Sparkles,
  Bookmark
} from 'lucide-react';

interface FormattedAcademicAnswerProps {
  content: string;
}

export function FormattedAcademicAnswer({ content }: FormattedAcademicAnswerProps) {
  const [copiedCodeId, setCopiedCodeId] = useState<string | null>(null);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCodeId(id);
    setTimeout(() => setCopiedCodeId(null), 2000);
  };

  // Helper to parse blocks: code, table, callout, headings, lists, paragraphs
  const renderBlocks = () => {
    if (!content) return null;

    const lines = content.split('\n');
    const elements: React.ReactNode[] = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      // 1. Code Block (```)
      if (line.trim().startsWith('```')) {
        const lang = line.trim().replace(/^```/, '') || 'code';
        const codeLines: string[] = [];
        i++;
        while (i < lines.length && !lines[i].trim().startsWith('```')) {
          codeLines.push(lines[i]);
          i++;
        }
        i++; // skip closing ```
        const codeText = codeLines.join('\n');
        const codeId = `code-${i}`;

        elements.push(
          <div key={codeId} className="my-4 rounded-xl overflow-hidden border border-slate-800 bg-slate-950/80 shadow-md">
            <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800 text-xs text-slate-400">
              <span className="flex items-center space-x-1.5 font-mono text-[11px] font-semibold text-slate-300">
                <Code2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>{lang.toUpperCase()}</span>
              </span>
              <button
                onClick={() => handleCopy(codeText, codeId)}
                className="flex items-center space-x-1 text-slate-400 hover:text-white px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-700 transition text-[11px]"
              >
                {copiedCodeId === codeId ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Code</span>
                  </>
                )}
              </button>
            </div>
            <pre className="p-4 text-xs font-mono text-emerald-300/90 overflow-x-auto leading-relaxed">
              <code>{codeText}</code>
            </pre>
          </div>
        );
        continue;
      }

      // 2. Table Block (lines with '|')
      if (line.trim().startsWith('|') && line.includes('|')) {
        const tableLines: string[] = [];
        while (i < lines.length && lines[i].trim().startsWith('|')) {
          tableLines.push(lines[i].trim());
          i++;
        }

        if (tableLines.length >= 2) {
          // Parse header and rows
          const headerCells = tableLines[0]
            .split('|')
            .slice(1, -1)
            .map((c) => c.trim());

          // Skip separator line (e.g. |---|---|)
          const dataRows = tableLines.slice(2).map((r) =>
            r
              .split('|')
              .slice(1, -1)
              .map((c) => c.trim())
          );

          elements.push(
            <div key={`table-${i}`} className="my-4 overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/50 shadow-md">
              <div className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800/60 border-b border-slate-800 text-xs font-bold text-slate-300">
                <TableIcon className="w-4 h-4 text-sky-400" />
                <span>Comparison & Structured Data</span>
              </div>
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-800/40 text-slate-200 border-b border-slate-700/80">
                    {headerCells.map((h, hIdx) => (
                      <th key={hIdx} className="px-4 py-3 font-semibold tracking-wider">
                        {renderInlineFormatted(h)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {dataRows.map((row, rIdx) => (
                    <tr
                      key={rIdx}
                      className={rIdx % 2 === 0 ? 'bg-slate-900/30 hover:bg-slate-800/40' : 'bg-slate-950/30 hover:bg-slate-800/40'}
                    >
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="px-4 py-2.5 leading-relaxed">
                          {renderInlineFormatted(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
          continue;
        }
      }

      // 3. Headings (#, ##, ###, ####)
      if (line.startsWith('#')) {
        const level = line.match(/^#+/)?.[0].length || 1;
        const headingText = line.replace(/^#+\s*/, '').trim();

        if (level === 1 || level === 2) {
          elements.push(
            <div key={`h-${i}`} className="mt-5 mb-3 pt-2 border-b border-slate-800 pb-2">
              <h2 className="text-base font-extrabold text-white flex items-center space-x-2 tracking-tight">
                <span className="w-2 h-4 rounded-full bg-indigo-500 inline-block" />
                <span>{renderInlineFormatted(headingText)}</span>
              </h2>
            </div>
          );
        } else if (level === 3) {
          // Special badge check for sections like "Exam Tip", "Definition", "Working Mechanism"
          const isExamTip = /exam tip|caution|pitfall/i.test(headingText);
          const isDefinition = /definition|overview/i.test(headingText);
          const isAdvantages = /advantage|pros|benefits/i.test(headingText);

          elements.push(
            <div key={`h3-${i}`} className="mt-4 mb-2 flex items-center space-x-2">
              {isExamTip ? (
                <span className="p-1 rounded-md bg-amber-500/20 text-amber-400">
                  <Lightbulb className="w-4 h-4" />
                </span>
              ) : isDefinition ? (
                <span className="p-1 rounded-md bg-sky-500/20 text-sky-400">
                  <Bookmark className="w-4 h-4" />
                </span>
              ) : isAdvantages ? (
                <span className="p-1 rounded-md bg-emerald-500/20 text-emerald-400">
                  <Sparkles className="w-4 h-4" />
                </span>
              ) : (
                <ChevronRight className="w-4 h-4 text-indigo-400" />
              )}
              <h3 className="text-sm font-bold text-slate-100">{renderInlineFormatted(headingText)}</h3>
            </div>
          );
        } else {
          elements.push(
            <h4 key={`h4-${i}`} className="text-xs font-bold text-slate-300 mt-3 mb-1 uppercase tracking-wider">
              {renderInlineFormatted(headingText)}
            </h4>
          );
        }
        i++;
        continue;
      }

      // 4. Callout / Blockquote (> ...)
      if (line.trim().startsWith('>')) {
        const quoteLines: string[] = [];
        while (i < lines.length && lines[i].trim().startsWith('>')) {
          quoteLines.push(lines[i].replace(/^>\s*/, ''));
          i++;
        }
        const quoteText = quoteLines.join('\n');
        elements.push(
          <div key={`quote-${i}`} className="my-3 p-3.5 rounded-xl bg-indigo-950/30 border-l-4 border-indigo-500 text-xs text-indigo-200 flex items-start space-x-2.5">
            <Lightbulb className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <div className="leading-relaxed font-medium">{renderInlineFormatted(quoteText)}</div>
          </div>
        );
        continue;
      }

      // 5. Bullet points (* or - or numbered 1.)
      if (/^(\s*[-*]|\s*\d+\.)\s+/.test(line)) {
        const isNumbered = /^\s*\d+\.\s+/.test(line);
        const itemText = line.replace(/^(\s*[-*]|\s*\d+\.)\s+/, '').trim();

        elements.push(
          <div key={`li-${i}`} className="my-1.5 flex items-start space-x-2.5 pl-2 text-xs text-slate-200 leading-relaxed">
            <span className="mt-1 shrink-0">
              {isNumbered ? (
                <span className="w-4 h-4 rounded-full bg-slate-800 text-indigo-300 text-[10px] font-bold flex items-center justify-center border border-slate-700">
                  {line.match(/\d+/)?.[0]}
                </span>
              ) : (
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block" />
              )}
            </span>
            <div className="flex-1">{renderInlineFormatted(itemText)}</div>
          </div>
        );
        i++;
        continue;
      }

      // 6. Horizontal Rules (---)
      if (line.trim() === '---' || line.trim() === '***') {
        elements.push(<hr key={`hr-${i}`} className="my-4 border-slate-800" />);
        i++;
        continue;
      }

      // 7. Regular paragraph / text
      if (line.trim()) {
        elements.push(
          <p key={`p-${i}`} className="my-2 text-xs sm:text-sm text-slate-200 leading-relaxed">
            {renderInlineFormatted(line)}
          </p>
        );
      }

      i++;
    }

    return elements;
  };

  // Helper to normalize arrows and special functional dependency notation
  const cleanArrowsAndLatex = (str: string): string => {
    if (!str) return '';
    return str
      // Fix \rightarrow, \ightarrow, \\rightarrow, \to, -->, ->
      .replace(/\\+(r?ightarrow|to)/gi, ' → ')
      .replace(/\\+ightarrow/gi, ' → ')
      .replace(/\r+ightarrow/gi, ' → ')
      .replace(/\\+(leftarrow)/gi, ' ← ')
      .replace(/\\+(Rightarrow)/gi, ' ⇒ ')
      .replace(/\\+(Leftrightarrow)/gi, ' ⇔ ')
      .replace(/-->/g, ' → ')
      .replace(/(?<=[A-Za-z0-9_})\s])->(?=[A-Za-z0-9_(\s])/g, ' → ')
      .replace(/\s*→\s*/g, ' → ');
  };

  // Helper to render bold (**text**), code (`code`), citations ([Page X])
  const renderInlineFormatted = (text: string): React.ReactNode => {
    if (!text) return null;

    // First normalize any broken arrows in text
    const normalizedText = cleanArrowsAndLatex(text);

    // Split by citations like [Page X] or bold **text** or inline `code`
    const parts = normalizedText.split(/(\*\*.*?\*\*|`.*?`|\[Page\s*\d+\]|\$.*?\$)/g);

    return parts.map((part, index) => {
      // Bold
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={index} className="font-bold text-slate-100">
            {cleanArrowsAndLatex(part.slice(2, -2))}
          </strong>
        );
      }
      // Inline code
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={index} className="px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono text-[11px] border border-slate-700/60">
            {cleanArrowsAndLatex(part.slice(1, -1))}
          </code>
        );
      }
      // Math formula ($...$)
      if (part.startsWith('$') && part.endsWith('$')) {
        return (
          <span key={index} className="px-1.5 py-0.5 rounded bg-slate-900 font-mono text-[11px] text-amber-300 font-semibold border border-slate-800">
            {cleanArrowsAndLatex(part.slice(1, -1))}
          </span>
        );
      }
      // Citation ([Page X])
      if (/^\[Page\s*\d+\]$/i.test(part)) {
        return (
          <span key={index} className="inline-flex items-center px-2 py-0.5 mx-1 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
            {part}
          </span>
        );
      }

      return cleanArrowsAndLatex(part);
    });
  };

  return <div className="space-y-1">{renderBlocks()}</div>;
}
