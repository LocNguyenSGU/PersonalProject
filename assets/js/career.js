// Career/Work Experience Data
const careerExperience = [
    {
        title: "Intern — Full stack Developer",
        company: "DG External",
        startDate: "Sep 2025",
        endDate: "Present",
        duration: "4 months",
        description: "A fast-growing product company specializing in dropshipping solutions.",
        responsibilities: "Tham gia phát triển các sản phẩm cho công ty.",
        techStack: ["Ruby", "Shopify", "PostgreSQL"],
        companyUrl: "#",
        type: "Internship"
    }
    // Add more career entries here as needed
];

// Tech stack logos mapping
const techLogos = {
    "Ruby": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ruby/ruby-original.svg",
    "Shopify": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/shopify.svg",
    "PostgreSQL": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg",
    "Spring Boot": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/spring/spring-original.svg",
    "React": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg",
    "TypeScript": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg",
    "JavaScript": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg",
    "Python": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg",
    "Django": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/django/django-plain.svg",
    "MySQL": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg",
    "MongoDB": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg",
    "Redis": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg",
    "Docker": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg",
    "Git": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg"
};

// Calculate duration from dates
function calculateCareerDuration(startDate, endDate) {
    const months = {
        'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
        'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
    };
    
    const [startMonth, startYear] = startDate.split(' ');
    const start = new Date(parseInt(startYear), months[startMonth]);
    
    let end;
    if (endDate === 'Present') {
        end = new Date();
    } else {
        const [endMonth, endYear] = endDate.split(' ');
        end = new Date(parseInt(endYear), months[endMonth]);
    }
    
    const monthsDiff = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
    
    if (monthsDiff < 1) return '< 1 tháng';
    if (monthsDiff === 1) return '1 tháng';
    if (monthsDiff < 12) return `${monthsDiff} tháng`;
    
    const years = Math.floor(monthsDiff / 12);
    const remainingMonths = monthsDiff % 12;
    
    if (remainingMonths === 0) return `${years} năm`;
    return `${years} năm ${remainingMonths} tháng`;
}

// Render career experience
function renderCareer() {
    const careerContainer = document.getElementById('career-container');
    if (!careerContainer) return;
    
    const html = careerExperience.map((job, index) => {
        const duration = job.duration || calculateCareerDuration(job.startDate, job.endDate);
        const isCurrentJob = job.endDate === 'Present';
        
        return `
            <div class="relative group" data-career-company="${job.company}" data-career-position="${job.title}">
                <!-- Timeline connector -->
                ${index > 0 ? '<div class="absolute left-4 -top-6 w-0.5 h-6 bg-slate-300 dark:bg-slate-600"></div>' : ''}
                
                <!-- Timeline dot -->
                <div class="absolute left-0 top-6 w-8 h-8 rounded-full ${isCurrentJob ? 'bg-gradient-to-br from-purple-500 to-primary' : 'bg-slate-400 dark:bg-slate-600'} border-4 border-white dark:border-slate-900 group-hover:scale-110 transition-transform duration-200 z-10 flex items-center justify-center">
                    ${isCurrentJob ? '<div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>' : ''}
                </div>
                
                <!-- Career Card -->
                <div class="ml-16 bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 hover:border-primary dark:hover:border-primary transition-all duration-200 shadow-sm hover:shadow-md">
                    <!-- Header -->
                    <div class="mb-4">
                        <h3 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                            ${job.title} — <span class="text-primary">${job.company}</span>
                        </h3>
                        <div class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                            <span>${job.startDate} — ${job.endDate === 'Present' ? '<span class="text-green-600 dark:text-green-400 font-semibold">Hiện tại</span>' : job.endDate}</span>
                            <span class="text-slate-400 dark:text-slate-600">•</span>
                            <span>${duration}</span>
                        </div>
                        <span class="inline-block px-2.5 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-xs font-medium rounded-lg">
                            ${job.type}
                        </span>
                    </div>
                    
                    <!-- Description -->
                    <p class="text-slate-600 dark:text-slate-400 mb-3 text-sm italic leading-relaxed">
                        ${job.description}
                    </p>
                    
                    <!-- Responsibilities -->
                    <p class="text-slate-700 dark:text-slate-300 mb-4 leading-relaxed">
                        ${job.responsibilities}
                    </p>
                    
                    <!-- Tech Stack Tags -->
                    <div class="mb-4">
                        <div class="flex flex-wrap gap-2">
                            ${job.techStack.map(tech => `
                                <span class="px-3 py-1.5 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm font-medium rounded-lg">
                                    ${tech}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- Tech Stack Icons -->
                    <div class="flex items-center gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
                        ${job.techStack.slice(0, 5).map(tech => {
                            const logo = techLogos[tech];
                            if (!logo) return '';
                            return `
                                <div class="w-12 h-12 p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg hover:scale-110 transition-transform duration-200" title="${tech}">
                                    <img src="${logo}" alt="${tech}" class="w-full h-full object-contain ${tech === 'Shopify' ? 'dark:invert' : ''}" />
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    careerContainer.innerHTML = html;
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderCareer);
} else {
    renderCareer();
}
