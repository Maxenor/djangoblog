// Analytics tracking script
(function() {
    'use strict';
    
    let startTime = Date.now();
    let isActive = true;
    let readingTime = 0;
    
    // Track if user is actively reading
    function trackActivity() {
        isActive = true;
    }
    
    function trackInactivity() {
        isActive = false;
    }
    
    // Add event listeners for user activity
    document.addEventListener('mousemove', trackActivity);
    document.addEventListener('scroll', trackActivity);
    document.addEventListener('keypress', trackActivity);
    document.addEventListener('click', trackActivity);
    
    // Track visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            trackInactivity();
        } else {
            trackActivity();
            startTime = Date.now(); // Reset timer when coming back
        }
    });
    
    // Calculate reading time every second
    setInterval(function() {
        if (isActive && !document.hidden) {
            readingTime += 1;
        }
        isActive = false; // Reset activity flag
    }, 1000);
    
    // Send reading time data when user leaves the page
    function sendReadingTime() {
        if (readingTime > 5) { // Only send if user spent more than 5 seconds
            const articleId = window.location.pathname.match(/\/article\/(\d+)\//);
            if (articleId) {
                navigator.sendBeacon('/analytics/track-reading-time/', JSON.stringify({
                    article_id: articleId[1],
                    reading_time: readingTime,
                    csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value
                }));
            }
        }
    }
    
    // Send data on page unload
    window.addEventListener('beforeunload', sendReadingTime);
    window.addEventListener('pagehide', sendReadingTime);
    
    // Send data periodically for long reading sessions
    setInterval(function() {
        if (readingTime > 60) { // Send every minute for long sessions
            sendReadingTime();
            readingTime = 0; // Reset counter
        }
    }, 60000);
    
})();
