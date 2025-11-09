import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Features from '../components/Features';
import LogoCloud from '../components/LogoCloud';
import EarlyAccessForm from '../components/EarlyAccessForm';
import FAQ from '../components/FAQ';

function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 transition-colors duration-300">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <LogoCloud />
        <EarlyAccessForm />
        <FAQ />
      </main>
      <footer className="bg-gray-50 dark:bg-gray-800 py-12 text-center text-gray-600 dark:text-gray-400 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-6">
          <p>© {new Date().getFullYear()} Aevum Health. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default Home; 