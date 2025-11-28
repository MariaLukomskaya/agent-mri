import React from 'react';
import { ChaosMode } from '../types';
import { Play, Loader2, AlertCircle, CheckCircle2, ChevronDown } from 'lucide-react';

interface ControlCardProps {
  task: string;
  setTask: (t: string) => void;
  mode: ChaosMode;
  setMode: (m: ChaosMode) => void;
  onRun: () => void;
  status: 'idle' | 'running' | 'done' | 'error';
}

const ControlCard: React.FC<ControlCardProps> = ({ 
  task, setTask, mode, setMode, onRun, status 
}) => {
  return (
    <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] p-8 border border-gray-100 mb-8">
      
      <div className="flex flex-col md:flex-row gap-8 mb-10">
        {/* Left: Task Input */}
        <div className="flex-grow md:w-2/3">
          <label className="block text-[13px] font-medium text-gray-500 uppercase tracking-wider mb-3">
            Task Instruction
          </label>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            className="w-full min-h-[120px] p-5 bg-white border border-gray-200 rounded-2xl text-gray-900 text-[15px] font-light focus:outline-none focus:ring-4 focus:ring-gray-100 focus:border-gray-300 transition-all resize-none placeholder:text-gray-300 shadow-sm"
            placeholder="Describe the task for the intern..."
          />
        </div>

        {/* Right: Chaos Mode */}
        <div className="md:w-1/3 min-w-[250px]">
          <label className="block text-[13px] font-medium text-gray-500 uppercase tracking-wider mb-3">
            Simulation Mode
          </label>
          <div className="relative group">
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as ChaosMode)}
              className="w-full appearance-none p-5 bg-white border border-gray-200 rounded-2xl text-gray-900 text-[15px] font-medium focus:outline-none focus:ring-4 focus:ring-gray-100 focus:border-gray-300 transition-all cursor-pointer shadow-sm hover:border-gray-300"
            >
              <option value="default">Default Behavior</option>
              <option value="hallucination">High Hallucination</option>
              <option value="tool_misuse">Tool Misuse</option>
              <option value="memory_loss">Context Loss</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-5 text-gray-400 group-hover:text-gray-600 transition-colors">
              <ChevronDown size={18} />
            </div>
          </div>
          <p className="mt-3 text-[13px] text-gray-400 font-light leading-relaxed">
            Determines the type of errors the intern is prone to making during this run.
          </p>
        </div>
      </div>

      {/* Action Area */}
      <div className="flex flex-col items-center">
        <button
          onClick={onRun}
          disabled={status === 'running' || !task}
          className={`
            w-full max-w-sm h-14 rounded-full flex items-center justify-center gap-3 text-[15px] font-medium transition-all duration-300
            ${status === 'running' 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-gray-900 hover:bg-black text-white shadow-lg shadow-gray-200 active:scale-[0.98]'}
            disabled:opacity-70
          `}
        >
          {status === 'running' ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Play fill="currentColor" size={16} />
              <span>Run Simulation</span>
            </>
          )}
        </button>

        {/* Status Text */}
        <div className="mt-6 h-6">
          {status === 'running' && (
             <span className="flex items-center gap-2 text-sm text-gray-500 font-medium animate-pulse">
                Running logic trace...
             </span>
          )}
          {status === 'done' && (
            <span className="flex items-center gap-2 text-sm text-green-600 font-medium">
              <CheckCircle2 size={16} />
              Analysis Complete
            </span>
          )}
          {status === 'error' && (
            <span className="flex items-center gap-2 text-sm text-red-500 font-medium">
              <AlertCircle size={16} />
              Simulation failed
            </span>
          )}
        </div>
      </div>

    </div>
  );
};

export default ControlCard;