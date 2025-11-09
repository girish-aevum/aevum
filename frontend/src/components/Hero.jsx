import React from 'react';
import { motion } from 'framer-motion';

function Hero() {
  return (
    <>
      {/* Main Hero Section */}
      <section className="bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-16 md:py-24 relative overflow-hidden transition-colors duration-300">
        <div className="absolute inset-0 bg-gradient-to-r from-brand-primary/5 via-transparent to-brand-secondary/5 dark:from-brand-primary/10 dark:via-transparent dark:to-brand-secondary/10"></div>
        <div className="max-w-6xl mx-auto px-6 relative">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-4xl md:text-5xl lg:text-7xl font-bold bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 dark:from-gray-100 dark:via-gray-200 dark:to-gray-100 bg-clip-text text-transparent leading-tight mb-6"
            >
              YOUR GENES HAVE SECRETS WE SPEAK THEIR LANGUAGE
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-4xl mx-auto leading-relaxed mb-10"
            >
              We unlock true wellness by integrating your unique DNA, cultural heritage, and daily rhythms into a personalized plan for your mind, body, and spirit.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <a href="#early" className="px-8 py-4 bg-gradient-to-r from-brand-primary to-brand-secondary text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-brand-primary/25 transform hover:-translate-y-0.5 transition-all duration-300">
                GET EARLY ACCESS
              </a>
              <a href="#features" className="px-8 py-4 border-2 border-brand-primary text-brand-primary hover:bg-brand-primary hover:text-white hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-300 rounded-xl">
                Learn More
              </a>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Unique DNA Integration Section */}
      <section className="bg-gradient-to-r from-brand-primary via-purple-600 to-brand-secondary text-white py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10 dark:bg-black/20"></div>
        <div className="max-w-6xl mx-auto px-6 relative">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6 leading-tight">
                Stop Guessing. Start Thriving.
              </h2>
              <p className="text-lg mb-8 text-white/90 leading-relaxed">
                Aevum translates your unique DNA and real-time body signals into actionable wellness advice. Unlike generic apps, we seamlessly integrate your genetic blueprint, cultural heritage, and daily biomarkers.
              </p>
              <a href="#early" className="inline-block px-8 py-4 bg-white text-brand-primary font-semibold rounded-xl hover:bg-gray-100 hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-300">
                Know more
              </a>
            </div>
            <div className="bg-white/10 dark:bg-white/5 rounded-2xl p-8 backdrop-blur border border-white/20 shadow-2xl">
              <div className="text-center">
                <div className="text-5xl font-bold mb-3">98%</div>
                <div className="text-white/80 text-lg">Accuracy Rate</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Personalized Outcomes Section */}
      <section className="bg-gradient-to-r from-brand-secondary via-indigo-600 to-brand-primary text-white py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10 dark:bg-black/20"></div>
        <div className="max-w-6xl mx-auto px-6 relative">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="bg-white/10 dark:bg-white/5 rounded-2xl p-8 backdrop-blur border border-white/20 shadow-2xl">
              <div className="text-center">
                <div className="text-5xl font-bold mb-3">50+</div>
                <div className="text-white/80 text-lg">Cultures Supported</div>
              </div>
            </div>
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6 leading-tight">
                Personalized Outcomes
              </h2>
              <p className="text-lg mb-8 text-white/90 leading-relaxed">
                We're designed to deliver significantly better outcomes because your plan perfectly aligns with your unique biology and lifestyle. No more one-size-fits-all approaches.
              </p>
              <a href="#early" className="inline-block px-8 py-4 bg-white text-brand-primary font-semibold rounded-xl hover:bg-gray-100 hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-300">
                Start Here
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="bg-gradient-to-br from-white via-gray-50 to-blue-50 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800 py-16 transition-colors duration-300">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { number: "10K+", text: "DNA Profiles" },
              { number: "95%", text: "Accuracy Rate" },
              { number: "24/7", text: "Support" },
              { number: "24+", text: "Years of Genomics Experience" }
            ].map((item, index) => (
              <div key={index} className="text-center bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 border border-gray-100 dark:border-gray-700">
                <div className="text-2xl md:text-3xl font-bold text-brand-primary mb-2">{item.number}</div>
                <div className="text-gray-600 dark:text-gray-300 text-sm leading-tight">{item.text}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

export default Hero; 