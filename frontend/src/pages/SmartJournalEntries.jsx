import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import apiClient from '../apiClient';
import { useNavigate, useLocation } from 'react-router-dom';

const MOODS = [
  { value: 1, emoji: '😞', label: 'Very Sad' },
  { value: 2, emoji: '😕', label: 'Sad' },
  { value: 3, emoji: '😐', label: 'Neutral' },
  { value: 4, emoji: '😊', label: 'Happy' },
  { value: 5, emoji: '😄', label: 'Very Happy' },
];

function groupEntriesByDate(entries) {
  const groups = {};
  entries.forEach(entry => {
    const date = entry.entry_date;
    if (!groups[date]) groups[date] = [];
    groups[date].push(entry);
  });
  return Object.entries(groups).sort((a, b) => new Date(b[0]) - new Date(a[0]));
}

function formatDateHeader(dateStr) {
  const today = new Date();
  const entryDate = new Date(dateStr);
  const diff = (today.setHours(0,0,0,0) - entryDate.setHours(0,0,0,0)) / (1000*60*60*24);
  if (diff === 0) return 'Today';
  if (diff === 1) return 'Yesterday';
  return entryDate.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
}

function SmartJournalEntries() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [entryDetail, setEntryDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  // Initialize date filters from navigation state
  useEffect(() => {
    // Check if there's a state passed from calendar navigation
    const navigationState = location.state || {};
    
    if (navigationState.startDate) {
      setStartDate(navigationState.startDate);
      setEndDate(navigationState.startDate);
      
      // Clear the location state to prevent reusing it
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, navigate]);

  // Fetch entries with filters
  useEffect(() => {
    async function fetchEntries() {
      setLoading(true);
      try {
        const params = {};
        if (search) params.search = search;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        
        const res = await apiClient.get('/smart-journal/entries/', { params });
        setEntries(res.data.results || res.data || []);
      } catch (err) {
        console.error("Failed to fetch entries:", err);
      }
      setLoading(false);
    }
    
    fetchEntries();
  }, [search, startDate, endDate]);

  // Fetch entry detail when selectedEntry changes
  useEffect(() => {
    if (!selectedEntry) return setEntryDetail(null);
    
    setDetailLoading(true);
    apiClient.get(`/smart-journal/entries/${selectedEntry}/`)
      .then(res => {
        // Ensure data is valid before setting
        const entryData = res.data || {};
        
        // Normalize category and tags
        if (entryData.category && typeof entryData.category === 'object') {
          entryData.category = entryData.category.name || 'Uncategorized';
        }
        
        if (entryData.tags && Array.isArray(entryData.tags)) {
          entryData.tags = entryData.tags.map(tag => 
            typeof tag === 'object' ? (tag.name || 'Unknown Tag') : tag
          );
        }
        
        setEntryDetail(entryData);
        setDetailLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch entry details:", err);
        setEntryDetail(null);
        setDetailLoading(false);
      });
  }, [selectedEntry]);

  // Close modal
  const closeModal = () => {
    setSelectedEntry(null);
    setEntryDetail(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      <Navbar />
      <main className="container mx-auto max-w-6xl px-4 py-6 flex-grow">
        {/* Compact Header and Search */}
        <div className="mb-6 flex items-center space-x-4">
          <button
            onClick={() => navigate('/smart-journal')}
            className="text-gray-500 hover:text-brand-primary transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          
          <div className="flex-grow flex space-x-2">
            <div className="relative flex-grow">
            <input
              type="text"
                placeholder="Search entries..."
              value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-2 rounded-lg bg-white border border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
            />
              <svg xmlns="http://www.w3.org/2000/svg" className="absolute left-2 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-1/4 px-2 py-2 rounded-lg bg-white border border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
            />
            
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-1/4 px-2 py-2 rounded-lg bg-white border border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
            />
            
            <button
              onClick={() => {/* Trigger search */}}
              className="bg-brand-primary text-white px-4 py-2 rounded-lg hover:bg-brand-secondary transition-colors"
            >
              Search
            </button>
          </div>
        </div>

        {/* Entries List in 3 Columns */}
        {loading ? (
          <div className="grid grid-cols-3 gap-4">
            {[1,2,3].map(i => (
              <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
            ))}
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-10 text-gray-500 dark:text-gray-400">
            No journal entries found
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {groupEntriesByDate(entries).map(([date, dayEntries]) => (
              <div key={date} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">
                  {formatDateHeader(date)}
                </div>
                <div className="space-y-2">
                  {dayEntries.slice(0, 3).map(entry => (
                    <div 
                      key={entry.entry_id}
                      onClick={() => setSelectedEntry(entry.entry_id)}
                      className="flex items-start space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg cursor-pointer transition-colors"
                    >
                      <span className="text-xl mt-1">
                        {MOODS.find(m => m.value === entry.mood_rating)?.emoji || '😐'}
                      </span>
                      <div className="flex-grow overflow-hidden">
                        <div className="flex justify-between items-center">
                          <h3 className="font-medium text-gray-800 dark:text-gray-200 truncate text-sm">
                            {entry.title || 'Untitled Entry'}
                          </h3>
                          {entry.is_favorite && (
                            <span className="text-yellow-500 text-xs ml-2">★</span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          {entry.content_preview || 'No content'}
                        </p>
                      </div>
                    </div>
                  ))}
                  {dayEntries.length > 3 && (
                    <div className="text-center text-xs text-gray-500 dark:text-gray-400 pt-2">
                      +{dayEntries.length - 3} more entries
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
      
      <footer className="bg-white/50 dark:bg-gray-900/50 py-6 text-center text-gray-600 dark:text-gray-400">
        <div className="max-w-7xl mx-auto px-6">
          <p>© {new Date().getFullYear()} Aevum Health. All rights reserved.</p>
        </div>
      </footer>

      {/* Entry Detail Modal */}
      {selectedEntry && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 overflow-y-auto"
          onClick={closeModal}
        >
          <div 
            className="relative w-full max-w-2xl max-h-[90vh] bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 m-4 overflow-y-auto border border-gray-200 dark:border-gray-700"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              className="absolute top-4 right-4 text-gray-500 hover:text-brand-primary dark:hover:text-brand-secondary transition-colors"
              onClick={closeModal}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {detailLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-brand-primary dark:border-brand-secondary"></div>
              </div>
            ) : entryDetail ? (
              <>
                {/* Entry Header */}
                <div className="mb-6">
                  <div className="flex justify-between items-center">
                    <h2 className="text-3xl font-bold text-brand-primary dark:text-brand-secondary">
                      {entryDetail.title || 'Untitled Entry'}
                    </h2>
                    <div className="flex items-center space-x-2">
                      <span className="text-3xl">
                        {MOODS.find(m => m.value === entryDetail.mood_rating)?.emoji || '😐'}
                      </span>
                      {entryDetail.is_favorite && (
                        <span className="text-yellow-500 text-2xl">★</span>
                      )}
                    </div>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 mt-2">
                    {new Date(entryDetail.entry_date).toLocaleDateString(undefined, {
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric'
                    })}
                  </p>
                </div>

                {/* Entry Content */}
                <div className="prose dark:prose-invert max-w-none text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-700 p-6 rounded-xl mb-6 shadow-inner">
                  <p>{entryDetail.content}</p>
                </div>

                {/* Additional Details */}
                <div className="grid grid-cols-2 gap-4 p-6 bg-gray-100 dark:bg-gray-700 rounded-xl text-sm shadow-inner">
                  {entryDetail.category && (
                    <div className="text-gray-700 dark:text-gray-300">
                      <strong className="text-brand-primary dark:text-brand-secondary">Category:</strong>{' '}
                      {typeof entryDetail.category === 'object' 
                        ? (entryDetail.category.name || 'Uncategorized') 
                        : entryDetail.category}
                    </div>
                  )}
                  {entryDetail.location && (
                    <div className="text-gray-700 dark:text-gray-300">
                      <strong className="text-brand-primary dark:text-brand-secondary">Location:</strong>{' '}
                      {entryDetail.location}
                    </div>
                  )}
                  <div className="text-gray-700 dark:text-gray-300">
                    <strong className="text-brand-primary dark:text-brand-secondary">Energy Level:</strong>{' '}
                    {entryDetail.energy_level}/5
                  </div>
                  {entryDetail.tags && (
                    <div className="text-gray-700 dark:text-gray-300">
                      <strong className="text-brand-primary dark:text-brand-secondary">Tags:</strong>{' '}
                      {Array.isArray(entryDetail.tags) 
                        ? entryDetail.tags.join(', ') 
                        : (entryDetail.tags.map ? entryDetail.tags.map(tag => tag.name || tag).join(', ') : 'No tags')}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="text-center text-gray-500 dark:text-gray-400 py-12">
                Unable to load entry details
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default SmartJournalEntries; 