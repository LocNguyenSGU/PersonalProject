const projects = [
    {
        type: "basic",
        startDate: "01/07/2023",
        endDate: "01/07/2023",
        title: "Music Player",
        description: "Website nghe nhạc cơ bản được xây dựng bằng HTML, CSS và JavaScript thuần.",
        techStack: ["HTML5", "CSS3", "JavaScript"],
        role: "Solo Developer",
        whatILearned: "Cơ bản về DOM manipulation, Audio API, và event handling trong JavaScript.",
        link: "https://locnguyensgu.github.io/Music/",
        category: "Personal",
        impressive: false
    },
    {
        type: "basic",
        startDate: "01/09/2023",
        endDate: "31/12/2023",
        title: "E-commerce Website",
        description: "Website thương mại điện tử cơ bản được xây dựng bằng HTML, CSS và JavaScript thuần, sử dụng Local Storage làm cơ sở dữ liệu. Dự án của môn \"Website cơ bản\".",
        techStack: ["HTML5", "CSS3", "JavaScript", "Local Storage"],
        role: "Frontend Developer",
        whatILearned: "Làm việc với Local Storage, quản lý state trong vanilla JavaScript, responsive design và UX patterns cho e-commerce.",
        link: "https://github.com/LocNguyenSGU/DoAnWebN11",
        score: "9.5",
        category: "School Project",
        impressive: false
    },
    {
        type: "advanced",
        startDate: "01/02/2024",
        endDate: "31/05/2024",
        title: "SGU Test System",
        description: "Hệ thống thi trắc nghiệm được xây dựng bằng Java Servlet và JSP, dự án của môn \"Lập trình Java\".",
        techStack: ["Java Servlet", "JSP", "MySQL", "JDBC", "Bootstrap"],
        role: "Full-stack Developer",
        whatILearned: "Java Servlet architecture, session management, database design, và cách xây dựng hệ thống bảo mật cho ứng dụng thi trực tuyến.",
        link: "https://github.com/LocNguyenSGU/SGU-Test",
        score: "10",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "01/02/2024",
        endDate: "31/05/2024",
        title: "Tour Booking Website",
        description: "Website đặt tour du lịch xây dựng bằng PHP theo kiến trúc MVC, dự án của môn \"Website nâng cao\".",
        techStack: ["PHP", "MySQL", "MVC Pattern", "Bootstrap", "jQuery"],
        role: "Backend Developer",
        whatILearned: "Kiến trúc MVC trong PHP, xử lý thanh toán online, quản lý booking system và tối ưu hóa truy vấn database.",
        link: "https://github.com/lamkbvn/WEB2",
        score: "10",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "01/09/2024",
        endDate: "30/11/2024",
        title: "Sport Field Booking System - Backend",
        description: "Backend Spring Boot cung cấp API cho hệ thống đặt sân thể thao, dự án của môn \"Công nghệ J2EE\".",
        techStack: ["Spring Boot", "Spring Security", "MySQL", "JWT", "RESTful API"],
        role: "Backend Developer",
        whatILearned: "Spring Boot ecosystem, JWT authentication, RESTful API design patterns và microservices architecture cơ bản.",
        link: "https://github.com/LocNguyenSGU/SportFieldBookingSystem",
        score: "9",
        category: "School Project",
        impressive: false
    },
    {
        type: "basic",
        startDate: "01/09/2024",
        endDate: "30/11/2024",
        title: "Sport Field Booking System - Frontend",
        description: "Ứng dụng web React.js cho hệ thống đặt sân thể thao, dự án của môn \"Công nghệ J2EE\".",
        techStack: ["React.js", "Ant Design", "Axios", "React Router"],
        role: "Frontend Developer",
        whatILearned: "React component lifecycle, state management với hooks, integration với RESTful API và UI/UX design cho booking system.",
        link: "https://github.com/duylam15/react-sport-field-booking-system",
        score: "9",
        category: "School Project",
        impressive: false
    },
    {
        type: "advanced",
        startDate: "01/09/2024",
        endDate: "30/11/2024",
        title: "Flight Management System - Backend",
        description: "Backend Spring Boot cung cấp API cho hệ thống quản lý chuyến bay, dự án của môn \"Công nghệ phần mềm\".",
        techStack: ["Spring Boot", "Spring Data JPA", "MySQL", "Spring Security", "Redis"],
        role: "Backend Lead Developer",
        whatILearned: "Complex business logic implementation, caching strategies với Redis, transaction management và software engineering best practices.",
        link: "https://github.com/kietsocola/FlightManagementSystem",
        score: "9",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "01/09/2024",
        endDate: "30/11/2024",
        title: "Flight Management System - Frontend",
        description: "Ứng dụng web React.js cho hệ thống quản lý chuyến bay, dự án của môn \"Công nghệ phần mềm\".",
        techStack: ["React.js", "Redux Toolkit", "Material-UI", "React Query"],
        role: "Frontend Developer",
        whatILearned: "Advanced state management với Redux Toolkit, data fetching patterns với React Query, và complex form handling.",
        link: "https://github.com/duylam15/react-flight-management-system",
        score: "9",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "01/12/2024",
        endDate: "29/05/2025",
        title: "Calligo Frontend",
        description: "Ứng dụng web chat và gọi hiện đại được phát triển bằng React.js và Ant Design, mang đến trải nghiệm giao tiếp thời gian thực mượt mà.",
        techStack: ["React.js", "Ant Design", "WebSocket", "WebRTC", "Axios"],
        role: "Frontend Developer",
        whatILearned: "Real-time communication với WebSocket, WebRTC implementation cho video/voice call, và performance optimization cho real-time apps.",
        link: "https://github.com/LocNguyenSGU/Calligo-FE",
        category: "Team Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "01/12/2024",
        endDate: "28/05/2025",
        title: "Calligo Backend",
        description: "Hệ thống backend xây dựng bằng Spring Boot với kiến trúc microservices, hỗ trợ chat và gọi thoại/video theo thời gian thực.",
        techStack: ["Spring Boot", "WebSocket", "Microservices", "Redis", "MySQL", "RabbitMQ"],
        role: "Backend Architect",
        whatILearned: "Microservices architecture, message queue với RabbitMQ, WebSocket scaling, và distributed system design patterns.",
        link: "https://github.com/LocNguyenSGU/Calligo",
        category: "Team Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "23/02/2025",
        endDate: "15/04/2025",
        title: "Clone Instagram",
        description: "Frontend React TypeScript xây dựng ứng dụng giống Instagram, kết nối với backend Social Media.",
        techStack: ["React", "TypeScript", "Redux", "Tailwind CSS", "WebSocket"],
        role: "Frontend Developer",
        whatILearned: "TypeScript best practices, advanced React patterns, real-time features implementation, và infinite scroll optimization.",
        link: "https://github.com/duylam15/react-Instagram-clone",
        score: "9",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "23/02/2025",
        endDate: "14/04/2025",
        title: "Social Media",
        description: "Backend Spring Boot cung cấp API cho mạng xã hội tương tự Instagram, tích hợp các công nghệ như JWT, Redis, Spring Security, WebSocket, RabbitMQ, MySQL, OpenAI, GeminiAI.",
        techStack: ["Spring Boot", "Spring Security", "Redis", "WebSocket", "RabbitMQ", "MySQL", "OpenAI API", "Gemini AI"],
        role: "Backend Lead Developer",
        whatILearned: "AI integration trong backend, advanced caching strategies, real-time notification system, và scalable architecture design.",
        link: "https://github.com/LocNguyenSGU/SocialMedia",
        score: "9",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "01/03/2025",
        endDate: "14/04/2025",
        title: "Clone Spotify",
        description: "Frontend React TypeScript xây dựng ứng dụng nghe nhạc giống Spotify, kết nối với backend Social Media.",
        techStack: ["React", "TypeScript", "Redux Toolkit", "Tailwind CSS", "Web Audio API"],
        role: "Frontend Developer",
        whatILearned: "Audio streaming optimization, complex state management for media player, advanced TypeScript patterns, và performance tuning.",
        link: "https://github.com/duylam15/react-clone-spotify",
        score: "9.5",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "01/03/2025",
        endDate: "14/04/2025",
        title: "Backend Spotify",
        description: "Hệ thống backend Django cung cấp API cho ứng dụng Spotify, sử dụng các công nghệ như JWT, WebSocket, MySQL, OpenAI, GeminiAI và huấn luyện mô hình.",
        techStack: ["Django", "Django REST Framework", "WebSocket", "MySQL", "OpenAI API", "Gemini AI", "Machine Learning"],
        role: "Backend Developer & ML Engineer",
        whatILearned: "Django REST Framework patterns, ML model training và deployment, music recommendation algorithms, và API optimization.",
        link: "https://github.com/lamkbvn/BACKEND_SPOTIFY",
        score: "9.5",
        category: "School Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "03/03/2025",
        endDate: "22/05/2025",
        title: "NCKH: Nhận diện cảm xúc khuôn mặt",
        description: "Dự án NCKH phát triển hệ thống nhận diện biểu cảm khuôn mặt trong điều kiện ánh sáng yếu, sử dụng MobileNetV3 kết hợp thuật toán tăng cường dữ liệu thích ứng để điều chỉnh độ sáng và cải thiện độ chính xác.",
        techStack: ["Python", "TensorFlow", "MobileNetV3", "OpenCV", "NumPy", "Data Augmentation"],
        role: "ML Research Engineer",
        whatILearned: "Deep learning cho computer vision, model optimization techniques, data augmentation strategies, và research methodology.",
        link: "https://github.com/lamkbvn/DO_AN_PPNCKH",
        score: "9.8",
        category: "Research Project",
        impressive: true
    },
    {
        type: "advanced",
        startDate: "22/03/2025",
        endDate: "23/03/2025",
        title: "EduMind",
        description: "Phát triển nền tảng học tập ứng dụng AI tích hợp mind mapping, tóm tắt nội dung, bài tập và thảo luận bằng OpenAI.",
        techStack: ["React", "TypeScript", "OpenAI API", "Node.js", "MongoDB", "TailwindCSS"],
        role: "Full-stack Developer",
        whatILearned: "Rapid prototyping, AI prompt engineering, building MVP under time constraints, và hackathon best practices.",
        link: "https://github.com/LocNguyenSGU/Hackathon_Luong_Nghin_Do",
        hackathon: "Top 2",
        category: "Hackathon",
        impressive: true
    },
    {
        type: "basic",
        startDate: "01/03/2025",
        endDate: "Now",
        title: "Personal Website",
        description: "Website cá nhân để giới thiệu bản thân, các dự án và kỹ năng, tải CV và liên hệ.",
        techStack: ["HTML5", "CSS3", "JavaScript", "Responsive Design"],
        role: "Designer & Developer",
        whatILearned: "Personal branding, portfolio design best practices, SEO basics, và web performance optimization.",
        link: "https://github.com/LocNguyenSGU/nguyenhuuloc2k4",
        category: "Personal",
        impressive: false
    },
    {
        type: "advanced",
        startDate: "01/07/2025",
        endDate: "19/01/2026",
        title: "Khoá luận tốt nghiệp: Ứng dụng trí tuệ nhân tạo trong xây dựng hệ thống học tăng cường hỗ trợ dạy và học STEM",
        description: "Dự án KLTN xây dựng hệ thống theo kiến trúc microservice đằng sau tích hợp hỗ trợ cho Moodle phía trước.",
        techStack: ["Spring Boot", "Microservices", "Moodle", "AI/ML", "Docker", "Kubernetes", "PostgreSQL"],
        role: "System Architect & Lead Developer",
        whatILearned: "Advanced microservices architecture, LMS integration, AI-powered education systems, containerization và orchestration với K8s.",
        category: "Thesis Project",
        score: "10",
        impressive: true
    }
];

