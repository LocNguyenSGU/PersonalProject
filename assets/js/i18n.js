// i18n - Internationalization for Portfolio
const translations = {
    en: {
        // Navigation
        nav: {
            skills: "Skills",
            career: "Career",
            projects: "Projects",
            about: "About"
        },
        
        // Hero Section
        hero: {
            greeting: "Hi, I'm",
            title: "Full-Stack AI Developer",
            description: "Passionate about building scalable web applications with modern technologies. Experienced in microservices architecture, AI integration, and real-time systems.",
            viewWork: "View My Work",
            contact: "Contact Me",
            resumeTitle: "Resume Preview",
            lastUpdated: "Last updated: January 2026",
            viewCV: "View CV",
            downloadCV: "Download CV",
            cvPreview: "CV Preview",
            close: "Close"
        },
        
        // Skills Section
        skills: {
            title: "Skills & Expertise",
            subtitle: "Technologies and tools I work with",
            frontend: "Frontend",
            backend: "Backend",
            database: "Database & DevOps",
            advanced: "Advanced",
            intermediate: "Intermediate",
            additionalTech: "Additional Technologies & Frameworks",
            realtime: "Real-time & Messaging",
            aiMl: "AI & ML",
            softSkills: "Soft Skills",
            softSkillsList: {
                problemSolving: "Problem Solving",
                teamwork: "Team Collaboration",
                learning: "Quick Learning",
                communication: "Communication"
            }
        },
        
        // Career Section
        career: {
            title: "Career",
            subtitle: "My professional journey and work experience",
            present: "Present",
            months: "months",
            month: "month",
            years: "years",
            year: "year",
            lessThan: "< 1 month",
            loading: "Loading career information...",
            internship: "Internship",
            fulltime: "Full-time",
            parttime: "Part-time",
            freelance: "Freelance"
        },
        
        // Projects Section
        projects: {
            title: "Projects",
            subtitle: "A chronological journey through my development projects",
            filterAll: "All",
            filterImpressive: "Impressive Projects",
            allProjects: "All {count} projects",
            impressiveProjects: "{count} impressive projects",
            loading: "Loading projects...",
            noProjects: "No projects found.",
            categories: {
                school: "School Projects",
                thesis: "Thesis",
                research: "Research",
                hackathon: "Hackathon",
                team: "Team Projects",
                personal: "Personal"
            },
            score: "Score",
            role: "Role",
            duration: "Duration",
            techStack: "Tech Stack",
            whatLearned: "What I Learned",
            viewCode: "Code",
            now: "Now"
        },
        
        // About Section
        about: {
            title: "About Me",
            subtitle: "Getting to know the developer",
            education: "Education",
            languages: "Languages",
            degree: "Bachelor of Computer Science",
            university: "Saigon University • 2021-2025",
            gpa: "GPA: 3.5+/4.0",
            vietnamese: "Vietnamese (Native)",
            english: "English (Professional Working)",
            bio: {
                p1: "I am a final year Computer Science student at Saigon University, passionate about building web applications and distributed systems. From my first projects with HTML/CSS to complex microservices systems, I am always seeking opportunities to learn and apply new technologies.",
                p2: "With experience in 18+ projects, from Spring Boot/Django backend to React/TypeScript frontend, I have worked with many modern technologies such as microservices, WebSocket, AI integration, and real-time systems. I am particularly interested in building scalable system architectures and integrating AI into real-world applications.",
                p3: "Currently, I am working on my thesis on AI applications in reinforcement learning systems for STEM education. I am looking for internship/fresher developer opportunities to apply my knowledge to real projects and develop my professional skills."
            }
        },
        
        // Footer
        footer: {
            connect: "Let's Connect",
            subtitle: "Feel free to reach out for opportunities or collaboration!",
            email: "Email Me",
            github: "GitHub",
            linkedin: "LinkedIn",
            copyright: "Built with modern web technologies."
        }
    },
    
    vi: {
        // Navigation
        nav: {
            skills: "Kỹ năng",
            career: "Sự nghiệp",
            projects: "Dự án",
            about: "Giới thiệu"
        },
        
        // Hero Section
        hero: {
            greeting: "Xin chào, tôi là",
            title: "Lập trình viên Full-Stack AI",
            description: "Đam mê xây dựng các ứng dụng web có khả năng mở rộng với công nghệ hiện đại. Có kinh nghiệm về kiến trúc microservices, tích hợp AI và hệ thống thời gian thực.",
            viewWork: "Xem Dự Án",
            contact: "Liên Hệ",
            resumeTitle: "Xem Trước CV",
            lastUpdated: "Cập nhật: Tháng 1, 2026",
            viewCV: "Xem CV",
            downloadCV: "Tải CV",
            cvPreview: "Xem Trước CV",
            close: "Đóng"
        },
        
        // Skills Section
        skills: {
            title: "Kỹ Năng & Chuyên Môn",
            subtitle: "Công nghệ và công cụ tôi sử dụng",
            frontend: "Frontend",
            backend: "Backend",
            database: "Database & DevOps",
            advanced: "Nâng cao",
            intermediate: "Trung bình",
            additionalTech: "Công Nghệ & Framework Bổ Sung",
            realtime: "Thời gian thực & Messaging",
            aiMl: "AI & ML",
            softSkills: "Kỹ Năng Mềm",
            softSkillsList: {
                problemSolving: "Giải Quyết Vấn Đề",
                teamwork: "Làm Việc Nhóm",
                learning: "Học Hỏi Nhanh",
                communication: "Giao Tiếp"
            }
        },
        
        // Career Section
        career: {
            title: "Sự Nghiệp",
            subtitle: "Hành trình nghề nghiệp của tôi",
            present: "Hiện tại",
            months: "tháng",
            month: "tháng",
            years: "năm",
            year: "năm",
            lessThan: "< 1 tháng",
            loading: "Đang tải thông tin sự nghiệp...",
            internship: "Thực tập sinh",
            fulltime: "Toàn thời gian",
            parttime: "Bán thời gian",
            freelance: "Tự do"
        },
        
        // Projects Section
        projects: {
            title: "Dự Án",
            subtitle: "Hành trình phát triển kỹ năng qua các dự án thực tế",
            filterAll: "Tất cả",
            filterImpressive: "Dự án ấn tượng",
            allProjects: "Tất cả {count} dự án",
            impressiveProjects: "{count} dự án ấn tượng",
            loading: "Đang tải dự án...",
            noProjects: "Không tìm thấy dự án nào.",
            categories: {
                school: "Dự án Trường",
                thesis: "Khóa luận",
                research: "Nghiên cứu",
                hackathon: "Hackathon",
                team: "Dự án Nhóm",
                personal: "Cá nhân"
            },
            score: "Điểm",
            role: "Vai trò",
            duration: "Thời gian",
            techStack: "Công nghệ",
            whatLearned: "Kiến Thức Thu Được",
            viewCode: "Code",
            now: "Hiện tại"
        },
        
        // About Section
        about: {
            title: "Giới Thiệu",
            subtitle: "Tìm hiểu về lập trình viên",
            education: "Học vấn",
            languages: "Ngôn ngữ",
            degree: "Cử nhân Khoa học Máy tính",
            university: "Đại học Sài Gòn • 2021-2025",
            gpa: "GPA: 3.5+/4.0",
            vietnamese: "Tiếng Việt (Bản ngữ)",
            english: "Tiếng Anh (Làm việc chuyên nghiệp)",
            bio: {
                p1: "Tôi là sinh viên năm cuối ngành Khoa học Máy tính tại Đại học Sài Gòn, đam mê xây dựng các ứng dụng web và hệ thống phân tán. Từ những dự án đầu tiên với HTML/CSS đến các hệ thống microservices phức tạp, tôi luôn tìm kiếm cơ hội để học hỏi và áp dụng công nghệ mới.",
                p2: "Với kinh nghiệm phát triển 18+ dự án, từ backend Spring Boot/Django đến frontend React/TypeScript, tôi đã làm việc với nhiều công nghệ hiện đại như microservices, WebSocket, AI integration, và real-time systems. Tôi đặc biệt quan tâm đến việc xây dựng kiến trúc hệ thống scalable và tích hợp AI vào ứng dụng thực tế.",
                p3: "Hiện tại, tôi đang thực hiện khóa luận tốt nghiệp về ứng dụng AI trong hệ thống học tăng cường cho STEM education. Tôi mong muốn tìm kiếm cơ hội thực tập/fresher developer để áp dụng kiến thức vào các dự án thực tế và phát triển kỹ năng chuyên môn."
            }
        },
        
        // Footer
        footer: {
            connect: "Kết Nối",
            subtitle: "Liên hệ với tôi để hợp tác hoặc cơ hội làm việc!",
            email: "Gửi Email",
            github: "GitHub",
            linkedin: "LinkedIn",
            copyright: "Xây dựng với công nghệ web hiện đại."
        }
    }
};

