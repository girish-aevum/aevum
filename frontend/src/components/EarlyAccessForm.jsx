import React, { useState } from 'react';
import apiClient from '../apiClient';

const INTERESTS = [
  { value: 'NUTRITION', label: 'Nutrition & Diet' },
  { value: 'MENTAL_WELLNESS', label: 'Mental Wellness' },
  { value: 'HEALTHCARE', label: 'Healthcare & Medicine' },
  { value: 'DNA_PROFILE', label: 'DNA & Genetic Insights' },
  { value: 'AI_COMPANION', label: 'AI Health Companion' },
];

function EarlyAccessForm() {
  const [form, setForm] = useState({ full_name: '', email: '', phone_number: '', primary_interest: 'NUTRITION' });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setResult(null);
    try {
      const res = await apiClient.post('/dashboard/early-access/', form);
      setResult({ ok: true, message: res.data.message });
      setForm({ full_name: '', email: '', phone_number: '', primary_interest: 'NUTRITION' });
    } catch (err) {
      const apiMsg = err?.response?.data?.message || 'Submission failed';
      setResult({ ok: false, message: apiMsg });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="early" className="bg-white dark:bg-gray-900 py-20 transition-colors duration-300">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100">Ready to Transform Your Health?</h2>
          <p className="mt-4 text-xl text-gray-600 dark:text-gray-400">Join thousands who are already on their personalized wellness journey. Get early access to Aevum's comprehensive health insights.</p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-8 md:p-12 transition-colors duration-300">
          <form onSubmit={onSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Full Name</label>
                <input
                  name="full_name"
                  value={form.full_name}
                  onChange={onChange}
                  placeholder="Enter your full name"
                  required
                  className="w-full px-4 py-3 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-brand-primary focus:border-transparent outline-none transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email Address</label>
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={onChange}
                  placeholder="Enter your email"
                  required
                  className="w-full px-4 py-3 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-brand-primary focus:border-transparent outline-none transition-colors"
                />
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Phone Number (Optional)</label>
                <input
                  name="phone_number"
                  value={form.phone_number}
                  onChange={onChange}
                  placeholder="Enter your phone number"
                  className="w-full px-4 py-3 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-brand-primary focus:border-transparent outline-none transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Primary Interest</label>
                <select
                  name="primary_interest"
                  value={form.primary_interest}
                  onChange={onChange}
                  className="w-full px-4 py-3 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-brand-primary focus:border-transparent outline-none transition-colors"
                >
                  {INTERESTS.map(interest => (
                    <option key={interest.value} value={interest.value}>{interest.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="pt-4">
              <button
                disabled={submitting}
                className="w-full md:w-auto px-12 py-4 rounded-lg bg-brand-primary text-white font-semibold text-lg hover:bg-brand-primary/90 disabled:opacity-60 transition-colors"
              >
                {submitting ? 'Submitting...' : 'Get Early Access'}
              </button>
              
              {result && (
                <div className={`mt-4 p-4 rounded-lg ${result.ok ? 'bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300' : 'bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-300'}`}>
                  {result.message}
                </div>
              )}
            </div>

            <p className="text-sm text-gray-500 dark:text-gray-400 pt-2">
              By submitting this form, you agree to receive communications about Aevum Health. We respect your privacy and will never share your information.
            </p>
          </form>
        </div>
      </div>
    </section>
  );
}

export default EarlyAccessForm; 