// Helper function to format date for display
function formatDate(dateStr) {
    if (dateStr === "Now") return "Hiện tại";
    const [day, month, year] = dateStr.split('/');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${months[parseInt(month) - 1]} ${year}`;
}

// Helper function to calculate project duration
function calculateDuration(startDate, endDate) {
    const start = parseDate(startDate);
    const end = endDate === "Now" ? new Date() : parseDate(endDate);
    const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
    return months > 0 ? `${months} tháng` : '< 1 tháng';
}

// Helper function to parse date string
function parseDate(dateStr) {
    if (dateStr === "Now") return new Date();
    const [day, month, year] = dateStr.split('/');
    return new Date(year, month - 1, day);
}

// Filter state
let currentFilter = 'all'; // 'all' or 'impressive'

// Sort projects by start date (newest first for timeline display)
const sortedProjects = [...projects].sort((a, b) => {
    return parseDate(b.startDate) - parseDate(a.startDate);
});

// Get category badge color
function getCategoryBadgeColor(category) {
    const colors = {
        "School Project": "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
        "Personal": "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400",
        "Team Project": "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400",
        "Research Project": "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400",
        "Hackathon": "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400",
        "Thesis Project": "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400"
    };
    return colors[category] || "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300";
}

// Filter projects based on current filter
function getFilteredProjects() {
    if (currentFilter === 'impressive') {
        return sortedProjects.filter(p => p.impressive === true);
    }
    return sortedProjects;
}

// Split projects into two columns (zigzag pattern for timeline)
function splitIntoColumns(projectsList) {
    const leftColumn = [];
    const rightColumn = [];
    
    projectsList.forEach((project, index) => {
        if (index % 2 === 0) {
            leftColumn.push(project);
        } else {
            rightColumn.push(project);
        }
    });
    
    return { leftColumn, rightColumn };
}

// Render a single project card
function renderProjectCard(project, isOngoing) {
    const duration = calculateDuration(project.startDate, project.endDate);
    
    return `
        <div class="relative group mb-8">
            <!-- Timeline dot -->
            <div class="absolute -left-6 top-3 w-4 h-4 rounded-full ${isOngoing ? 'bg-primary animate-pulse' : 'bg-slate-400 dark:bg-slate-500'} border-4 border-white dark:border-slate-900 group-hover:scale-125 transition-transform duration-200 z-10"></div>
            
            <!-- Project Card -->
            <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 hover:border-primary dark:hover:border-primary transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md">
                <!-- Header -->
                <div class="flex flex-col gap-2 mb-3">
                    <div class="flex items-start justify-between gap-2">
                        <h3 class="text-base font-semibold text-slate-900 dark:text-white leading-tight flex-1">${project.title}</h3>
                        ${project.impressive ? '<span class="flex-shrink-0 w-2 h-2 bg-amber-500 rounded-full" title="Dự án ấn tượng"></span>' : ''}
                    </div>
                    <div class="flex flex-wrap items-center gap-2">
                        ${project.score ? `<span class="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-full">Điểm: ${project.score}/10</span>` : ''}
                        ${project.hackathon ? `<span class="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-semibold rounded-full">${project.hackathon}</span>` : ''}
                        <span class="px-2 py-0.5 ${getCategoryBadgeColor(project.category)} text-xs font-medium rounded-md">
                            ${project.category}
                        </span>
                    </div>
                </div>
                
                <!-- Timeline info -->
                <div class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-3">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    <span>${formatDate(project.startDate)} - ${formatDate(project.endDate)}</span>
                    <span class="text-slate-400 dark:text-slate-600">•</span>
                    <span>${duration}</span>
                </div>
                
                <!-- Description -->
                <p class="text-slate-600 dark:text-slate-300 mb-3 text-sm leading-relaxed">
                    ${project.description}
                </p>
                
                <!-- Tech Stack -->
                <div class="mb-3">
                    <div class="flex flex-wrap gap-1.5">
                        ${project.techStack.map(tech => `
                            <span class="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 text-xs font-medium rounded">${tech}</span>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Role & Link -->
                <div class="flex items-center justify-between gap-2 pt-3 border-t border-slate-100 dark:border-slate-700">
                    <span class="text-xs text-slate-600 dark:text-slate-400">${project.role}</span>
                    ${project.link ? `
                        <a href="${project.link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-xs font-medium text-primary hover:text-blue-700 dark:hover:text-blue-400 transition-colors duration-200">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd"></path>
                            </svg>
                            <span class="hidden sm:inline">Code</span>
                        </a>
                    ` : ''}
                </div>
                
                <!-- What I Learned - Expandable -->
                <details class="mt-3 group/details">
                    <summary class="cursor-pointer text-xs font-semibold text-amber-900 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 transition-colors list-none flex items-center gap-1">
                        <svg class="w-3 h-3 transition-transform group-open/details:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                        What I Learned
                    </summary>
                    <div class="mt-2 bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 rounded-lg p-2.5">
                        <p class="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">${project.whatILearned}</p>
                    </div>
                </details>
            </div>
        </div>
    `;
}

// Render projects function
function renderProjects() {
    const projectsContainer = document.getElementById('projects-container');
    if (!projectsContainer) return;

    const filteredProjects = getFilteredProjects();
    
    if (filteredProjects.length === 0) {
        projectsContainer.innerHTML = `
            <div class="col-span-2 text-center py-12">
                <p class="text-slate-600 dark:text-slate-400">Không tìm thấy dự án nào.</p>
            </div>
        `;
        return;
    }

    const { leftColumn, rightColumn } = splitIntoColumns(filteredProjects);
    
    // Render left column
    const leftHtml = leftColumn.map(project => {
        const isOngoing = project.endDate === "Now";
        return renderProjectCard(project, isOngoing);
    }).join('');
    
    // Render right column
    const rightHtml = rightColumn.map(project => {
        const isOngoing = project.endDate === "Now";
        return renderProjectCard(project, isOngoing);
    }).join('');
    
    projectsContainer.innerHTML = `
        <!-- Left Column -->
        <div class="relative pl-6">
            <!-- Timeline line -->
            <div class="absolute left-0 top-0 bottom-0 w-px bg-slate-300 dark:bg-slate-600"></div>
            ${leftHtml}
        </div>
        
        <!-- Right Column -->
        <div class="relative pl-6">
            <!-- Timeline line -->
            <div class="absolute left-0 top-0 bottom-0 w-px bg-slate-300 dark:bg-slate-600"></div>
            ${rightHtml}
        </div>
    `;
    
    // Update project count
    updateProjectCount(filteredProjects.length, projects.length);
}

// Update project count display
function updateProjectCount(showing, total) {
    const countElement = document.getElementById('project-count');
    if (countElement && window.i18n) {
        countElement.textContent = currentFilter === 'all' 
            ? window.i18n.format('projects.allProjects', { count: total })
            : window.i18n.format('projects.impressiveProjects', { count: showing });
    }
}

// Filter button handlers
function setupFilterButtons() {
    const allBtn = document.getElementById('filter-all');
    const impressiveBtn = document.getElementById('filter-impressive');
    
    if (allBtn) {
        allBtn.addEventListener('click', () => {
            currentFilter = 'all';
            updateFilterButtons();
            renderProjects();
        });
    }
    
    if (impressiveBtn) {
        impressiveBtn.addEventListener('click', () => {
            currentFilter = 'impressive';
            updateFilterButtons();
            renderProjects();
        });
    }
}

// Update filter button styles
function updateFilterButtons() {
    const allBtn = document.getElementById('filter-all');
    const impressiveBtn = document.getElementById('filter-impressive');
    
    if (currentFilter === 'all') {
        allBtn?.classList.add('bg-primary', 'text-white');
        allBtn?.classList.remove('bg-white', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
        
        impressiveBtn?.classList.remove('bg-primary', 'text-white');
        impressiveBtn?.classList.add('bg-white', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
    } else {
        impressiveBtn?.classList.add('bg-primary', 'text-white');
        impressiveBtn?.classList.remove('bg-white', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
        
        allBtn?.classList.remove('bg-primary', 'text-white');
        allBtn?.classList.add('bg-white', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setupFilterButtons();
        renderProjects();
    });
} else {
    setupFilterButtons();
    renderProjects();
}

// Re-render when language changes
window.addEventListener('languageChanged', () => {
    updateProjectCount(getFilteredProjects().length, projects.length);
});
