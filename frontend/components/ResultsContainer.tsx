import React, { useState } from 'react';
import { InternRunResponse, TimelineStep } from '../types';
import { MessageSquare, Activity, History, FileText, UserCheck, ScrollText } from 'lucide-react';
import MarkdownViewer from './MarkdownViewer';
import TimelineTab from './tabs/TimelineTab';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface ResultsContainerProps {
  data: InternRunResponse | null;
}

const ResultsContainer: React.FC<ResultsContainerProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!data) return null;

  const tabs = [
    { id: 0, label: 'Response', icon: <MessageSquare size={15} strokeWidth={2.5} /> },
    { id: 1, label: 'MRI Score', icon: <Activity size={15} strokeWidth={2.5} /> },
    { id: 2, label: 'Timeline', icon: <History size={15} strokeWidth={2.5} /> },
    { id: 3, label: 'Log View', icon: <ScrollText size={15} strokeWidth={2.5} /> },
    { id: 4, label: 'Report', icon: <FileText size={15} strokeWidth={2.5} /> },
    { id: 5, label: 'Feedback', icon: <UserCheck size={15} strokeWidth={2.5} /> },
  ];

  const generateTimelineMarkdown = (steps: TimelineStep[]): string => {
    if (!steps || steps.length === 0) return "_No structured timeline available for this run yet._";

    const lines: string[] = [];
    lines.push("## 🕒 Agent Timeline");
    lines.push("");
    lines.push("Each block below is one step in the agent run: thoughts, tool calls, memory ops, and the final answer.");
    lines.push("---");

    steps.forEach((step, idx) => {
      const stepId = step.step_id || idx + 1;
      const kind = step.type || "step";
      const label = step.label || "";
      const short = step.short || "";
      const text = step.text || "";
      const tags = step.tags || [];

      let header = `### Step ${stepId}: \`${kind}\``;
      if (label) {
        header += ` — ${label}`;
      }
      lines.push(header);
      lines.push("");

      if (short) {
        lines.push(`**What this step does:** ${short}`);
        lines.push("");
      }

      if (text) {
        lines.push("**Detail / excerpt:**");
        lines.push("");
        text.split('\n').forEach(line => {
          if (line.trim()) {
             lines.push(`> ${line}`);
          } else {
             lines.push(">");
          }
        });
        lines.push("");
      }

      if (tags && tags.length > 0) {
        const tagsStr = tags.map(t => `\`${t}\``).join(", ");
        lines.push(`**MRI tags:** ${tagsStr}`);
        lines.push("");
      }

      lines.push("---");
    });

    return lines.join("\n");
  };

  return (
    <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-gray-100 overflow-hidden min-h-[600px] flex flex-col">
      {/* Tab Header */}
      <div className="flex border-b border-gray-100 overflow-x-auto no-scrollbar px-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center gap-2.5 px-6 py-6 text-[13px] font-medium whitespace-nowrap transition-colors relative
              ${activeTab === tab.id ? 'text-gray-900' : 'text-gray-400 hover:text-gray-600'}
            `}
          >
            <span className={activeTab === tab.id ? 'opacity-100' : 'opacity-70'}>{tab.icon}</span>
            {tab.label}
            {activeTab === tab.id && (
              <span className="absolute bottom-0 left-6 right-6 h-[2px] bg-gray-900 rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-8 md:p-10 flex-grow bg-white">
        
        {/* Tab 1: Intern Answer */}
        {activeTab === 0 && (
          <div className="max-w-3xl animate-in fade-in duration-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-8 tracking-tight">
              Intern's Final Response
            </h3>
            <div className="prose prose-slate prose-sm max-w-none">
               <MarkdownViewer content={data.final_answer_md} />
            </div>
          </div>
        )}

        {/* Tab 2: MRI Score */}
        {activeTab === 1 && (
           <MRIScoreTab data={data} />
        )}

        {/* Tab 3: Timeline (Visual) */}
        {activeTab === 2 && (
          <div className="max-w-3xl animate-in fade-in duration-500">
            <TimelineTab steps={data.timeline_steps} />
          </div>
        )}

        {/* Tab 4: Log View (Markdown) */}
        {activeTab === 3 && (
          <div className="max-w-3xl animate-in fade-in duration-500">
            <MarkdownViewer content={generateTimelineMarkdown(data.timeline_steps)} />
          </div>
        )}

        {/* Tab 5: Incident Report */}
        {activeTab === 4 && (
          <div className="max-w-3xl animate-in fade-in duration-500">
            <MarkdownViewer content={data.report_markdown} />
          </div>
        )}

        {/* Tab 6: Manager Feedback */}
        {activeTab === 5 && (
          <div className="max-w-3xl animate-in fade-in duration-500">
            <MarkdownViewer content={data.critic_markdown} />
          </div>
        )}

      </div>
    </div>
  );
};

// Sub-component for MRI Score
const MRIScoreTab: React.FC<{ data: InternRunResponse }> = ({ data }) => {
  const score = data.risk.score;
  const riskColor = score < 30 ? '#10B981' : score < 70 ? '#F59E0B' : '#EF4444'; 
  const chartData = [
    { name: 'Risk', value: score },
    { name: 'Safe', value: 100 - score },
  ];

  return (
    <div className="grid md:grid-cols-2 gap-16 animate-in fade-in duration-500 items-center">
      
      {/* Left: Score Visual */}
      <div className="flex flex-col items-center justify-center p-10 bg-gray-50/50 rounded-3xl border border-gray-100">
        <h3 className="text-gray-400 font-medium mb-8 uppercase tracking-widest text-[11px]">Risk Score Analysis</h3>
        <div className="relative w-56 h-56">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={75}
                outerRadius={85}
                startAngle={90}
                endAngle={-270}
                dataKey="value"
                stroke="none"
                cornerRadius={10}
                paddingAngle={5}
              >
                <Cell key="risk" fill={riskColor} />
                <Cell key="safe" fill="#E5E7EB" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
             <span className="text-5xl font-light text-gray-900 tracking-tighter">{score}</span>
             <span className={`text-[13px] font-medium px-3 py-1 rounded-full mt-2 ${
                data.risk.level === 'Low' ? 'bg-green-100 text-green-700' : 
                data.risk.level === 'Medium' ? 'bg-amber-100 text-amber-700' : 
                'bg-red-100 text-red-700'
             }`}>
               {data.risk.level}
             </span>
          </div>
        </div>
      </div>

      {/* Right: Summary Stats */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-8 tracking-tight">Run Summary</h3>
        
        <div className="grid grid-cols-2 gap-6 mb-10">
          <div className="p-5 rounded-2xl border border-gray-100 bg-white shadow-sm">
            <span className="block text-3xl font-light text-gray-900 tracking-tight">{data.summary.total_steps}</span>
            <span className="text-[11px] text-gray-400 font-medium uppercase tracking-wider mt-1">Total Steps</span>
          </div>
          <div className="p-5 rounded-2xl border border-gray-100 bg-white shadow-sm">
            <span className="block text-3xl font-light text-red-500 tracking-tight">{data.summary.flagged_steps}</span>
            <span className="text-[11px] text-gray-400 font-medium uppercase tracking-wider mt-1">Issues Detected</span>
          </div>
        </div>

        <h4 className="text-[13px] font-medium text-gray-500 uppercase tracking-wider mb-4">Failure Modes</h4>
        <div className="space-y-3">
          {Object.entries(data.summary.by_failure_type).map(([key, count]) => (
            <div key={key} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 transition-colors">
               <div className="flex items-center gap-3">
                 <div className="w-1.5 h-1.5 rounded-full bg-red-400"></div>
                 <span className="text-[14px] text-gray-700 capitalize font-normal">{key.replace(/_/g, ' ')}</span>
               </div>
               <span className="text-[14px] text-gray-900 font-medium">{count}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default ResultsContainer;