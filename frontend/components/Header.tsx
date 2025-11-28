import React from 'react';
import { Brain } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur-xl border-b border-gray-100 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="text-gray-900">
            <Brain strokeWidth={1.5} size={24} />
          </div>
          <span className="font-medium text-gray-900 text-base tracking-tight">Agent MRI</span>
        </div>
        
        <div className="flex items-center gap-8">
          <nav className="hidden md:flex items-center gap-6">
            <a href="#" className="text-[13px] font-medium text-gray-500 hover:text-gray-900 transition-colors">Documentation</a>
            <a href="#" className="text-[13px] font-medium text-gray-500 hover:text-gray-900 transition-colors">GitHub</a>
          </nav>
          <div className="h-4 w-px bg-gray-200 hidden md:block"></div>
          <span className="px-2.5 py-1 bg-gray-100/80 text-gray-500 text-[11px] font-medium rounded-md uppercase tracking-wide">
            Demo Environment
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;