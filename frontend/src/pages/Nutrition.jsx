import React from 'react';
import Navbar from '../components/Navbar';
import { FaAppleAlt } from 'react-icons/fa';

function Nutrition() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-green-100 dark:from-gray-900 dark:via-gray-900 dark:to-green-900 flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-12 flex flex-col items-center justify-center">
        <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-10 flex flex-col items-center">
          <FaAppleAlt className="text-green-500 text-6xl mb-4" />
          <h1 className="text-4xl font-bold text-green-600 mb-2 text-center">Nutrition</h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center mb-4">
            Welcome to your Nutrition dashboard. Track your meals, get personalized advice, and optimize your nutrition for better health.
          </p>
          <div className="mt-8 text-gray-400 text-center">(More features coming soon!)</div>
        </div>
      </main>
    </div>
  );
}

export default Nutrition; 