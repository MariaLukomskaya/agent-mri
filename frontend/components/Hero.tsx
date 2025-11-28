import React from 'react';
import { ScanSearch, Sparkles, X, Check } from 'lucide-react';

const Hero: React.FC = () => {
  return (
    <div className="bg-white rounded-3xl p-8 md:p-12 border border-gray-100 shadow-[0_4px_20px_rgba(0,0,0,0.02)] mb-8">
      <div className="max-w-3xl mb-12">
        <h1 className="text-3xl md:text-4xl font-semibold text-gray-900 tracking-tight mb-4">
          Visualise Agent Reasoning
        </h1>
        <p className="text-lg text-gray-500 font-light leading-relaxed">
          Watch a chaotic junior AI try to handle complex tasks, while Agent MRI scans for hallucinations, tool misuse, and logic failures in real-time.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 md:gap-16 border-t border-gray-100 pt-8">
        
        {/* Chaos Column */}
        <div>
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-orange-50 rounded-xl text-orange-600">
                    <Sparkles size={18} strokeWidth={2} />
                </div>
                <h3 className="font-medium text-gray-900 text-sm uppercase tracking-wide">The Chaos Intern</h3>
            </div>
            <ul className="space-y-4">
                <li className="flex items-start gap-3 text-[15px] text-gray-600 font-light">
                    <X size={16} className="text-orange-400 mt-1 shrink-0" />
                    <span>Hallucinates confident facts without sources</span>
                </li>
                <li className="flex items-start gap-3 text-[15px] text-gray-600 font-light">
                    <X size={16} className="text-orange-400 mt-1 shrink-0" />
                    <span>Misuses tools (calls shipping APIs for coding tasks)</span>
                </li>
                <li className="flex items-start gap-3 text-[15px] text-gray-600 font-light">
                    <X size={16} className="text-orange-400 mt-1 shrink-0" />
                    <span>Loses context and drifts from the objective</span>
                </li>
            </ul>
        </div>

        {/* MRI Column */}
        <div>
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-blue-50 rounded-xl text-blue-600">
                    <ScanSearch size={18} strokeWidth={2} />
                </div>
                <h3 className="font-medium text-gray-900 text-sm uppercase tracking-wide">Agent MRI Analysis</h3>
            </div>
            <ul className="space-y-4">
                <li className="flex items-start gap-3 text-[15px] text-gray-600 font-light">
                    <Check size={16} className="text-blue-500 mt-1 shrink-0" />
                    <span>Parses reasoning steps and tool invocations</span>
                </li>
                <li className="flex items-start gap-3 text-[15px] text-gray-600 font-light">
                    <Check size={16} className="text-blue-500 mt-1 shrink-0" />
                    <span>Tags risks like <span className="text-gray-900 font-medium">hallucination_risk</span> automatically</span>
                </li>
                <li className="flex items-start gap-3 text-[15px] text-gray-600 font-light">
                    <Check size={16} className="text-blue-500 mt-1 shrink-0" />
                    <span>Generates executive incident reports</span>
                </li>
            </ul>
        </div>

      </div>
    </div>
  );
};

export default Hero;