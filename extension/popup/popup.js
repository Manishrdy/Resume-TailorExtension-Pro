// popup/popup.js - Main Application Logic

// State
let currentResume = null;
let tailoredResume = null;
let currentProfileId = null;
let editingResumeId = null;
let editingResumeSnapshot = null;

// Resume form draft autosave
const RESUME_DRAFT_VERSION = 1;
const DRAFT_DEBOUNCE_MS = 400;
let draftSaveTimer = null;

// DOM Elements
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),

    // Resume tab
    resumeSelect: document.getElementById('resume-select'),
    newResumeBtn: document.getElementById('new-resume-btn'),
    resumePreview: document.getElementById('resume-preview'),
    previewName: document.getElementById('preview-name'),
    previewEmail: document.getElementById('preview-email'),
    expCount: document.getElementById('exp-count'),
    eduCount: document.getElementById('edu-count'),
    projCount: document.getElementById('proj-count'),
    editResumeBtn: document.getElementById('edit-resume-btn'),
    deleteResumeBtn: document.getElementById('delete-resume-btn'),
    exportJsonBtn: document.getElementById('export-json-btn'),

    // Backup / import
    exportAllBtn: document.getElementById('export-all-btn'),
    importResumesBtn: document.getElementById('import-resumes-btn'),
    importFileInput: document.getElementById('import-file-input'),
    clearStorageBtn: document.getElementById('clear-storage-btn'),

    // Tailor tab
    currentResumeName: document.getElementById('current-resume-name'),
    scrapeBtn: document.getElementById('scrape-btn'),
    jobDescription: document.getElementById('job-description'),
    tailorBtn: document.getElementById('tailor-btn'),
    loading: document.getElementById('loading'),
    results: document.getElementById('results'),
    atsScore: document.getElementById('ats-score'),
    matchedCount: document.getElementById('matched-count'),
    matchedKeywords: document.getElementById('matched-keywords'),
    missingCount: document.getElementById('missing-count'),
    missingKeywords: document.getElementById('missing-keywords'),
    downloadPdfBtn: document.getElementById('download-pdf-btn'),
    errorMsg: document.getElementById('error-msg'),
    successMsg: document.getElementById('success-msg'),

    // History tab
    historyList: document.getElementById('history-list'),

    // Settings tab
    apiUrl: document.getElementById('api-url'),
    darkModeToggle: document.getElementById('dark-mode-toggle'),
    saveSettingsBtn: document.getElementById('save-settings-btn'),
    testConnectionBtn: document.getElementById('test-connection-btn'),
    connectionStatus: document.getElementById('connection-status'),

    // Footer
    currentProfileFooter: document.getElementById('current-profile-footer'),

    // Modal
    modal: document.getElementById('resume-modal'),
    modalTitle: document.getElementById('modal-title'),
    modalClose: document.getElementById('modal-close'),
    clearDraftBtn: document.getElementById('clear-draft-btn'),
    resumeForm: document.getElementById('resume-form'),
    cancelBtn: document.getElementById('cancel-btn'),
    clearDraftBtn: document.getElementById('clear-draft-btn'),

    // Form containers
    experienceContainer: document.getElementById('experience-container'),
    educationContainer: document.getElementById('education-container'),
    projectsContainer: document.getElementById('projects-container'),
    skillsContainer: document.getElementById('skills-container'),

    // Add buttons
    addExperience: document.getElementById('add-experience'),
    addEducation: document.getElementById('add-education'),
    addProject: document.getElementById('add-project'),
    addSkill: document.getElementById('add-skill')
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadResumes();
    await loadSettings();
    await loadHistory();
    setupEventListeners();
    updateCurrentProfileDisplay();
});

