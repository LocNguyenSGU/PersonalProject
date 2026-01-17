/**
 * Personalization Manager
 * Applies AI-generated personalization rules to portfolio
 */
class PersonalizationManager {
    constructor(apiUrl = '/api') {
        this.apiUrl = apiUrl;
        this.userId = null;
        this.segment = null;
    }
    
    /**
     * Initialize personalization on page load
     */
    async init() {
        try {
            console.log('[PersonalizationManager] Initializing...');
            
            // 1. Get GA4 client ID
            this.userId = await this.getGA4ClientId();
            console.log('[PersonalizationManager] GA4 client ID:', this.userId);
            
            // 2. Fetch rules from backend
            const response = await fetch(
                `${this.apiUrl}/personalization?user_id=${this.userId}`
            );
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const { segment, priority_sections, featured_projects, highlight_skills } = await response.json();
            this.segment = segment;
            
            console.log('[PersonalizationManager] Segment:', segment);
            console.log('[PersonalizationManager] Rules:', { priority_sections, featured_projects, highlight_skills });
            
            // 3. Apply rules
            this.applyRules({
                priority_sections,
                featured_projects,
                highlight_skills
            });
            
            // 4. Track personalization
            this.trackPersonalizationApplied(segment);
            
        } catch (error) {
            console.warn('[PersonalizationManager] Failed, showing default', error);
            // Site continues with default experience
        }
    }
    
    /**
     * Get GA4 client ID
     */
    getGA4ClientId() {
        return new Promise((resolve) => {
            try {
                // Check if gtag is available
                if (typeof gtag === 'undefined') {
                    console.warn('[PersonalizationManager] gtag not available, using fallback ID');
                    resolve(`visitor_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
                    return;
                }
                
                gtag('get', 'client_id', function(clientId) {
                    console.log('[PersonalizationManager] Got GA4 client ID:', clientId);
                    resolve(clientId || `visitor_${Date.now()}`);
                });
            } catch (error) {
                console.warn('[PersonalizationManager] Error getting GA4 ID:', error);
                resolve(`visitor_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
            }
        });
    }
    
    /**
     * Apply personalization rules to DOM
     */
    applyRules(rules) {
        const { priority_sections = [], featured_projects = [], highlight_skills = [] } = rules;
        
        // Priority sections: reorder
        if (priority_sections.length > 0) {
            console.log('[PersonalizationManager] Applying section priorities:', priority_sections);
            this.reorderSections(priority_sections);
        }
        
        // Featured projects: highlight
        if (featured_projects.length > 0) {
            console.log('[PersonalizationManager] Featuring projects:', featured_projects);
            this.highlightFeaturedProjects(featured_projects);
        }
        
        // Highlight skills
        if (highlight_skills.length > 0) {
            console.log('[PersonalizationManager] Highlighting skills:', highlight_skills);
            this.emphasizeSkills(highlight_skills);
        }
    }
    
    /**
     * Reorder sections based on priority
     */
    reorderSections(priority_sections) {
        // Find main content container
        const container = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;
        if (!container) return;
        
        const sections = Array.from(container.querySelectorAll('section[id]'));
        
        // Sort sections based on priority
        sections.sort((a, b) => {
            const aIndex = priority_sections.indexOf(a.id);
            const bIndex = priority_sections.indexOf(b.id);
            
            if (aIndex === -1 && bIndex === -1) return 0;
            if (aIndex === -1) return 1;
            if (bIndex === -1) return -1;
            return aIndex - bIndex;
        });
        
        // Reorder in DOM
        sections.forEach(section => {
            container.appendChild(section);
        });
    }
    
    /**
     * Highlight featured projects
     */
    highlightFeaturedProjects(featured_projects) {
        document.querySelectorAll('[data-project-id]').forEach(el => {
            const projectId = el.getAttribute('data-project-id');
            if (featured_projects.includes(projectId)) {
                el.classList.add('personalized-featured');
                el.style.order = '-1'; // Move to front if flex
                
                // Add badge
                const badge = document.createElement('div');
                badge.className = 'personalization-badge';
                badge.textContent = '⭐ Featured for you';
                badge.style.cssText = 'position: absolute; top: 10px; right: 10px; background: #FFD700; color: #000; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; z-index: 10;';
                
                if (el.style.position !== 'absolute' && el.style.position !== 'fixed') {
                    el.style.position = 'relative';
                }
                el.appendChild(badge);
            }
        });
    }
    
    /**
     * Emphasize skills
     */
    emphasizeSkills(highlight_skills) {
        document.querySelectorAll('[data-skill], .skill, .skill-tag').forEach(el => {
            const skill = el.getAttribute('data-skill') || el.textContent.trim().toLowerCase();
            if (highlight_skills.some(s => skill.toLowerCase().includes(s.toLowerCase()) || s.toLowerCase().includes(skill.toLowerCase()))) {
                el.classList.add('personalized-skill');
                el.style.fontWeight = 'bold';
                el.style.color = '#2563EB'; // Primary color
            }
        });
    }
    
    /**
     * Track personalization event
     */
    trackPersonalizationApplied(segment) {
        try {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'personalization_applied', {
                    'segment': segment,
                    'timestamp': new Date().toISOString()
                });
                console.log('[PersonalizationManager] Tracked personalization_applied event');
            }
        } catch (error) {
            console.warn('[PersonalizationManager] Failed to track event:', error);
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const pm = new PersonalizationManager('/api');
    pm.init();
});
