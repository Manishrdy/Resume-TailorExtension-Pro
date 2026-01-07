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

    // Tailor resume
    async tailorResume(resume, jobDescription) {
        try {
            const response = await fetch(`${this.baseUrl}/api/tailor`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume: resume,
                    jobDescription: jobDescription,
                    preserveStructure: true
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Tailoring failed');
            }

            return await response.json();
        } catch (error) {
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

    // Download PDF
    async downloadPDF(pdfBlob, filename) {
        try {
            const url = URL.createObjectURL(pdfBlob);

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
    }
};

// Initialize on load
api.init();