import React from 'react';

const MarkdownViewer: React.FC<{ content: string; className?: string }> = ({ content, className }) => {
  const lines = content.split('\n');
  
  return (
    <div className={`space-y-4 text-gray-700 leading-relaxed font-light ${className}`}>
      {lines.map((line, idx) => {
        // Headers
        if (line.startsWith('## ')) return <h3 key={idx} className="text-lg font-medium text-gray-900 mt-8 mb-3 tracking-tight">{line.replace('## ', '')}</h3>;
        if (line.startsWith('# ')) return <h2 key={idx} className="text-xl font-semibold text-gray-900 mb-6 tracking-tight">{line.replace('# ', '')}</h2>;
        
        // Horizontal Rule
        if (line.trim() === '---') return <hr key={idx} className="my-6 border-gray-200" />;

        // Blockquotes
        if (line.startsWith('> ')) return <div key={idx} className="border-l-[3px] border-gray-200 pl-4 py-1 my-4 text-gray-500 italic text-[15px]">{line.replace('> ', '')}</div>;
        
        // List items with bolding support
        if (line.startsWith('- ')) {
            const text = line.replace('- ', '');
            // simple bold parser
            const parts = text.split(/(\*\*.*?\*\*)/g);
            return (
                <div key={idx} className="flex items-start gap-3 ml-2">
                    <span className="block w-1.5 h-1.5 mt-2 rounded-full bg-gray-300 shrink-0" />
                    <span className="text-[15px]">
                        {parts.map((part, i) => 
                            part.startsWith('**') ? <strong key={i} className="font-semibold text-gray-900">{part.replace(/\*\*/g, '')}</strong> : part
                        )}
                    </span>
                </div>
            );
        }

        // Numbered lists
        if (/^\d+\./.test(line)) {
            const [num, ...rest] = line.split('.');
            const text = rest.join('.').trim();
            const parts = text.split(/(\*\*.*?\*\*)/g);
            return (
                <div key={idx} className="flex items-start gap-3 ml-2">
                     <span className="text-gray-400 font-medium text-[15px] w-4">{num}.</span>
                     <span className="text-[15px]">
                        {parts.map((part, i) => 
                            part.startsWith('**') ? <strong key={i} className="font-semibold text-gray-900">{part.replace(/\*\*/g, '')}</strong> : part
                        )}
                     </span>
                </div>
            );
        }

        // Table simulation (very basic)
        if (line.startsWith('|')) {
            const cols = line.split('|').filter(c => c.trim() !== '');
            if (line.includes('---')) return null; // skip separator
            const isHeader = lines[idx + 1]?.includes('---');
            return (
                <div key={idx} className={`grid grid-cols-3 gap-6 py-3 text-[14px] ${isHeader ? "border-b border-gray-200 font-medium text-gray-900" : "text-gray-600 border-b border-gray-50"}`}>
                    {cols.map((c, i) => <span key={i}>{c}</span>)}
                </div>
            )
        }

        // Empty lines
        if (line.trim() === '') return <div key={idx} className="h-1"></div>;
        
        // Regular paragraph with bold support
        const parts = line.split(/(\*\*.*?\*\*)/g);
        return (
            <p key={idx} className="text-[15px]">
                {parts.map((part, i) => 
                    part.startsWith('**') ? <strong key={i} className="font-semibold text-gray-900">{part.replace(/\*\*/g, '')}</strong> : part
                )}
            </p>
        );
      })}
    </div>
  );
};

export default MarkdownViewer;