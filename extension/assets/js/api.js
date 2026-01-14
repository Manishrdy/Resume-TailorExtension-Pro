// assets/js/api.js - FastAPI Client

const api = {
    baseUrl: 'http://localhost:8000',

    // Initialize with settings
    async init() {
        const settings = await storage.getSettings();
        this.baseUrl = settings.apiUrl;
    },

    // Check backend health
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`);
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    },

    // Tailor resume with timeout support
    async tailorResume(resume, jobDescription, timeoutMs = 60000) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
            
            const response = await fetch(`${this.baseUrl}/api/tailor`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume: resume,
                    jobDescription: jobDescription,
                    preserveStructure: true
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Tailoring failed');
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                console.error('Tailor request timeout after 60 seconds');
                throw new Error('AI processing timed out. The request took too long. Please try again.');
            }
            console.error('Tailor API error:', error);
            throw error;
        }
    },

    // Generate PDF
    async generatePDF(resume) {
        try {
            const response = await fetch(`${this.baseUrl}/api/generate-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume: resume
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'PDF generation failed');
            }

            return await response.blob();
        } catch (error) {
            console.error('PDF API error:', error);
            throw error;
        }
    },

    // Generate DOCX (NEW)
    async generateDOCX(resume) {
        try {
            const response = await fetch(`${this.baseUrl}/api/generate-docx`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume: resume
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'DOCX generation failed');
            }

            return await response.blob();
        } catch (error) {
            console.error('DOCX API error:', error);
            throw error;
        }
    },

    // Download file (works for both PDF and DOCX)
    async downloadFile(fileBlob, filename) {
        try {
            const url = URL.createObjectURL(fileBlob);

            await chrome.downloads.download({
                url: url,
                filename: `tailored-resumes/${filename}`,
                saveAs: false
            });

            setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (error) {
            console.error('Download error:', error);
            throw error;
        }
    },

    // Legacy method for backward compatibility
    async downloadPDF(pdfBlob, filename) {
        return this.downloadFile(pdfBlob, filename);
    }
};

// Initialize on load
api.init();