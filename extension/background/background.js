// background/background.js - Background Service Worker

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('Resume Tailor AI installed');

    // Initialize default settings
    chrome.storage.local.get('settings', (result) => {
        if (!result.settings) {
            chrome.storage.local.set({
                settings: {
                    apiUrl: 'http://localhost:8000',
                    darkMode: false
                }
            });
        }
    });
});

// Handle messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'scrape') {
        // Forward scraping request to content script
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, request, sendResponse);
            }
        });
        return true; // Keep message channel open
    }
});

// Log when service worker starts
console.log('Resume Tailor AI: Background service worker started');