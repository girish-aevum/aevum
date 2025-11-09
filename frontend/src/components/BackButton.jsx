import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeftIcon } from '@heroicons/react/24/solid';

function BackButton({ 
  className = '', 
  label = 'Back', 
  destination = -1 
}) {
  const navigate = useNavigate();

  const handleBack = () => {
    if (typeof destination === 'number') {
      navigate(destination);
    } else {
      navigate(destination);
    }
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={handleBack}
      className={`
        flex 
        items-center 
        space-x-2 
        text-gray-700 
        dark:text-gray-300 
        hover:text-brand-primary 
        dark:hover:text-brand-primary 
        transition-colors 
        ${className}
      `}
    >
      <ArrowLeftIcon className="h-5 w-5" />
      <span>{label}</span>
    </motion.button>
  );
}

export default BackButton; 