'use client';

import { useEffect } from 'react';

export default function ErrorHandler() {
  useEffect(() => {
    // Suppress Chrome extension errors
    const originalError = console.error;
    console.error = function(message, ...args) {
      // Check if it's a Chrome extension error
      if (
        typeof message === 'string' &&
        (message.includes('A listener indicated an asynchronous response by returning true') ||
         message.includes('message channel closed before a response was received') ||
         message.includes('Extension context invalidated'))
      ) {
        // Silently ignore Chrome extension errors
        return;
      }
      // Log other errors normally
      originalError.apply(console, [message, ...args]);
    };

    // Handle uncaught promise rejections
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (
        event.reason?.message?.includes('A listener indicated an asynchronous response') ||
        event.reason?.message?.includes('message channel closed')
      ) {
        event.preventDefault();
        return;
      }
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    // Cleanup
    return () => {
      console.error = originalError;
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return null;
}