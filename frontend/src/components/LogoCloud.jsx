import React from 'react';

function LogoCloud() {
  const partners = [
    'Stanford Medicine', 'Mayo Clinic', 'Johns Hopkins', 'Harvard Medical', 'MIT Labs', 'NIH Research'
  ];
  
  return (
    <section id="logos" className="bg-white dark:bg-gray-900 py-16 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h3 className="text-lg font-medium text-gray-500 dark:text-gray-400">Trusted by leading healthcare institutions worldwide</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 items-center">
          {partners.map((partner, index) => (
            <div key={index} className="text-center">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
                <span className="text-gray-600 dark:text-gray-300 font-medium text-sm">{partner}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default LogoCloud; 