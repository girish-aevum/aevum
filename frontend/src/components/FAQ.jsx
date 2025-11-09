import React from 'react';

const FAQS = [
  { 
    q: 'Is my data private and secure?', 
    a: 'Absolutely. We follow strict data protection protocols. Your genetic information is encrypted, stored securely in NABL and CAP-accredited labs, and never sold. You maintain complete ownership and control of your data.' 
  },
  { 
    q: 'Who can benefit from Aevum?', 
    a: 'Anyone seeking to optimize their health journey. From individuals wanting personalized wellness insights to caregivers managing family health, our platform provides comprehensive, science-backed genetic analysis for all.' 
  },
  { 
    q: 'How accurate are your genetic insights?', 
    a: 'We pride ourselves on 95%+ accuracy. Our advanced sequencing technology and rigorous quality controls ensure precise genetic analysis. Each report is processed in certified laboratories and reviewed by expert genetic counselors.' 
  },
  { 
    q: 'What makes Aevum different from other genetic tests?', 
    a: 'Unlike generic tests, we integrate your unique DNA, cultural heritage, and daily biomarkers. Our AI-powered platform translates complex genetic data into actionable, personalized recommendations that evolve with your lifestyle.' 
  },
  { 
    q: 'How quickly will I get my results?', 
    a: 'After submitting your sample, you\'ll receive a comprehensive digital report within 2-3 weeks. Each report includes a personalized genetic counseling session to help you understand and act on your insights.' 
  },
  { 
    q: 'Can I trust the health recommendations?', 
    a: 'Absolutely. Our recommendations are developed by geneticists, nutritionists, and AI experts. We combine cutting-edge scientific research with machine learning to provide hyper-personalized, evidence-based health strategies.' 
  },
];

function FAQ() {
  return (
    <section id="faq" className="bg-gray-50 dark:bg-gray-900 py-20 transition-colors duration-300">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100">Ready to Transform Your Health?</h2>
          <p className="mt-4 text-xl text-gray-600 dark:text-gray-400">Get answers to your most pressing questions about personalized genetic wellness.</p>
        </div>
        
        <div className="space-y-6">
          {FAQS.map((faq, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-6 md:p-8 shadow-sm border border-gray-100 dark:border-gray-700 transition-colors duration-300">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">{faq.q}</h3>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FAQ; 