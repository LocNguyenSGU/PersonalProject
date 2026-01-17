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
    },
    
    /**
     * Track repeat view
     */
    trackRepeatView(itemId, viewCount) {
        gtag('event', 'repeat_view', {
            'item_id': itemId,
            'view_count': viewCount,
            'timestamp': Date.now()
        });
        console.log('[Analytics] repeat_view:', { itemId, viewCount });
    },
    
    /**
     * Track career timeline interaction
     */
    trackCareerTimelineInteract(company, position) {
        gtag('event', 'career_timeline_interact', {
            'company': company,
            'position': position,
            'timestamp': Date.now()
        });
        console.log('[Analytics] career_timeline_interact:', { company, position });
    },
    
    /**
     * Track resume download
     */
    trackDownloadResume() {
        gtag('event', 'download_resume', {
            'timestamp': Date.now()
        });
        console.log('[Analytics] download_resume');
    },
    
    /**
     * Track external link click
     */
    trackExternalLinkClick(linkType, destination) {
        gtag('event', 'external_link_click', {
            'link_type': linkType,
            'destination': destination,
            'timestamp': Date.now()
        });
        console.log('[Analytics] external_link_click:', { linkType, destination });
    },
    
    /**
     * Internal helper: Track time spent on element
     */
    _trackTimeOnElement(element, eventCallback) {
        let startTime = null;
        let duration = 0;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    startTime = Date.now();
                } else if (startTime) {
                    duration = Date.now() - startTime;
                    if (duration > 3000) { // Only track if > 3 seconds
                        eventCallback(duration);
                    }
                    startTime = null;
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(element);
        return observer;
    },
    
    /**
     * Internal helper: Track view counts for repeat visits
     */
    _trackRepeatViews() {
        const viewCounts = JSON.parse(localStorage.getItem('analytics_view_counts') || '{}');
        
        return {
            increment(itemId) {
                viewCounts[itemId] = (viewCounts[itemId] || 0) + 1;
                localStorage.setItem('analytics_view_counts', JSON.stringify(viewCounts));
                
                if (viewCounts[itemId] > 1) {
                    AnalyticsTracker.trackRepeatView(itemId, viewCounts[itemId]);
                }
            }
        };
    }
};

// Auto-setup: Attach tracking to common elements
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Analytics] Setting up event listeners...');
    
    const repeatViewTracker = AnalyticsTracker._trackRepeatViews();
    
    // Project card clicks with repeat view tracking
    document.querySelectorAll('[data-project-id]').forEach(card => {
        card.addEventListener('click', () => {
            const projectId = card.getAttribute('data-project-id');
            const category = card.getAttribute('data-category') || 'general';
            AnalyticsTracker.trackProjectClick(projectId, category);
            repeatViewTracker.increment(projectId);
        });
        
        // Deep read tracking (time spent on project card)
        AnalyticsTracker._trackTimeOnElement(card, (duration) => {
            const projectId = card.getAttribute('data-project-id');
            AnalyticsTracker.trackDeepRead(projectId, duration);
        });
    });
    
    // Contact button clicks
    document.querySelectorAll('[data-contact-type]').forEach(btn => {
        btn.addEventListener('click', () => {
            const contactType = btn.getAttribute('data-contact-type');
            AnalyticsTracker.trackContactIntent(contactType);
        });
    });
    
    // Skill hover tracking
    document.querySelectorAll('[data-skill-name]').forEach(skill => {
        let hoverStart = null;
        
        skill.addEventListener('mouseenter', () => {
            hoverStart = Date.now();
        });
        
        skill.addEventListener('mouseleave', () => {
            if (hoverStart) {
                const duration = Date.now() - hoverStart;
                if (duration > 500) { // Only track meaningful hovers (> 0.5s)
                    const skillName = skill.getAttribute('data-skill-name');
                    AnalyticsTracker.trackSkillHover(skillName, duration);
                }
                hoverStart = null;
            }
        });
    });
    
    // Section view tracking
    document.querySelectorAll('section[id]').forEach(section => {
        AnalyticsTracker._trackTimeOnElement(section, (duration) => {
            AnalyticsTracker.trackSectionView(section.id, duration);
        });
    });
    
    // Career timeline interaction tracking
    document.querySelectorAll('[data-career-company]').forEach(item => {
        item.addEventListener('click', () => {
            const company = item.getAttribute('data-career-company');
            const position = item.getAttribute('data-career-position') || 'Unknown';
            AnalyticsTracker.trackCareerTimelineInteract(company, position);
        });
    });
    
    // Resume download tracking
    document.querySelectorAll('[data-action="download-resume"]').forEach(btn => {
        btn.addEventListener('click', () => {
            AnalyticsTracker.trackDownloadResume();
        });
    });
    
    // External link click tracking
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        link.addEventListener('click', () => {
            const href = link.getAttribute('href');
            const linkType = link.getAttribute('data-link-type') || 'external';
            AnalyticsTracker.trackExternalLinkClick(linkType, href);
        });
    });
    
    // Scroll depth tracking (improved with debounce)
    let scrollTracked = {
        '25': false,
        '50': false,
        '75': false,
        '100': false
    };
    
    let scrollTimeout = null;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
            
            if (scrollPercent > 25 && !scrollTracked['25']) {
                AnalyticsTracker.trackScrollDepth('25%');
                scrollTracked['25'] = true;
            }
            if (scrollPercent > 50 && !scrollTracked['50']) {
                AnalyticsTracker.trackScrollDepth('50%');
                scrollTracked['50'] = true;
            }
            if (scrollPercent > 75 && !scrollTracked['75']) {
                AnalyticsTracker.trackScrollDepth('75%');
                scrollTracked['75'] = true;
            }
            if (scrollPercent >= 98 && !scrollTracked['100']) {
                AnalyticsTracker.trackScrollDepth('100%');
                scrollTracked['100'] = true;
            }
        }, 150); // Debounce 150ms
    });
    
    console.log('[Analytics] All event listeners attached successfully');
});