// Tab Navigation
function setupEventListeners() {
    // Tab switching
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Resume tab
    elements.resumeSelect.addEventListener('change', handleResumeSelect);
    elements.newResumeBtn.addEventListener('click', () => openModal());
    elements.editResumeBtn.addEventListener('click', () => openModal(currentResume));
    elements.deleteResumeBtn.addEventListener('click', handleDeleteResume);
    elements.exportJsonBtn.addEventListener('click', handleExportJson);

    // Backup / import
    if (elements.exportAllBtn) elements.exportAllBtn.addEventListener('click', handleExportAll);
    if (elements.importResumesBtn) elements.importResumesBtn.addEventListener('click', handleImportResumes);
    if (elements.importFileInput) elements.importFileInput.addEventListener('change', handleImportFileChange);
    if (elements.clearStorageBtn) elements.clearStorageBtn.addEventListener('click', handleClearStorage);

    // Tailor tab
    elements.scrapeBtn.addEventListener('click', handleScrape);
    elements.jobDescription.addEventListener('input', updateTailorButton);
    elements.tailorBtn.addEventListener('click', handleTailor);
    elements.downloadPdfBtn.addEventListener('click', handleDownloadPdf);

    // Settings tab
    elements.saveSettingsBtn.addEventListener('click', handleSaveSettings);
    elements.testConnectionBtn.addEventListener('click', handleTestConnection);

    // Modal
    elements.modalClose.addEventListener('click', closeModal);
    elements.cancelBtn.addEventListener('click', closeModal);
    elements.clearDraftBtn.addEventListener('click', handleClearDraft);
    elements.resumeForm.addEventListener('submit', handleSaveResume);

    // Autosave resume form draft (persists even when popup closes)
    elements.resumeForm.addEventListener('input', queueSaveDraft);
    // Capture remove clicks (inline onclick removes the node; save after)
    elements.resumeForm.addEventListener('click', (e) => {
        if (e.target && e.target.classList && e.target.classList.contains('remove-btn')) {
            setTimeout(queueSaveDraft, 0);
        }
    });

    

    // Close when clicking outside the editor card
    elements.modal.addEventListener('click', (e) => {
        if (e.target && e.target.classList && e.target.classList.contains('modal-overlay')) {
            closeModal();
        }
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !elements.modal.classList.contains('hidden')) {
            closeModal();
        }
    });
// Dynamic form buttons
    elements.addExperience.addEventListener('click', () => addExperienceEntry());
    elements.addEducation.addEventListener('click', () => addEducationEntry());
    elements.addProject.addEventListener('click', () => addProjectEntry());
    elements.addSkill.addEventListener('click', () => addSkillEntry());
}

