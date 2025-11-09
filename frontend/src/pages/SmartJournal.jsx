import React, { useEffect, useState, useRef } from 'react';
import Navbar from '../components/Navbar';
import apiClient from '../apiClient';
import { useNavigate } from 'react-router-dom';

const MOODS = [
  { value: 1, emoji: '😞', label: 'Very Sad' },
  { value: 2, emoji: '😕', label: 'Sad' },
  { value: 3, emoji: '😐', label: 'Neutral' },
  { value: 4, emoji: '😊', label: 'Happy' },
  { value: 5, emoji: '😄', label: 'Very Happy' },
];

// Utility function to generate calendar days
const generateCalendarDays = (year, month) => {
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDay = firstDay.getDay(); // 0-6, 0 is Sunday

  const days = [];
  
  // Add empty slots for days before the first day of the month
  for (let i = 0; i < startingDay; i++) {
    days.push(null);
  }

  // Add actual days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    days.push(new Date(year, month, day));
  }

  return days;
};

function SmartJournal() {
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [streak, setStreak] = useState(null);
  const [reminders, setReminders] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quickEntry, setQuickEntry] = useState('');
  const [quickMood, setQuickMood] = useState(3);
  const [adding, setAdding] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [entryDetail, setEntryDetail] = useState(null);
  
  // Refs for dropdown containers
  const monthDropdownRef = useRef(null);
  const yearDropdownRef = useRef(null);

  // Entry form state
  const [form, setForm] = useState({
    title: '',
    content: '',
    mood_rating: 3,
    energy_level: 3,
    privacy_level: 'PRIVATE',
    is_favorite: false,
    is_draft: false,
    tag_names: [],
    tags: '', // for UI only
    category: '',
    template: '',
    location: '',
    weather: '',
  });
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const [categories, setCategories] = useState([]);
  const [templates, setTemplates] = useState([]);

  // Calendar State
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedMonth, setSelectedMonth] = useState(currentDate.getMonth());
  const [selectedYear, setSelectedYear] = useState(currentDate.getFullYear());
  const [isMonthDropdownOpen, setIsMonthDropdownOpen] = useState(false);
  const [isYearDropdownOpen, setIsYearDropdownOpen] = useState(false);
  const [monthEntries, setMonthEntries] = useState([]);

  // Add effect to handle outside clicks and escape key
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Check if click is outside month dropdown
      if (
        isMonthDropdownOpen && 
        monthDropdownRef.current && 
        !monthDropdownRef.current.contains(event.target)
      ) {
        setIsMonthDropdownOpen(false);
      }

      // Check if click is outside year dropdown
      if (
        isYearDropdownOpen && 
        yearDropdownRef.current && 
        !yearDropdownRef.current.contains(event.target)
      ) {
        setIsYearDropdownOpen(false);
      }
    };

    // Handle escape key
    const handleEscapeKey = (event) => {
      if (event.key === 'Escape') {
        setIsMonthDropdownOpen(false);
        setIsYearDropdownOpen(false);
      }
    };

    // Add event listeners
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscapeKey);

    // Cleanup event listeners
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isMonthDropdownOpen, isYearDropdownOpen]);

  // Months and Years for dropdown
  const MONTHS = [
    'January', 'February', 'March', 'April', 
    'May', 'June', 'July', 'August', 
    'September', 'October', 'November', 'December'
  ];
  // Years dynamically generated from 2020 to current year + 1
  const YEARS = Array.from(
    { length: new Date().getFullYear() - 2020 + 2 }, 
    (_, i) => 2020 + i
  );

  // Energy level symbols
  const ENERGY_SYMBOLS = {
    1: '🔋',   // Very Low
    2: '🔋🔋', // Low
    3: '🔋🔋🔋', // Moderate
    4: '🔋🔋🔋🔋', // High
    5: '🔋🔋🔋🔋🔋' // Very High
  };

  // Fetch entries for the selected month
  useEffect(() => {
    async function fetchMonthEntries() {
      try {
        const response = await apiClient.get('/smart-journal/entries/', {
          params: {
            start_date: `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-01`,
            end_date: `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-${new Date(selectedYear, selectedMonth + 1, 0).getDate()}`
          }
        });
        setMonthEntries(response.data.results || []);
      } catch (error) {
        console.error('Failed to fetch month entries:', error);
        setMonthEntries([]);
      }
    }

    fetchMonthEntries();
  }, [selectedMonth, selectedYear]);

  // Get mood for a specific date
  const getMoodForDate = (date) => {
    // Implement logic to get mood for a specific date
    // This would likely involve checking entries for the given date
    return null;
  };

  // Get mood and energy for a specific date
  const getDateDetails = (date) => {
    if (!date || !monthEntries || monthEntries.length === 0) return null;

    const dayEntries = monthEntries.filter(entry => {
      const entryDate = new Date(entry.entry_date);
      return entryDate.toDateString() === date.toDateString();
    });

    if (dayEntries.length === 0) return null;

    // If multiple entries on the same day, take the first one
    const entry = dayEntries[0];
    return {
      entry: entry,
      mood: MOODS.find(m => m.value === entry.mood_rating)?.emoji || '😐',
      energy: ENERGY_SYMBOLS[entry.energy_level] || ''
    };
  };

  // Navigation handlers
  const goToPreviousMonth = () => {
    let newMonth = selectedMonth - 1;
    let newYear = selectedYear;
    
    if (newMonth < 0) {
      newMonth = 11;
      newYear -= 1;
    }
    
    setSelectedMonth(newMonth);
    setSelectedYear(newYear);
  };

  const goToNextMonth = () => {
    let newMonth = selectedMonth + 1;
    let newYear = selectedYear;
    
    if (newMonth > 11) {
      newMonth = 0;
      newYear += 1;
    }
    
    setSelectedMonth(newMonth);
    setSelectedYear(newYear);
  };

  // Change month handler
  const changeMonth = (newMonth) => {
    setSelectedMonth(newMonth);
    setIsMonthDropdownOpen(false);
  };

  // Change year handler
  const changeYear = (newYear) => {
    setSelectedYear(newYear);
    setIsYearDropdownOpen(false);
  };

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [entriesRes, streakRes, remindersRes, insightsRes, categoriesRes, templatesRes] = await Promise.all([
          apiClient.get('/smart-journal/entries/?limit=5'),
          apiClient.get('/smart-journal/streak/'),
          apiClient.get('/smart-journal/reminders/'),
          apiClient.get('/smart-journal/insights/?limit=3'),
          apiClient.get('/smart-journal/categories/'),
          apiClient.get('/smart-journal/templates/'),
        ]);
        setEntries(entriesRes.data.results || []);
        setStreak(streakRes.data);
        setReminders(remindersRes.data.results || []);
        setInsights(insightsRes.data.results || []);
        setCategories(categoriesRes.data.results || categoriesRes.data || []);
        setTemplates(templatesRes.data.results || templatesRes.data || []);
      } catch (err) {}
      setLoading(false);
    }
    fetchData();
  }, []);

  const refreshEntries = async () => {
    const entriesRes = await apiClient.get('/smart-journal/entries/?limit=5');
    setEntries(entriesRes.data.results || []);
  };

  // Quick add entry (kept for fast logging)
  const handleQuickAdd = async () => {
    if (!quickEntry.trim()) return;
    setAdding(true);
    try {
      await apiClient.post('/smart-journal/entries/quick-create/', {
        content: quickEntry,
        mood_rating: quickMood,
      });
      setQuickEntry('');
      setQuickMood(3);
      await refreshEntries();
    } catch (err) {}
    setAdding(false);
  };

  // Full entry form submit
  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    setFormError('');
    try {
      await apiClient.post('/smart-journal/entries/create/', {
        title: form.title,
        content: form.content,
        mood_rating: form.mood_rating,
        energy_level: form.energy_level,
        privacy_level: form.privacy_level,
        is_favorite: form.is_favorite,
        is_draft: form.is_draft,
        tag_names: form.tags.split(',').map(t => t.trim()).filter(Boolean),
        category: form.category || null,
        template: form.template || null,
        location: form.location,
        weather: form.weather,
      });
      setShowModal(false);
      setForm({ 
        title: '',
        content: '',
        mood_rating: 3,
        energy_level: 3,
        privacy_level: 'PRIVATE',
        is_favorite: false,
        is_draft: false,
        tag_names: [],
        tags: '',
        category: '',
        template: '',
        location: '',
        weather: '',
      });
      await refreshEntries();
    } catch (err) {
      setFormError('Failed to create entry. Please try again.');
    }
    setFormLoading(false);
  };

  // Fetch entry detail when selectedEntry changes
  useEffect(() => {
    if (!selectedEntry) return setEntryDetail(null);
    
    apiClient.get(`/smart-journal/entries/${selectedEntry}/`)
      .then(res => {
        // Normalize data to handle potential object structures
        const entryData = res.data;
        
        // Ensure category is a string
        if (entryData.category && typeof entryData.category === 'object') {
          entryData.category = entryData.category.name || 'Uncategorized';
        }
        
        // Ensure tags are an array of strings
        if (entryData.tags && Array.isArray(entryData.tags)) {
          entryData.tags = entryData.tags.map(tag => 
            typeof tag === 'object' ? (tag.name || 'Unknown Tag') : tag
          );
        }
        
        setEntryDetail(entryData);
      })
      .catch(err => {
        console.error("Failed to fetch entry details:", err);
        setEntryDetail(null);
      });
  }, [selectedEntry]);

  // Close modal function
  const closeModal = () => {
    setSelectedEntry(null);
    setEntryDetail(null);
  };

  // Helper to group entries by date
  function groupEntriesByDate(entries) {
    const groups = {};
    entries.forEach(entry => {
      const date = entry.entry_date;
      if (!groups[date]) groups[date] = [];
      groups[date].push(entry);
    });
    // Sort dates descending
    return Object.entries(groups).sort((a, b) => new Date(b[0]) - new Date(a[0]));
  }

  // Helper to format date headers
  function formatDateHeader(dateStr) {
    const today = new Date();
    const entryDate = new Date(dateStr);
    const diff = (today.setHours(0,0,0,0) - entryDate.setHours(0,0,0,0)) / (1000*60*60*24);
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Yesterday';
    return entryDate.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
  }

  // Navigate to entries for a specific date
  const navigateToDateEntries = (date) => {
    // Format the date as YYYY-MM-DD
    const formattedDate = date instanceof Date 
      ? date.toISOString().slice(0, 10) 
      : date;
    
    // Navigate to journal entries with date filter
    navigate('/journal-entries', { 
      state: { 
        startDate: formattedDate,
        endDate: formattedDate 
      } 
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-brand-primary/10 dark:from-gray-900 dark:via-gray-900 dark:to-brand-primary/20 flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-10">
        <div className="flex space-x-8 max-w-6xl mx-auto">
          {/* Left Column - 30% Width */}
          <div className="w-1/3 space-y-8">
            {/* New Journal Entry Button */}
            <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-6">
              <button
                onClick={() => setShowModal(true)}
                className="w-full px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-2xl text-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
              >
                + New Journal Entry
              </button>
            </div>

            {/* Streak, Reminders, Milestones */}
            <div className="space-y-6">
              <div className="bg-gradient-to-br from-orange-100 via-white to-orange-200 dark:from-orange-900 dark:via-gray-900 dark:to-orange-800 rounded-2xl shadow-xl p-6 flex flex-col items-center border border-orange-200 dark:border-orange-800">
                <div className="text-5xl mb-2">🔥</div>
                <div className="text-lg font-semibold">Current Streak</div>
                <div className="text-3xl text-orange-600 font-extrabold drop-shadow">{streak?.current_streak || 0} days</div>
                <div className="text-xs text-gray-500 mt-2">Longest: {streak?.longest_streak || 0} days</div>
              </div>
              
              <div className="bg-gradient-to-br from-blue-100 via-white to-blue-200 dark:from-blue-900 dark:via-gray-900 dark:to-blue-800 rounded-2xl shadow-xl p-6 flex flex-col items-center border border-blue-200 dark:border-blue-800">
                <div className="text-4xl mb-2">⏰</div>
                <div className="text-lg font-semibold">Next Reminder</div>
                <div className="text-md text-blue-700 font-bold">
                  {reminders[0]?.reminder_time ? reminders[0].reminder_time : 'No reminders set'}
                </div>
                <div className="text-xs text-gray-500 mt-2">{reminders[0]?.title}</div>
              </div>
              
              <div className="bg-gradient-to-br from-green-100 via-white to-green-200 dark:from-green-900 dark:via-gray-900 dark:to-green-800 rounded-2xl shadow-xl p-6 flex flex-col items-center border border-green-200 dark:border-green-800">
                <div className="text-4xl mb-2">🏆</div>
                <div className="text-lg font-semibold">Milestones</div>
                <ul className="text-sm text-gray-700 dark:text-gray-300 mt-2 list-disc list-inside text-center">
                  {(streak?.milestones_achieved || []).slice(-3).map((m, i) => (
                    <li key={i} className="mb-1">{m.milestone} <span className="text-xs text-gray-400">({new Date(m.achieved_at).toLocaleDateString()})</span></li>
                  ))}
                  {(!streak?.milestones_achieved || streak.milestones_achieved.length === 0) && <li>No milestones yet</li>}
                </ul>
              </div>
            </div>
          </div>

          {/* Right Column - 70% Width */}
          <div className="w-2/3 space-y-8">
            {/* Monthly Calendar */}
            <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-700">
              {/* Month and Year Navigation */}
              <div className="flex items-center justify-between px-6 py-5 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                {/* Previous Month Button */}
                <button 
                  onClick={goToPreviousMonth}
                  className="text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>

                {/* Month and Year Display with Dropdowns */}
                <div className="flex items-center space-x-4">
                  {/* Month Dropdown */}
                  <div className="relative" ref={monthDropdownRef}>
                    <button 
                      onClick={() => setIsMonthDropdownOpen(!isMonthDropdownOpen)}
                      className="text-xl font-bold text-gray-800 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                    >
                      {MONTHS[selectedMonth]}
                    </button>
                    {isMonthDropdownOpen && (
                      <div className="absolute z-10 mt-2 w-48 bg-white rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {MONTHS.map((month, index) => (
                          <button
                            key={month}
                            onClick={() => changeMonth(index)}
                            className={`
                              w-full text-left px-4 py-2 
                              ${selectedMonth === index 
                                ? 'bg-indigo-100 text-indigo-600' 
                                : 'hover:bg-gray-100'}
                            `}
                          >
                            {month}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Year Dropdown */}
                  <div className="relative" ref={yearDropdownRef}>
                    <button 
                      onClick={() => setIsYearDropdownOpen(!isYearDropdownOpen)}
                      className="text-xl font-bold text-gray-800 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                    >
                      {selectedYear}
                    </button>
                    {isYearDropdownOpen && (
                      <div className="absolute z-10 mt-2 w-32 bg-white rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {YEARS.map((year) => (
                          <button
                            key={year}
                            onClick={() => changeYear(year)}
                            className={`
                              w-full text-left px-4 py-2 
                              ${selectedYear === year 
                                ? 'bg-indigo-100 text-indigo-600' 
                                : 'hover:bg-gray-100'}
                            `}
                          >
                            {year}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Next Month Button */}
            <button
                  onClick={goToNextMonth}
                  className="text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
            </button>
          </div>

              {/* Calendar Grid */}
              {loading ? (
                <div className="grid grid-cols-7 gap-1 p-1 opacity-50">
                  {[...Array(42)].map((_, index) => (
                    <div 
                      key={index} 
                      className="bg-gray-200 dark:bg-gray-700 rounded-md min-h-[80px] animate-pulse"
                    />
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-7 gap-1 p-1">
                {/* Weekday Headers */}
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div 
                    key={day} 
                      className="text-[0.6rem] font-semibold text-gray-400 text-center uppercase tracking-wider py-0.5"
                  >
                      {day.charAt(0)}
                  </div>
                ))}

                {/* Calendar Days */}
                {generateCalendarDays(selectedYear, selectedMonth).map((day, index) => {
                  const dateDetails = day ? getDateDetails(day) : null;
                  const isToday = day && day.toDateString() === new Date().toDateString();
                  const isFutureDate = day && day > new Date();
                  const hasEntry = dateDetails !== null;
                  const moodEmoji = hasEntry ? dateDetails.mood : null;
                  
                  // Count entries or energy levels for the day
                  const entriesCount = hasEntry ? 
                    (monthEntries.filter(entry => 
                      new Date(entry.entry_date).toDateString() === day.toDateString()
                    ).length) : 0;

                  return (
                    <div 
                      key={index} 
                      className={`
                        relative p-2 text-center rounded-md transition-all duration-300 ease-in-out
                        flex flex-col items-center justify-between
                        min-h-[80px] h-full
                        border border-gray-200 dark:border-gray-700
                        ${!day ? 'bg-gray-100 dark:bg-gray-700 opacity-50' : 'bg-white dark:bg-gray-800'}
                        ${isToday ? 'ring-2 ring-indigo-500 dark:ring-indigo-400 bg-indigo-50 dark:bg-indigo-900/30' : ''}
                        ${isFutureDate ? 'text-gray-400 dark:text-gray-500' : ''}
                        ${hasEntry ? 'cursor-pointer hover:bg-indigo-100 dark:hover:bg-indigo-900/50' : ''}
                        shadow-sm hover:shadow-md
                        group
                      `}
                      onClick={() => {
                        // If the day has an entry, navigate to entries for this date
                        if (hasEntry) {
                          navigateToDateEntries(day);
                        }
                      }}
                    >
                      {day && (
                        <>
                          <div className="flex justify-between w-full items-start">
                            <span 
                              className={`
                                text-lg font-bold
                                ${isToday ? 'text-indigo-600 dark:text-indigo-300' : 'text-gray-800 dark:text-white'}
                              `}
                            >
                              {day.getDate()}
                            </span>
                            
                            {/* Energy Indicator with Count */}
                            {entriesCount > 0 && (
                              <div className="flex items-center space-x-1">
                                <span 
                                  className="text-xs text-white bg-indigo-500 rounded-full px-2 py-0.5 inline-flex items-center"
                                  title={`${entriesCount} entries on this day`}
                                >
                                  🔋 × {entriesCount}
                                </span>
                              </div>
                            )}
                          </div>

                          {/* Mood Emoji Placement */}
                          <div className="absolute bottom-1 left-1 text-xl opacity-70">
                            {moodEmoji && (
                              <span 
                                title={`Mood: ${MOODS.find(m => m.emoji === moodEmoji)?.label}`}
                              >
                                {moodEmoji}
                              </span>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
              )}
            </div>

            {/* Recent Entries */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-brand-primary">Recent Entries</h2>
                <button
                  className="px-4 py-2 bg-brand-primary text-white rounded-lg shadow hover:bg-brand-secondary transition-colors font-medium text-sm"
                  onClick={() => navigate('/smart-journal/entries')}
                >
                  View All
                </button>
              </div>
              {entries.length === 0 && <div className="text-gray-500 dark:text-gray-400">No entries yet.</div>}
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {groupEntriesByDate(entries)
                    .flatMap(([date, group]) => group)
                    .slice(0, 2)
                    .map(entry => (
                      <div 
                        key={entry.entry_id} 
                        className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 flex flex-col gap-2 border border-brand-primary/10 hover:shadow-2xl transition-all duration-200 cursor-pointer"
                        onClick={() => setSelectedEntry(entry.entry_id)}
                      >
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-2xl drop-shadow">{MOODS.find(m => m.value === entry.mood_rating)?.emoji || '😐'}</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200 text-lg truncate">{entry.title || 'Untitled'}</span>
                          {entry.is_favorite && <span className="ml-2 text-yellow-400 text-lg">★</span>}
                        </div>
                        <div className="text-gray-600 dark:text-gray-400 text-base line-clamp-2 mb-1">{entry.content}</div>
                        <div className="flex gap-2 flex-wrap mt-1">
                          {entry.tags?.map(tag => (
                            <span key={tag.id} className="px-3 py-1 bg-brand-primary/10 text-brand-primary rounded-full text-xs font-medium shadow-sm">{tag.name}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>

            {/* AI Insights & Recommendations */}
            <div>
              <h2 className="text-2xl font-bold text-brand-primary mb-4 flex items-center gap-2">
                <span>AI Insights & Recommendations</span>
                <span className="inline-block px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 text-xs font-semibold ml-2">AI</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {insights.length === 0 && <div className="text-gray-500 dark:text-gray-400">No insights yet.</div>}
                {insights.map(insight => (
                  <div key={insight.id} className="bg-gradient-to-br from-yellow-50 via-white to-yellow-100 dark:from-yellow-900 dark:via-gray-900 dark:to-yellow-800 rounded-2xl shadow-lg p-6 border border-yellow-200 dark:border-yellow-800">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-yellow-500 text-xl">✨</span>
                      <span className="font-semibold text-lg text-yellow-800 dark:text-yellow-200">{insight.title}</span>
                    </div>
                    <div className="text-gray-700 dark:text-gray-300 mb-2">{insight.description}</div>
                    <div className="text-xs text-gray-400">{new Date(insight.generated_at).toLocaleDateString()}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Modal for Add Entry (unchanged) */}
          {showModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" style={{overflow: 'hidden'}}>
              <div className="relative w-full max-w-xl max-h-[90vh] bg-white/90 dark:bg-gray-900/90 rounded-3xl shadow-2xl p-0 flex flex-col border border-brand-primary/20 backdrop-blur-xl animate-fadeIn">
                <div className="flex items-center justify-between px-8 pt-8 pb-2">
                  <h2 className="flex-1 text-3xl font-extrabold text-brand-primary text-center tracking-tight">New Journal Entry</h2>
                  <button
                    className="ml-4 text-gray-400 hover:text-brand-primary text-3xl font-bold z-10"
                    onClick={() => setShowModal(false)}
                    aria-label="Close"
                    style={{lineHeight: 1}}
                  >
                    ×
                  </button>
                </div>
                <form onSubmit={handleFormSubmit} className="px-8 pb-8 grid grid-cols-1 md:grid-cols-2 gap-6 overflow-y-auto" style={{maxHeight: '65vh'}}>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title</label>
                      <input
                        type="text"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.title}
                        onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Content</label>
                      <textarea
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary min-h-[120px]"
                        value={form.content}
                        onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tags <span className="text-xs text-gray-400">(comma separated)</span></label>
                      <input
                        type="text"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.tags}
                        onChange={e => setForm(f => ({ ...f, tags: e.target.value }))}
                        placeholder="e.g. gratitude, health, work"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Location</label>
                      <input
                        type="text"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.location}
                        onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
                        placeholder="e.g. Home, Office, Park"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Weather</label>
                      <input
                        type="text"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.weather}
                        onChange={e => setForm(f => ({ ...f, weather: e.target.value }))}
                        placeholder="e.g. Sunny, Rainy, Cloudy"
                      />
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Mood</label>
                      <select
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.mood_rating}
                        onChange={e => setForm(f => ({ ...f, mood_rating: Number(e.target.value) }))}
                      >
                        {MOODS.map(mood => (
                          <option key={mood.value} value={mood.value}>
                            {mood.emoji} {mood.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Energy Level</label>
                      <select
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.energy_level}
                        onChange={e => setForm(f => ({ ...f, energy_level: Number(e.target.value) }))}
                      >
                        <option value={1}>🔋 Very Low</option>
                        <option value={2}>🔋 Low</option>
                        <option value={3}>🔋 Moderate</option>
                        <option value={4}>🔋 High</option>
                        <option value={5}>🔋 Very High</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                      <select
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.category}
                        onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                      >
                        <option value="">Select category</option>
                        {categories.map(cat => (
                          <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Template</label>
                      <select
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.template}
                        onChange={e => setForm(f => ({ ...f, template: e.target.value }))}
                      >
                        <option value="">Select template</option>
                        {templates.map(tpl => (
                          <option key={tpl.id} value={tpl.id}>{tpl.name}</option>
                        ))}
                      </select>
                    </div>
                    {/* Remove the Entry Date input */}
                    {/* <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Entry Date</label>
                      <input
                        type="date"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.entry_date}
                        onChange={e => setForm(f => ({ ...f, entry_date: e.target.value }))}
                      />
                    </div> */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Privacy</label>
                      <select
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        value={form.privacy_level}
                        onChange={e => setForm(f => ({ ...f, privacy_level: e.target.value }))}
                      >
                        <option value="PRIVATE">Private (Only Me)</option>
                        <option value="SHARED">Shared (Selected People)</option>
                        <option value="PUBLIC">Public (Anyone)</option>
                      </select>
                    </div>
                    <div className="flex items-center gap-4 mt-2">
                      <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                        <input type="checkbox" checked={form.is_favorite} onChange={e => setForm(f => ({ ...f, is_favorite: e.target.checked }))} /> Favorite
                      </label>
                      <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                        <input type="checkbox" checked={form.is_draft} onChange={e => setForm(f => ({ ...f, is_draft: e.target.checked }))} /> Draft
                      </label>
                    </div>
                  </div>
                  {formError && <div className="col-span-2 text-red-500 text-sm text-center">{formError}</div>}
                  <div className="col-span-2">
                    <button
                      type="submit"
                      className="w-full py-4 bg-gradient-to-r from-brand-primary to-brand-secondary text-white rounded-xl shadow-lg font-semibold text-xl hover:from-brand-secondary hover:to-brand-primary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-primary"
                      disabled={formLoading}
                    >
                      {formLoading ? 'Saving...' : 'Save Entry'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

      {/* Modal for Entry Detail */}
      {selectedEntry && entryDetail && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 overflow-y-auto"
          onClick={closeModal}
        >
          <div 
            className="relative w-full max-w-2xl max-h-[90vh] bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 m-4 overflow-y-auto"
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
              {/* Created At */}
              <div className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Created on: {new Date(entryDetail.created_at).toLocaleDateString(undefined, {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      <footer className="bg-white/50 dark:bg-gray-900/50 py-6 text-center text-gray-600 dark:text-gray-400">
        <div className="max-w-7xl mx-auto px-6">
          <p>© {new Date().getFullYear()} Aevum Health. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default SmartJournal; 