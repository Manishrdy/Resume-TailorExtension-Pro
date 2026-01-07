// content/scraper.js - Job Site Scraper (Production Refactor)

(() => {
    'use strict';

    /**
     * This content script extracts a job description from the current page.
     * - Primary targeted sites: LinkedIn, Indeed, Greenhouse, Glassdoor, Ashby
     * - Other sites: organic extraction first (structured data + main content heuristics)
     * - If organic extraction fails: return empty string and `needsManual: true`
     */

    const MIN_TEXT_LEN = 200;          // Minimum acceptable JD length
    const MAX_TEXT_LEN = 12000;        // Hard cap for returned text (token/control)
    const ORGANIC_MAX_CANDIDATE_LEN = 25000;

    const PRIMARY_SOURCES = Object.freeze({
        LINKEDIN: 'linkedin',
        INDEED: 'indeed',
        GREENHOUSE: 'greenhouse',
        GLASSDOOR: 'glassdoor',
        ASHBY: 'ashby',
        ORGANIC: 'organic',
        NONE: 'none'
    });

    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request?.action !== 'scrape') return;

        try {
            const result = scrapeJobDescription();
            // Keep backward compatibility: always return `jobDescription`
            sendResponse({
                jobDescription: result.text,
                meta: {
                    success: result.success,
                    source: result.source,
                    needsManual: result.needsManual,
                    url: window.location.href
                }
            });
        } catch (err) {
            console.error('Scraping error:', err);
            sendResponse({
                jobDescription: '',
                meta: {
                    success: false,
                    source: PRIMARY_SOURCES.NONE,
                    needsManual: true,
                    url: window.location.href,
                    error: String(err?.message || err)
                }
            });
        }

        return true; // async-safe
    });

    function scrapeJobDescription() {
        const url = window.location.href;
        const host = safeLower(window.location.hostname);

        // 1) Primary targeted websites (same as before)
        let raw = '';
        let source = PRIMARY_SOURCES.NONE;

        if (host.includes('linkedin.com')) {
            raw = scrapeLinkedIn();
            source = PRIMARY_SOURCES.LINKEDIN;
        } else if (host.includes('indeed.com')) {
            raw = scrapeIndeed();
            source = PRIMARY_SOURCES.INDEED;
        } else if (host.includes('greenhouse.io')) {
            raw = scrapeGreenhouse();
            source = PRIMARY_SOURCES.GREENHOUSE;
        } else if (host.includes('glassdoor.com')) {
            raw = scrapeGlassdoor();
            source = PRIMARY_SOURCES.GLASSDOOR;
        } else if (host.includes('ashbyhq.com')) {
            raw = scrapeAshby();
            source = PRIMARY_SOURCES.ASHBY;
        } else {
            // 2) Any other website: organic scrape first
            raw = scrapeOrganic();
            source = PRIMARY_SOURCES.ORGANIC;
        }

        const cleaned = cleanText(raw);

        const success = cleaned.length >= MIN_TEXT_LEN;
        const needsManual = !success && !isPrimaryHost(host); // only push manual for "other sites"

        return {
            text: success ? cleaned : '',
            success,
            source: success ? source : PRIMARY_SOURCES.NONE,
            needsManual
        };
    }

    function isPrimaryHost(host) {
        return (
            host.includes('linkedin.com') ||
            host.includes('indeed.com') ||
            host.includes('greenhouse.io') ||
            host.includes('glassdoor.com') ||
            host.includes('ashbyhq.com')
        );
    }

    // ---------------------------
    // Primary Site Scrapers
    // ---------------------------

    function scrapeLinkedIn() {
        return getTextBySelectors([
            '.jobs-description__content',
            '.jobs-description',
            '.description__text',
            '[class*="job-details"]',
            '[class*="description"]'
        ]);
    }

    function scrapeIndeed() {
        return getTextBySelectors([
            '#jobDescriptionText',
            '.jobsearch-jobDescriptionText',
            '[class*="jobDescription"]',
            '[id*="jobDescription"]'
        ]);
    }

    function scrapeGreenhouse() {
        const text = getTextBySelectors([
            '#content',
            '.application-content',
            '[data-provides="job-board"]',
            '.job-post',
            '[class*="job-description"]',
            'div[id*="job"]',
            'div[class*="content"]'
        ]);

        if (text && text.length >= MIN_TEXT_LEN) return text;

        // Greenhouse can be structured weirdly; body is a reasonable fallback
        const bodyText = document.body?.textContent || '';
        return bodyText.length > 500 ? bodyText : '';
    }

    function scrapeGlassdoor() {
        return getTextBySelectors([
            '[class*="JobDetails"]',
            '[class*="jobDescription"]',
            '.desc',
            '[data-test="jobDescriptionContent"]',
            '.jobDescriptionContent'
        ]);
    }

    function scrapeAshby() {
        return getTextBySelectors([
            '[class*="JobDescription"]',
            '[class*="job-description"]',
            '.job-description',
            'main',
            '[role="main"]'
        ]);
    }

    // ---------------------------
    // Organic Scraper (Other Sites)
    // ---------------------------

    function scrapeOrganic() {
        // (A) Structured data first (best quality, often includes full HTML description)
        const jsonLd = extractFromJsonLdJobPosting();
        if (jsonLd && jsonLd.length >= MIN_TEXT_LEN) return jsonLd;

        // (B) Try common job selectors / keyword-based container search
        const common = extractFromKeywordContainers();
        if (common && common.length >= MIN_TEXT_LEN) return common;

        // (C) Heuristic main content extraction: choose best "contenty" block
        const main = extractFromMainHeuristic();
        if (main && main.length >= MIN_TEXT_LEN) return main;

        // (D) Meta description as a last non-manual resort (often too short)
        const meta = extractFromMetaDescriptions();
        if (meta && meta.length >= MIN_TEXT_LEN) return meta;

        return '';
    }

    function extractFromJsonLdJobPosting() {
        const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
        for (const s of scripts) {
            const txt = s.textContent?.trim();
            if (!txt) continue;

            let data;
            try {
                data = JSON.parse(txt);
            } catch {
                // Some pages include multiple JSON objects or invalid JSON; skip safely
                continue;
            }

            const postings = findJobPostingsInJsonLd(data);
            for (const posting of postings) {
                const desc = posting?.description;
                if (typeof desc === 'string' && desc.trim()) {
                    // description is often HTML
                    const plain = htmlToText(desc);
                    if (plain.length >= MIN_TEXT_LEN) return plain;
                }
            }
        }
        return '';
    }

    function findJobPostingsInJsonLd(node) {
        const out = [];

        // JSON-LD can be array, object, or contain @graph
        const stack = [node];
        while (stack.length) {
            const cur = stack.pop();
            if (!cur) continue;

            if (Array.isArray(cur)) {
                for (const item of cur) stack.push(item);
                continue;
            }

            if (typeof cur === 'object') {
                // @graph
                if (cur['@graph']) stack.push(cur['@graph']);

                const type = cur['@type'];
                if (type) {
                    const typeStr = Array.isArray(type) ? type.join(' ') : String(type);
                    if (typeStr.toLowerCase().includes('jobposting')) {
                        out.push(cur);
                    }
                }

                // traverse children
                for (const k of Object.keys(cur)) {
                    const v = cur[k];
                    if (v && (typeof v === 'object' || Array.isArray(v))) stack.push(v);
                }
            }
        }

        return out;
    }

    function extractFromMetaDescriptions() {
        const candidates = [
            document.querySelector('meta[name="description"]')?.getAttribute('content') || '',
            document.querySelector('meta[property="og:description"]')?.getAttribute('content') || '',
            document.querySelector('meta[name="twitter:description"]')?.getAttribute('content') || ''
        ].map(x => x.trim()).filter(Boolean);

        // Return the longest meta description
        let best = '';
        for (const c of candidates) if (c.length > best.length) best = c;
        return best;
    }

    function extractFromKeywordContainers() {
        const patterns = [
            'job description',
            'job summary',
            'role description',
            'responsibilities',
            'requirements',
            'qualifications',
            'about the role',
            'what you will do',
            'what we are looking for',
            'the role',
            'what you\'ll do',
            'what you will bring'
        ];

        const nodes = document.querySelectorAll('main, article, section, div');
        let bestText = '';
        let bestScore = -Infinity;

        for (const el of nodes) {
            if (!el || isHidden(el) || isLowValueContainer(el)) continue;

            const text = safeText(el);
            if (text.length < MIN_TEXT_LEN || text.length > ORGANIC_MAX_CANDIDATE_LEN) continue;

            const lower = text.toLowerCase();
            const hits = patterns.reduce((acc, p) => acc + (lower.includes(p) ? 1 : 0), 0);
            if (hits === 0) continue;

            const score =
                hits * 50 +
                Math.min(text.length, 10000) * 0.01 -
                linkDensityPenalty(el) -
                boilerplatePenalty(lower);

            if (score > bestScore) {
                bestScore = score;
                bestText = text;
            }
        }

        return bestText;
    }

    function extractFromMainHeuristic() {
        const candidates = Array.from(document.querySelectorAll('main, article, section, div'))
            .filter(el => el && !isHidden(el) && !isLowValueContainer(el));

        let best = '';
        let bestScore = -Infinity;

        for (const el of candidates) {
            const text = safeText(el);
            if (text.length < MIN_TEXT_LEN || text.length > ORGANIC_MAX_CANDIDATE_LEN) continue;

            const lower = text.toLowerCase();

            const keywordScore =
                countKeyword(lower, 'responsibil') +
                countKeyword(lower, 'requirement') +
                countKeyword(lower, 'qualif') +
                countKeyword(lower, 'job description') +
                countKeyword(lower, 'about the role');

            const headingBonus = hasRelevantHeadingsNear(el) ? 40 : 0;

            const score =
                Math.min(text.length, 12000) * 0.02 +
                keywordScore * 20 +
                headingBonus -
                linkDensityPenalty(el) -
                boilerplatePenalty(lower);

            if (score > bestScore) {
                bestScore = score;
                best = text;
            }
        }

        // If nothing good, fall back to main/role=main text
        if (!best) {
            const main = document.querySelector('main') || document.querySelector('[role="main"]');
            if (main) return safeText(main);
        }

        return best;
    }

    function hasRelevantHeadingsNear(el) {
        // Look for headings inside the element
        const headings = el.querySelectorAll('h1,h2,h3,h4');
        for (const h of headings) {
            const t = safeLower(h.textContent || '');
            if (
                t.includes('responsibil') ||
                t.includes('requirement') ||
                t.includes('qualif') ||
                t.includes('job description') ||
                t.includes('about the role')
            ) return true;
        }
        return false;
    }

    // ---------------------------
    // Helpers
    // ---------------------------

    function getTextBySelectors(selectors) {
        for (const selector of selectors) {
            const el = document.querySelector(selector);
            if (!el) continue;

            const text = safeText(el);
            if (text.length >= MIN_TEXT_LEN) return text;
        }
        return '';
    }

    function safeText(el) {
        return (el?.textContent || '').replace(/\u00A0/g, ' ').trim();
    }

    function safeLower(s) {
        return String(s || '').toLowerCase();
    }

    function isHidden(el) {
        // Avoid expensive style calls in loops; but this is okay for content scripts
        const style = window.getComputedStyle(el);
        if (!style) return false;
        if (style.display === 'none' || style.visibility === 'hidden') return true;
        if (parseFloat(style.opacity || '1') === 0) return true;
        return false;
    }

    function isLowValueContainer(el) {
        const tag = safeLower(el.tagName);
        if (tag === 'nav' || tag === 'footer' || tag === 'header' || tag === 'aside') return true;

        const id = safeLower(el.id);
        const cls = safeLower(el.className);

        // common boilerplate zones
        const badHints = ['nav', 'footer', 'header', 'sidebar', 'menu', 'breadcrumb', 'cookie', 'consent', 'subscribe'];
        return badHints.some(h => id.includes(h) || cls.includes(h));
    }

    function linkDensityPenalty(el) {
        const textLen = safeText(el).length || 1;
        const linkText = Array.from(el.querySelectorAll('a'))
            .map(a => (a.textContent || '').trim())
            .join(' ');
        const linkLen = linkText.length;
        const density = linkLen / textLen; // 0..1
        return density * 150; // penalize heavy-link containers
    }

    function boilerplatePenalty(lowerText) {
        // penalize likely non-JD sections
        const boilerplateHints = [
            'cookie',
            'privacy policy',
            'terms of service',
            'all rights reserved',
            'sign in',
            'log in',
            'create account',
            'newsletter',
            'subscribe'
        ];
        let p = 0;
        for (const h of boilerplateHints) {
            if (lowerText.includes(h)) p += 20;
        }
        return p;
    }

    function countKeyword(text, keyword) {
        if (!text || !keyword) return 0;
        let count = 0;
        let idx = 0;
        while ((idx = text.indexOf(keyword, idx)) !== -1) {
            count++;
            idx += keyword.length;
        }
        return count;
    }

    function htmlToText(html) {
        try {
            const doc = new DOMParser().parseFromString(String(html), 'text/html');
            // Preserve some line breaks
            doc.querySelectorAll('br').forEach(br => br.replaceWith('\n'));
            doc.querySelectorAll('p,li,h1,h2,h3,h4').forEach(n => {
                // Add newline after blocky nodes
                n.appendChild(doc.createTextNode('\n'));
            });
            return (doc.body?.textContent || '').trim();
        } catch {
            return String(html || '').replace(/<[^>]*>/g, ' ').trim();
        }
    }

    // ---------------------------
    // Cleaning / Normalization
    // ---------------------------

    function cleanText(text) {
        if (!text) return '';

        let t = String(text);

        // Normalize newlines early
        t = t.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

        // Convert NBSP and collapse spaces (but keep newlines)
        t = t.replace(/\u00A0/g, ' ');
        t = t.replace(/[ \t\f\v]+/g, ' ');

        // Trim each line and remove empty noise lines
        let lines = t.split('\n').map(l => l.trim());

        // Remove very short boilerplate lines (light touch)
        lines = lines.filter(l => {
            if (!l) return false;
            const lower = l.toLowerCase();

            // Avoid removing legitimate short bullets; only drop very short boilerplate-ish lines
            if (l.length < 12) return true;

            const skipPhrases = [
                'about us',
                'about the company',
                'company culture',
                'our mission',
                'our vision',
                'our values',
                'why join us',
                'perks and benefits',
                'employee benefits'
            ];
            if (skipPhrases.some(p => lower === p)) return false;

            return true;
        });

        // Re-join with newlines, then compress excessive newlines
        t = lines.join('\n');
        t = t.replace(/\n{3,}/g, '\n\n').trim();

        // Length control
        if (t.length > MAX_TEXT_LEN) {
            // Try to keep from key sections onward if present
            const m = t.match(/(?:job description|responsibilities|requirements|qualifications)[\s\S]{0,9000}/i);
            t = m ? m[0].trim() : t.slice(0, MAX_TEXT_LEN).trim();
        }

        return t.length >= MIN_TEXT_LEN ? t : '';
    }

    console.log('Resume Tailor AI: Content script loaded (refactored)');
})();
