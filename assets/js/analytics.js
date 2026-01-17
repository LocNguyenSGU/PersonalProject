/**
 * Analytics Event Tracker
 * Sends custom events to GA4
 */
const AnalyticsTracker = {
    // Utility to send custom events to GA4
    
    /**
     * Track project click
     */
    trackProjectClick(projectId, category) {
        gtag('event', 'project_click', {
            'project_id': projectId,
            'category': category,
            'timestamp': Date.now()
        });
        console.log('[Analytics] project_click:', { projectId, category });
    },
    
    /**
     * Track section view
     */
    trackSectionView(sectionName, duration) {
        gtag('event', 'section_view', {
            'section_name': sectionName,
            'time_spent': duration,
            'timestamp': Date.now()
        });
        console.log('[Analytics] section_view:', { sectionName, duration });
    },
    
    /**
     * Track contact intent
     */
    trackContactIntent(contactType) {
        gtag('event', 'contact_intent', {
            'contact_type': contactType,
            'timestamp': Date.now()
        });
        console.log('[Analytics] contact_intent:', { contactType });
    },
    
    /**
     * Track skill hover
     */
    trackSkillHover(skillName, duration) {
        gtag('event', 'skill_hover', {
            'skill_name': skillName,
            'duration': duration,
            'timestamp': Date.now()
        });
        console.log('[Analytics] skill_hover:', { skillName, duration });
    },
    
    /**
     * Track deep read
     */
    trackDeepRead(projectId, duration) {
        gtag('event', 'deep_read', {
            'project_id': projectId,
            'duration': duration,
            'timestamp': Date.now()
        });
        console.log('[Analytics] deep_read:', { projectId, duration });
    },
    
    /**
     * Track scroll depth
     */
    trackScrollDepth(milestone) {
        gtag('event', 'scroll_depth', {
            'milestone': milestone,
            'timestamp': Date.now()
        });
        console.log('[Analytics] scroll_depth:', { milestone });
    },
    
    /**
     * Track language switch
     */
    trackLanguageSwitch(fromLang, toLang) {
        gtag('event', 'language_switch', {
            'from_lang': fromLang,
            'to_lang': toLang,
            'timestamp': Date.now()
        });
        console.log('[Analytics] language_switch:', { fromLang, toLang });
    }
};

// Auto-setup: Attach tracking to common elements
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Analytics] Setting up event listeners...');
    
    // Project card clicks
    document.querySelectorAll('[data-project-id]').forEach(card => {
        card.addEventListener('click', () => {
            const projectId = card.getAttribute('data-project-id');
            const category = card.getAttribute('data-category') || 'general';
            AnalyticsTracker.trackProjectClick(projectId, category);
        });
    });
    
    // Contact button clicks
    document.querySelectorAll('[data-contact-type]').forEach(btn => {
        btn.addEventListener('click', () => {
            const contactType = btn.getAttribute('data-contact-type');
            AnalyticsTracker.trackContactIntent(contactType);
        });
    });
    
    // Scroll tracking
    let scrollTracked = false;
    window.addEventListener('scroll', () => {
        const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        
        if (scrollPercent > 25 && !scrollTracked) {
            AnalyticsTracker.trackScrollDepth('25%');
            scrollTracked = true;
        }
        if (scrollPercent > 50) {
            AnalyticsTracker.trackScrollDepth('50%');
        }
        if (scrollPercent > 75) {
            AnalyticsTracker.trackScrollDepth('75%');
        }
        if (scrollPercent > 100) {
            AnalyticsTracker.trackScrollDepth('100%');
        }
    });
});
