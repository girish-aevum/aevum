import React from 'react';

function BrandLogo() {
  return (
    <div className="flex items-center gap-3">
      <div className="relative h-11 w-11">
        <div className="absolute inset-0 rounded-full bg-brand-primary/25 blur-lg" />
        <div className="relative h-11 w-11 rounded-full bg-gradient-to-br from-brand-primary to-brand-secondary flex items-center justify-center shadow-[0_0_20px_rgba(102,126,234,0.35)]">
          <i className="fa-solid fa-dna text-white/95 text-lg" aria-hidden="true"></i>
          <span className="pointer-events-none absolute inset-0 rounded-full ring-2 ring-white/10 animate-ping" style={{ animationDuration: '2.4s' }} />
        </div>
      </div>
      <div className="leading-tight">
        <div className="text-[22px] md:text-2xl font-semibold tracking-tight bg-gradient-to-r from-brand-primary to-brand-secondary bg-clip-text text-transparent">
          Aevum
        </div>
        <div className="uppercase text-[10px] md:text-[11px] tracking-[0.24em] text-gray-300">
          Wellness AI Revolution
        </div>
      </div>
    </div>
  );
}

export default BrandLogo; 