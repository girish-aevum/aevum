import React from 'react';
import { motion } from 'framer-motion';
import * as FaIcons from 'react-icons/fa';

const FEATURES = [
  { 
    icon: <FaIcons.FaDna className="h-8 w-8" />, 
    title: 'Turn Your DNA Into Daily Action', 
    desc: 'Your genetic report shouldn\'t gather dust in a drawer. We translate complex genetic data into simple daily choices: "Your COMT gene means you metabolize caffeine slowly, so switch to green tea after 2 PM for better sleep." Track improvements in energy, mood, and health markers.' 
  },
  { 
    icon: <FaIcons.FaMobileAlt className="h-8 w-8" />, 
    title: 'Your Phone Becomes a Health Scanner', 
    desc: 'Measure your stress, heart rate variability, and energy levels with 30-second daily face scans powered by advanced AI. No wearables needed! Log voice, text, or video reflections for deeper insights. "When we detect elevated stress plus your genetic sensitivity to cortisol, you get instant interventions: Try box breathing for 3 minutes. Your FKBP5 gene responds well to this technique."' 
  },
  { 
    icon: <FaIcons.FaChartLine className="h-8 w-8" />, 
    title: 'Watch Your Body Optimize in Real-Time', 
    desc: 'See your biological age decrease, inflammation markers improve, and energy levels stabilize. Our predictive AI spots patterns weeks before you feel symptoms. Track Biological Age, Inflammation Control, and Energy Optimization.' 
  },
  { 
    icon: <FaIcons.FaGlobeAmericas className="h-8 w-8" />, 
    title: 'Wellness That Gets Your Culture', 
    desc: 'Wellness that honors your heritage. We craft routines that blend your cultural background with genetic optimization. Enjoy meal plans with traditional ingredients and movement routines inspired by ancestral wisdom. Honor your heritage while optimizing your health.' 
  },
  { 
    icon: <FaIcons.FaBolt className="h-8 w-8" />, 
    title: 'AI-Powered Personalization', 
    desc: 'Advanced AI algorithms analyze your genetic profile to provide hyper-personalized recommendations. From nutrition to fitness, every suggestion is tailored to your unique genetic makeup, ensuring maximum effectiveness.' 
  },
  { 
    icon: <FaIcons.FaBullseye className="h-8 w-8" />, 
    title: 'Precision Health Targeting', 
    desc: 'Identify and mitigate potential health risks before they become problems. Our comprehensive genetic analysis provides early warning signs and preventive strategies customized to your genetic predispositions.' 
  },
];

function Features() {
  return (
    <section id="features" className="bg-gray-50 dark:bg-gray-900 py-20 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100">Unlock Your Personalized Wellness Journey</h2>
          <p className="mt-4 text-xl text-gray-600 dark:text-gray-400">Comprehensive genetic testing and AI-powered insights to transform your health from the inside out.</p>
        </div>

        <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {FEATURES.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 dark:border-gray-700"
            >
              <div className="w-16 h-16 bg-brand-primary/10 rounded-xl flex items-center justify-center text-brand-primary mb-6">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">{feature.title}</h3>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Features; 