// Tab Switching
function switchTab(tabName) {
    elements.tabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

// Load Resumes
async function loadResumes() {
    const resumes = await storage.getResumes();
    const savedProfileId = await storage.getCurrentProfile();

    elements.resumeSelect.innerHTML = '<option value="">Select resume...</option>';

    Object.values(resumes).forEach(resume => {
        const option = document.createElement('option');
        option.value = resume.id;
        option.textContent = resume.name;
        if (resume.id === savedProfileId) {
            option.selected = true;
        }
        elements.resumeSelect.appendChild(option);
    });

    if (savedProfileId && resumes[savedProfileId]) {
        currentResume = resumes[savedProfileId];
        currentProfileId = savedProfileId;
        displayResumePreview(currentResume);
    }
}

// Handle Resume Selection
async function handleResumeSelect(e) {
    const resumeId = e.target.value;

    if (!resumeId) {
        currentResume = null;
        currentProfileId = null;
        elements.resumePreview.classList.add('hidden');
        updateCurrentProfileDisplay();
        return;
    }

    const resumes = await storage.getResumes();
    currentResume = resumes[resumeId];
    currentProfileId = resumeId;

    await storage.setCurrentProfile(resumeId);
    displayResumePreview(currentResume);
    updateCurrentProfileDisplay();
}

// Display Resume Preview
function displayResumePreview(resume) {
    elements.previewName.textContent = resume.personalInfo.name;
    elements.previewEmail.textContent = resume.personalInfo.email;
    elements.expCount.textContent = resume.experience?.length || 0;
    elements.eduCount.textContent = resume.education?.length || 0;
    elements.projCount.textContent = resume.projects?.length || 0;
    elements.resumePreview.classList.remove('hidden');
}

// Update Current Profile Display
function updateCurrentProfileDisplay() {
    const name = currentResume ? currentResume.name : 'None';
    elements.currentProfileFooter.textContent = `Current: ${name}`;
    elements.currentResumeName.textContent = name;
    updateTailorButton();
}

// Open Modal (New or Edit)
function openModal(resume = null) {
    // Track whether we're editing an existing resume or creating a new one
    editingResumeId = resume?.id || null;
    editingResumeSnapshot = resume ? JSON.parse(JSON.stringify(resume)) : null;

    if (resume) {
        elements.modalTitle.textContent = 'Edit Resume';
        // Prefer draft (if any) over saved resume when editing
        restoreDraftOrPopulate(resume);
    } else {
        elements.modalTitle.textContent = 'Create New Resume';
        // Prefer draft (if any) for new resume creation
        restoreDraftOrReset();
    }

    // Fullscreen editor inside the popup for easier writing/editing
    elements.modal.classList.remove('hidden');
    elements.modal.classList.add('modal--fullscreen');
    document.body.classList.add('modal-open');

    // Focus the first meaningful input for faster editing
    const firstField = elements.modal.querySelector('input, textarea, select');
    if (firstField) firstField.focus();
}

// Close Modal
function closeModal() {
    elements.modal.classList.add('hidden');
    elements.modal.classList.remove('modal--fullscreen');
    document.body.classList.remove('modal-open');
}

function getDraftKey() {
    return editingResumeId ? `edit:${editingResumeId}` : 'new';
}

function queueSaveDraft() {
    // Only save when the editor is open (prevents background writes)
    if (elements.modal.classList.contains('hidden')) return;

    if (draftSaveTimer) clearTimeout(draftSaveTimer);
    draftSaveTimer = setTimeout(async () => {
        try {
            const state = collectResumeFormState();
            const hasMeaningfulContent = hasDraftContent(state);

            if (!hasMeaningfulContent) {
                // If user cleared everything, don't keep stale draft
                await storage.clearResumeDraft(getDraftKey());
                return;
            }

            await storage.saveResumeDraft(getDraftKey(), {
                version: RESUME_DRAFT_VERSION,
                updatedAt: new Date().toISOString(),
                editingResumeId: editingResumeId,
                data: state
            });
        } catch (err) {
            // Draft save failures should never break the UX
            console.warn('Draft save failed:', err);
        }
    }, DRAFT_DEBOUNCE_MS);
}

async function restoreDraftOrReset() {
    // New resume mode
    clearDynamicContainers();
    elements.resumeForm.reset();

    try {
        const draft = await storage.getResumeDraft('new');
        if (draft?.version === RESUME_DRAFT_VERSION && draft?.data) {
            applyResumeFormState(draft.data);
        }
    } catch (err) {
        console.warn('Draft restore (new) failed:', err);
    }
}

async function restoreDraftOrPopulate(resume) {
    clearDynamicContainers();
    elements.resumeForm.reset();

    try {
        const draft = await storage.getResumeDraft(getDraftKey());
        if (draft?.version === RESUME_DRAFT_VERSION && draft?.data) {
            applyResumeFormState(draft.data);
            return;
        }
    } catch (err) {
        console.warn('Draft restore (edit) failed:', err);
    }

    // Fallback to saved resume
    populateForm(resume);
}

function hasDraftContent(state) {
    if (!state) return false;
    const s = JSON.stringify(state);
    // cheap check to avoid storing completely blank drafts
    return s.replace(/[\s"{}\[\]:,]/g, '').length > 0;
}

function collectResumeFormState() {
    const get = (name) => (document.querySelector(`[name="${name}"]`)?.value || '').trim();

    const state = {
        resumeName: get('resumeName'),
        personalInfo: {
            name: get('name'),
            email: get('email'),
            phone: get('phone'),
            location: get('location'),
            linkedin: get('linkedin'),
            portfolio: get('portfolio'),
            github: get('github'),
            summary: (document.querySelector('[name="summary"]')?.value || '').trim()
        },
        experience: [],
        education: [],
        projects: [],
        skills: []
    };

    // Experience
    const expItems = Array.from(elements.experienceContainer.querySelectorAll('.entry-item'));
    for (const item of expItems) {
        const employer = (item.querySelector('[name="exp-employer[]"]')?.value || '').trim();
        const role = (item.querySelector('[name="exp-role[]"]')?.value || '').trim();
        const startDate = (item.querySelector('[name="exp-start[]"]')?.value || '').trim();
        const endDate = (item.querySelector('[name="exp-end[]"]')?.value || '').trim();
        const descRaw = (item.querySelector('[name="exp-desc[]"]')?.value || '').trim();
        const description = descRaw ? descRaw.split('\n').map(l => l.trim()).filter(Boolean) : [];
        state.experience.push({ employer, role, startDate, endDate, description });
    }

    // Education
    const eduItems = Array.from(elements.educationContainer.querySelectorAll('.entry-item'));
    for (const item of eduItems) {
        const institution = (item.querySelector('[name="edu-institution[]"]')?.value || '').trim();
        const degree = (item.querySelector('[name="edu-degree[]"]')?.value || '').trim();
        const startDate = (item.querySelector('[name="edu-start[]"]')?.value || '').trim();
        const endDate = (item.querySelector('[name="edu-end[]"]')?.value || '').trim();
        const cwRaw = (item.querySelector('[name="edu-coursework[]"]')?.value || '').trim();
        const coursework = cwRaw ? cwRaw.split(',').map(c => c.trim()).filter(Boolean) : [];
        state.education.push({ institution, degree, startDate, endDate, coursework });
    }

    // Projects
    const projItems = Array.from(elements.projectsContainer.querySelectorAll('.entry-item'));
    for (const item of projItems) {
        const name = (item.querySelector('[name="proj-name[]"]')?.value || '').trim();
        const github = (item.querySelector('[name="proj-github[]"]')?.value || '').trim();
        const startDate = (item.querySelector('[name="proj-start[]"]')?.value || '').trim();
        const endDate = (item.querySelector('[name="proj-end[]"]')?.value || '').trim();
        const descRaw = (item.querySelector('[name="proj-desc[]"]')?.value || '').trim();
        const description = descRaw ? descRaw.split('\n').map(l => l.trim()).filter(Boolean) : [];
        state.projects.push({ name, github, startDate, endDate, description });
    }

    // Skills
    const skillItems = Array.from(elements.skillsContainer.querySelectorAll('.skill-category'));
    for (const item of skillItems) {
        const category = (item.querySelector('[name="skill-category[]"]')?.value || '').trim();
        const skills = (item.querySelector('[name="skill-items[]"]')?.value || '').trim();
        state.skills.push({ category, skills });
    }

    return state;
}

function applyResumeFormState(state) {
    if (!state) return;

    // Basic fields
    document.querySelector('[name="resumeName"]').value = state.resumeName || '';

    const pi = state.personalInfo || {};
    document.querySelector('[name="name"]').value = pi.name || '';
    document.querySelector('[name="email"]').value = pi.email || '';
    document.querySelector('[name="phone"]').value = pi.phone || '';
    document.querySelector('[name="location"]').value = pi.location || '';
    document.querySelector('[name="linkedin"]').value = pi.linkedin || '';
    document.querySelector('[name="portfolio"]').value = pi.portfolio || '';
    document.querySelector('[name="github"]').value = pi.github || '';
    document.querySelector('[name="summary"]').value = pi.summary || '';

    // Dynamic sections
    clearDynamicContainers();

    (state.experience || []).forEach(exp => addExperienceEntry({
        employer: exp.employer || '',
        role: exp.role || '',
        startDate: exp.startDate || '',
        endDate: exp.endDate || '',
        description: Array.isArray(exp.description) ? exp.description : []
    }));

    (state.education || []).forEach(edu => addEducationEntry({
        institution: edu.institution || '',
        degree: edu.degree || '',
        startDate: edu.startDate || '',
        endDate: edu.endDate || '',
        coursework: Array.isArray(edu.coursework) ? edu.coursework : []
    }));

    (state.projects || []).forEach(proj => addProjectEntry({
        name: proj.name || '',
        github: proj.github || '',
        startDate: proj.startDate || '',
        endDate: proj.endDate || '',
        description: Array.isArray(proj.description) ? proj.description : []
    }));

    (state.skills || []).forEach(s => addSkillEntry({
        category: s.category || '',
        skills: s.skills || ''
    }));
}

async function handleClearDraft() {
    try {
        await storage.clearResumeDraft(getDraftKey());

        // Reset editor to a sane state
        clearDynamicContainers();
        elements.resumeForm.reset();

        if (editingResumeSnapshot) {
            populateForm(editingResumeSnapshot);
        } else {
            editingResumeId = null;
            editingResumeSnapshot = null;
        }

        showSuccess('Draft cleared');
    } catch (err) {
        console.warn('Clear draft failed:', err);
        showError('Could not clear draft');
    }
}
// Clear Dynamic Containers
function clearDynamicContainers() {
    elements.experienceContainer.innerHTML = '';
    elements.educationContainer.innerHTML = '';
    elements.projectsContainer.innerHTML = '';
    elements.skillsContainer.innerHTML = '';
}

// Populate Form (for editing)
function populateForm(resume) {
    // Resume name
    document.querySelector('[name="resumeName"]').value = resume.name;

    // Personal info
    document.querySelector('[name="name"]').value = resume.personalInfo.name || '';
    document.querySelector('[name="email"]').value = resume.personalInfo.email || '';
    document.querySelector('[name="phone"]').value = resume.personalInfo.phone || '';
    document.querySelector('[name="location"]').value = resume.personalInfo.location || '';
    document.querySelector('[name="linkedin"]').value = resume.personalInfo.linkedin || '';
    document.querySelector('[name="portfolio"]').value = resume.personalInfo.portfolio || '';
    document.querySelector('[name="github"]').value = resume.personalInfo.github || '';
    document.querySelector('[name="summary"]').value = resume.personalInfo.summary || '';

    // Experience
    clearDynamicContainers();
    resume.experience?.forEach(exp => addExperienceEntry(exp));

    // Education
    resume.education?.forEach(edu => addEducationEntry(edu));

    // Projects
    resume.projects?.forEach(proj => addProjectEntry(proj));

    // Skills
    if (resume.skills && typeof resume.skills === 'object') {
        Object.entries(resume.skills).forEach(([category, skills]) => {
            addSkillEntry({ category, skills: Array.isArray(skills) ? skills.join(', ') : skills });
        });
    }
}

// Add Experience Entry
function addExperienceEntry(data = null) {
    const div = document.createElement('div');
    div.className = 'entry-item';
    div.innerHTML = `
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
        <div class="form-group">
            <label>Employer</label>
            <input type="text" name="exp-employer[]" class="form-control" placeholder="Company Name" value="${data?.employer || ''}">
        </div>
        <div class="form-group">
            <label>Role</label>
            <input type="text" name="exp-role[]" class="form-control" placeholder="Job Title" value="${data?.role || ''}">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Start Date</label>
                <input type="text" name="exp-start[]" class="form-control" placeholder="MMM YYYY" value="${data?.startDate || ''}">
            </div>
            <div class="form-group">
                <label>End Date</label>
                <input type="text" name="exp-end[]" class="form-control" placeholder="MMM YYYY or Present" value="${data?.endDate || ''}">
            </div>
        </div>
        <div class="form-group">
            <label>Description (one bullet per line)</label>
            <textarea name="exp-desc[]" class="form-control" rows="4" placeholder="• Built secure backend microservices...
- Designed scalable data ingestion...">${data?.description ? data.description.join('\n') : ''}</textarea>
        </div>
    `;
    elements.experienceContainer.appendChild(div);
}

// Add Education Entry
function addEducationEntry(data = null) {
    const div = document.createElement('div');
    div.className = 'entry-item';
    div.innerHTML = `
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
        <div class="form-group">
            <label>Institution</label>
            <input type="text" name="edu-institution[]" class="form-control" placeholder="University Name" value="${data?.institution || ''}">
        </div>
        <div class="form-group">
            <label>Degree</label>
            <input type="text" name="edu-degree[]" class="form-control" placeholder="e.g., Masters in Computer Science - 3.8 GPA" value="${data?.degree || ''}">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Start Date</label>
                <input type="text" name="edu-start[]" class="form-control" placeholder="MMM YYYY" value="${data?.startDate || ''}">
            </div>
            <div class="form-group">
                <label>End Date</label>
                <input type="text" name="edu-end[]" class="form-control" placeholder="MMM YYYY" value="${data?.endDate || ''}">
            </div>
        </div>
        <div class="form-group">
            <label>Coursework (comma-separated)</label>
            <textarea name="edu-coursework[]" class="form-control" rows="2" placeholder="Artificial Intelligence, Theory of Algorithms, Modern Computer Architecture">${data?.coursework ? data.coursework.join(', ') : ''}</textarea>
        </div>
    `;
    elements.educationContainer.appendChild(div);
}

// Add Project Entry
function addProjectEntry(data = null) {
    const div = document.createElement('div');
    div.className = 'entry-item';
    div.innerHTML = `
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
        <div class="form-group">
            <label>Project Name</label>
            <input type="text" name="proj-name[]" class="form-control" placeholder="Project Title" value="${data?.name || ''}">
        </div>
        <div class="form-group">
            <label>GitHub Link</label>
            <input type="url" name="proj-github[]" class="form-control" placeholder="https://github.com/username/repo" value="${data?.github || ''}">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Start Date</label>
                <input type="text" name="proj-start[]" class="form-control" placeholder="Winter 2025" value="${data?.startDate || ''}">
            </div>
            <div class="form-group">
                <label>End Date</label>
                <input type="text" name="proj-end[]" class="form-control" placeholder="Winter 2025" value="${data?.endDate || ''}">
            </div>
        </div>
        <div class="form-group">
            <label>Description (one bullet per line)</label>
            <textarea name="proj-desc[]" class="form-control" rows="3" placeholder="• Designed an end-to-end distributed backend...
- Implemented a queue-driven pipeline...">${data?.description ? data.description.join('\n') : ''}</textarea>
        </div>
    `;
    elements.projectsContainer.appendChild(div);
}

// Add Skill Entry
function addSkillEntry(data = null) {
    const div = document.createElement('div');
    div.className = 'skill-category';
    div.innerHTML = `
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
        <div class="form-group">
            <label>Category</label>
            <input type="text" name="skill-category[]" class="form-control" placeholder="e.g., Programming Languages" value="${data?.category || ''}">
        </div>
        <div class="form-group">
            <label>Skills (comma-separated)</label>
            <input type="text" name="skill-items[]" class="form-control" placeholder="Python, JavaScript, Java" value="${data?.skills || ''}">
        </div>
    `;
    elements.skillsContainer.appendChild(div);
}

// Handle Save Resume
async function handleSaveResume(e) {
    e.preventDefault();

    const formData = new FormData(e.target);

    // Build resume object
    const resume = {
        // Never overwrite the currently-selected resume when creating a new one.
        // Only overwrite when we're explicitly in edit mode.
        id: editingResumeId || crypto.randomUUID(),
        name: formData.get('resumeName'),
        personalInfo: {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone') || '',
            location: formData.get('location') || '',
            linkedin: formData.get('linkedin') || '',
            portfolio: formData.get('portfolio') || '',
            github: formData.get('github') || '',
            summary: formData.get('summary')
        },
        experience: [],
        education: [],
        projects: [],
        skills: {},
        certifications: []
    };

    // Experience
    const expEmployers = formData.getAll('exp-employer[]');
    expEmployers.forEach((employer, i) => {
        if (employer.trim()) {
            const desc = formData.getAll('exp-desc[]')[i];
            resume.experience.push({
                employer: employer,
                role: formData.getAll('exp-role[]')[i],
                startDate: formData.getAll('exp-start[]')[i],
                endDate: formData.getAll('exp-end[]')[i],
                description: desc.split('\n').filter(line => line.trim()).map(line => line.replace(/^[•\-\*]\s*/, ''))
            });
        }
    });

    // Education
    const eduInstitutions = formData.getAll('edu-institution[]');
    eduInstitutions.forEach((institution, i) => {
        if (institution.trim()) {
            const coursework = formData.getAll('edu-coursework[]')[i];
            resume.education.push({
                institution: institution,
                degree: formData.getAll('edu-degree[]')[i],
                startDate: formData.getAll('edu-start[]')[i],
                endDate: formData.getAll('edu-end[]')[i],
                coursework: coursework ? coursework.split(',').map(c => c.trim()).filter(c => c) : []
            });
        }
    });

    // Projects
    const projNames = formData.getAll('proj-name[]');
    projNames.forEach((name, i) => {
        if (name.trim()) {
            const desc = formData.getAll('proj-desc[]')[i];
            resume.projects.push({
                name: name,
                github: formData.getAll('proj-github[]')[i],
                startDate: formData.getAll('proj-start[]')[i],
                endDate: formData.getAll('proj-end[]')[i],
                description: desc.split('\n').filter(line => line.trim()).map(line => line.replace(/^[•\-\*]\s*/, ''))
            });
        }
    });

    // Skills
    const skillCategories = formData.getAll('skill-category[]');
    skillCategories.forEach((category, i) => {
        if (category.trim()) {
            const items = formData.getAll('skill-items[]')[i];
            resume.skills[category] = items.split(',').map(s => s.trim()).filter(s => s);
        }
    });

    // Save
    await storage.saveResume(resume);
    await storage.setCurrentProfile(resume.id);

    // Clear any autosaved draft now that the resume is saved
    await storage.clearResumeDraft(getDraftKey());

    closeModal();
    await loadResumes();
    showSuccess('Resume saved successfully!');
}

// Handle Delete Resume
async function handleDeleteResume() {
    if (!currentResume) return;

    if (confirm(`Delete resume "${currentResume.name}"?`)) {
        await storage.deleteResume(currentResume.id);
        currentResume = null;
        currentProfileId = null;
        await storage.setCurrentProfile(null);
        await loadResumes();
        elements.resumePreview.classList.add('hidden');
        updateCurrentProfileDisplay();
        showSuccess('Resume deleted');
    }
}

// Handle Export JSON
async function handleExportJson() {
    if (!currentResume) return;
    await storage.exportToJSON(currentResume);
    showSuccess('Resume exported!');
}

// Handle Export All (Backup)
async function handleExportAll() {
    try {
        const resumes = await storage.getResumes();
        if (!resumes || Object.keys(resumes).length === 0) {
            showError('No resumes to export');
            return;
        }
        await storage.exportAllResumesToJSON();
        showSuccess('Backup exported!');
    } catch (err) {
        console.error('Export all failed:', err);
        showError('Could not export backup');
    }
}

// Handle Import (Backup)
async function handleImportResumes() {
    // Reset input so selecting the same file again still triggers change
    elements.importFileInput.value = '';
    elements.importFileInput.click();
}

async function handleImportFileChange(e) {
    const file = e.target?.files?.[0];
    if (!file) return;

    try {
        const text = await file.text();
        const summary = await storage.importResumesFromJSONText(text, { overwrite: false });

        await loadResumes();
        updateCurrentProfileDisplay();

        const msgParts = [
            `${summary.added} added`,
            summary.deduped ? `${summary.deduped} kept as copies` : null,
            summary.overwritten ? `${summary.overwritten} overwritten` : null
        ].filter(Boolean);

        showSuccess(`Import complete: ${msgParts.join(', ')}`);
    } catch (err) {
        console.error('Import failed:', err);
        showError(err?.message || 'Import failed');
    } finally {
        elements.importFileInput.value = '';
    }
}

// Clear stored resumes/history/drafts from this browser
async function handleClearStorage() {
    const ok = confirm('This will delete all resumes, tailoring history, and drafts stored in this browser. Continue?');
    if (!ok) return;

    try {
        await storage.clearStoredData({ keepSettings: true });

        currentResume = null;
        tailoredResume = null;
        currentProfileId = null;

        elements.resumePreview.classList.add('hidden');
        elements.jobDescription.value = '';
        updateTailorButton();

        await loadResumes();
        await loadHistory();
        updateCurrentProfileDisplay();

        showSuccess('Local data cleared');
    } catch (err) {
        console.error('Clear storage failed:', err);
        showError('Could not clear local data');
    }
}


// Handle Scrape
async function handleScrape() {
    try {
        elements.scrapeBtn.disabled = true;
        elements.scrapeBtn.textContent = '🔄 Scraping...';

        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        const response = await chrome.tabs.sendMessage(tab.id, { action: 'scrape' });

        if (response && response.jobDescription) {
            elements.jobDescription.value = response.jobDescription;
            showSuccess('Job description scraped!');
        } else {
            showError('Could not scrape. Please paste manually.');
        }
    } catch (error) {
        console.error('Scrape error:', error);
        showError('Scraping failed. Please paste manually.');
    } finally {
        elements.scrapeBtn.disabled = false;
        elements.scrapeBtn.textContent = '🔍 Scrape from Current Page';
        updateTailorButton();
    }
}

// Update Tailor Button
function updateTailorButton() {
    const hasResume = currentResume !== null;
    const hasJD = elements.jobDescription.value.trim().length > 0;
    elements.tailorBtn.disabled = !(hasResume && hasJD);
}

// Handle Tailor
async function handleTailor() {
    if (!currentResume) {
        showError('Please select a resume first');
        return;
    }

    const jobDesc = elements.jobDescription.value.trim();
    if (!jobDesc) {
        showError('Please provide job description');
        return;
    }

    try {
        // Show loading
        elements.loading.classList.remove('hidden');
        elements.results.classList.add('hidden');
        elements.tailorBtn.disabled = true;
        hideMessages();

        // Call API
        const result = await api.tailorResume(currentResume, jobDesc);

        // Store tailored resume
        tailoredResume = result.tailoredResume;

        // Display results
        displayResults(result);

        elements.loading.classList.add('hidden');
        elements.results.classList.remove('hidden');
        showSuccess(`ATS Score: ${result.atsScore}/100`);

    } catch (error) {
        console.error('Tailor error:', error);
        elements.loading.classList.add('hidden');
        showError(error.message || 'Tailoring failed. Check backend connection.');
    } finally {
        elements.tailorBtn.disabled = false;
    }
}

// Display Results
function displayResults(result) {
    // ATS Score
    elements.atsScore.textContent = result.atsScore;

    // Matched Keywords
    elements.matchedCount.textContent = result.matchedKeywords.length;
    elements.matchedKeywords.innerHTML = '';
    result.matchedKeywords.forEach(keyword => {
        const span = document.createElement('span');
        span.className = 'keyword matched';
        span.textContent = keyword;
        elements.matchedKeywords.appendChild(span);
    });

    // Missing Keywords
    elements.missingCount.textContent = result.missingKeywords.length;
    elements.missingKeywords.innerHTML = '';
    result.missingKeywords.forEach(keyword => {
        const span = document.createElement('span');
        span.className = 'keyword missing';
        span.textContent = keyword;
        elements.missingKeywords.appendChild(span);
    });
}

// Handle Download PDF
async function handleDownloadPdf() {
    if (!tailoredResume) {
        showError('No tailored resume available');
        return;
    }

    try {
        elements.downloadPdfBtn.disabled = true;
        elements.downloadPdfBtn.textContent = '⏳ Generating PDF...';

        const pdfBlob = await api.generatePDF(tailoredResume);

        const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
        const filename = `${currentResume.name.replace(/\s+/g, '_')}_${timestamp}.pdf`;

        await api.downloadPDF(pdfBlob, filename);

        // Add to history
        await storage.addToHistory({
            id: crypto.randomUUID(),
            resumeName: currentResume.name,
            jobTitle: 'Job Application',
            company: 'Company',
            atsScore: parseInt(elements.atsScore.textContent),
            timestamp: new Date().toISOString(),
            filename: filename
        });

        await loadHistory();
        showSuccess('PDF downloaded!');

    } catch (error) {
        console.error('PDF error:', error);
        showError(error.message || 'PDF generation failed');
    } finally {
        elements.downloadPdfBtn.disabled = false;
        elements.downloadPdfBtn.textContent = '📄 Download Tailored PDF';
    }
}

// Load History
async function loadHistory() {
    const history = await storage.getHistory();

    if (history.length === 0) {
        elements.historyList.innerHTML = '<p class="empty">No tailored resumes yet</p>';
        return;
    }

    elements.historyList.innerHTML = '';

    history.forEach(entry => {
        const div = document.createElement('div');
        div.className = 'history-item';

        const date = new Date(entry.timestamp).toLocaleDateString();

        div.innerHTML = `
            <div class="history-info">
                <h4>${entry.resumeName}</h4>
                <p class="history-meta">Score: ${entry.atsScore}/100 • ${date}</p>
            </div>
            <button class="btn btn-sm btn-danger" onclick="deleteHistory('${entry.id}')">Delete</button>
        `;

        elements.historyList.appendChild(div);
    });
}

// Delete History (global function for onclick)
window.deleteHistory = async function (id) {
    await storage.deleteFromHistory(id);
    await loadHistory();
    showSuccess('Deleted from history');
};

// Load Settings
async function loadSettings() {
    const settings = await storage.getSettings();
    elements.apiUrl.value = settings.apiUrl;
    elements.darkModeToggle.checked = settings.darkMode;

    if (settings.darkMode) {
        document.body.classList.add('dark-mode');
        document.body.classList.add('dark');
    }
}

// Handle Save Settings
async function handleSaveSettings() {
    const settings = {
        apiUrl: elements.apiUrl.value,
        darkMode: elements.darkModeToggle.checked
    };

    await storage.saveSettings(settings);
    await api.init();

    if (settings.darkMode) {
        document.body.classList.add('dark-mode');
        document.body.classList.add('dark');
    } else {
        document.body.classList.remove('dark-mode');
        document.body.classList.remove('dark');
    }

    showSuccess('Settings saved!');
}

// Handle Test Connection
async function handleTestConnection() {
    try {
        elements.testConnectionBtn.disabled = true;
        elements.testConnectionBtn.textContent = 'Testing...';

        const isHealthy = await api.checkHealth();

        if (isHealthy) {
            elements.connectionStatus.className = 'alert success';
            elements.connectionStatus.textContent = '✅ Backend connection successful!';
        } else {
            elements.connectionStatus.className = 'alert error';
            elements.connectionStatus.textContent = '❌ Cannot connect to backend';
        }

        elements.connectionStatus.classList.remove('hidden');

    } catch (error) {
        elements.connectionStatus.className = 'alert error';
        elements.connectionStatus.textContent = '❌ Connection failed';
        elements.connectionStatus.classList.remove('hidden');
    } finally {
        elements.testConnectionBtn.disabled = false;
        elements.testConnectionBtn.textContent = 'Test Connection';

        setTimeout(() => {
            elements.connectionStatus.classList.add('hidden');
        }, 5000);
    }
}

// Show Success Message
function showSuccess(message) {
    elements.successMsg.textContent = message;
    elements.successMsg.classList.remove('hidden');
    elements.errorMsg.classList.add('hidden');

    setTimeout(() => {
        elements.successMsg.classList.add('hidden');
    }, 5000);
}

// Show Error Message
function showError(message) {
    elements.errorMsg.textContent = message;
    elements.errorMsg.classList.remove('hidden');
    elements.successMsg.classList.add('hidden');

    setTimeout(() => {
        elements.errorMsg.classList.add('hidden');
    }, 5000);
}

// Hide Messages
function hideMessages() {
    elements.errorMsg.classList.add('hidden');
    elements.successMsg.classList.add('hidden');
}