// i18n class
class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'vi';
        this.translations = translations;
    }
    
    // Get translation by key
    t(key) {
        const keys = key.split('.');
        let value = this.translations[this.currentLang];
        
        for (const k of keys) {
            if (value && typeof value === 'object') {
                value = value[k];
            } else {
                return key;
            }
        }
        
        return value || key;
    }
    
    // Format string with variables
    format(key, variables) {
        let text = this.t(key);
        for (const [varKey, varValue] of Object.entries(variables)) {
            text = text.replace(`{${varKey}}`, varValue);
        }
        return text;
    }
    
    // Change language
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLang = lang;
            localStorage.setItem('language', lang);
            this.updatePage();
            // Trigger re-render for dynamic content
            window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
        }
    }
    
    // Get current language
    getLanguage() {
        return this.currentLang;
    }
    
    // Update all elements with data-i18n attribute
    updatePage() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            
            if (element.hasAttribute('data-i18n-placeholder')) {
                element.placeholder = translation;
            } else if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.value = translation;
            } else {
                element.textContent = translation;
            }
        });
        
        // Update HTML lang attribute
        document.documentElement.lang = this.currentLang;
        
        // Update language toggle button state
        this.updateLanguageToggle();
    }
    
    // Update language toggle button
    updateLanguageToggle() {
        const enBtn = document.getElementById('lang-en');
        const viBtn = document.getElementById('lang-vi');
        
        if (this.currentLang === 'en') {
            enBtn?.classList.add('active');
            viBtn?.classList.remove('active');
        } else {
            viBtn?.classList.add('active');
            enBtn?.classList.remove('active');
        }
    }
}

// Create global i18n instance
const i18n = new I18n();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    i18n.updatePage();
    
    // Language toggle handlers
    const enBtn = document.getElementById('lang-en');
    const viBtn = document.getElementById('lang-vi');
    
    enBtn?.addEventListener('click', () => i18n.setLanguage('en'));
    viBtn?.addEventListener('click', () => i18n.setLanguage('vi'));
});

// Export for use in other scripts
window.i18n = i18n;
