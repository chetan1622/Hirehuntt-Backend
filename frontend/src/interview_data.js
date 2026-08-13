export const INTERVIEW_DATA = {
  "Software Engineer": [
    { q: "What is the difference between OOP and functional programming?", a: "OOP is based on objects and data encapsulation (e.g. Java, C++). Functional programming focuses on pure functions and immutability (e.g. Haskell, React Hooks)." },
    { q: "Explain the concept of REST APIs.", a: "REST (Representational State Transfer) is an architectural style for APIs that uses standard HTTP methods (GET, POST, PUT, DELETE) to manage resources via stateless operations." },
    { q: "What is time complexity (Big O notation)?", a: "It describes the worst-case scenario of an algorithm's execution time or space used based on the size of the input data (e.g. O(1), O(n), O(n^2))." },
    { q: "How do you handle memory leaks?", a: "By avoiding global variables, managing event listeners properly, using weak references, and profiling memory usage using dev tools." },
    { q: "Explain CI/CD.", a: "Continuous Integration automates code testing and merging. Continuous Deployment automatically releases the verified code to production." }
  ],
  "Data Analyst": [
    { q: "What is the difference between Data Mining and Data Profiling?", a: "Data profiling assesses data quality and structure. Data mining discovers patterns and relationships within the data to predict outcomes." },
    { q: "Explain the difference between WHERE and HAVING in SQL.", a: "WHERE filters rows before grouping. HAVING filters aggregated data after the GROUP BY clause." },
    { q: "What is Data Normalization?", a: "It's the process of organizing data to minimize redundancy and dependency, usually by dividing large tables into smaller related ones." },
    { q: "How do you handle missing values?", a: "You can remove the rows/columns, impute them with mean/median/mode, or use predictive models to estimate the missing values." },
    { q: "What is the difference between a JOIN and UNION?", a: "JOIN combines columns from multiple tables based on a related key. UNION combines rows from multiple queries with the same structure." }
  ],
  "HR Manager": [
    { q: "How do you handle conflicts between employees?", a: "I listen to both sides neutrally, identify the root cause, and facilitate a collaborative discussion to reach a professional resolution." },
    { q: "What is your recruitment strategy?", a: "I use a mix of inbound marketing, active sourcing on platforms like LinkedIn, employee referrals, and structured interview rubrics to find culture-add candidates." },
    { q: "How do you ensure employee retention?", a: "By fostering a transparent culture, offering clear career growth paths, ensuring competitive compensation, and maintaining open feedback loops." },
    { q: "What are the essential labor laws to keep in mind?", a: "Key laws involve minimum wage, working hours, anti-discrimination laws, maternity/paternity leave, and workplace safety regulations." },
    { q: "How do you measure employee engagement?", a: "Through regular anonymous pulse surveys, tracking turnover rates, analyzing eNPS (Employee Net Promoter Score), and conducting stay interviews." }
  ],
  "Marketing Manager": [
    { q: "What is the difference between B2B and B2C marketing?", a: "B2B focuses on logical ROI-driven decisions and relationship building. B2C appeals to emotions, quick purchasing decisions, and brand identity." },
    { q: "How do you measure the success of a campaign?", a: "By tracking KPIs such as Conversion Rate, Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), and overall engagement metrics." },
    { q: "What is SEO and why is it important?", a: "Search Engine Optimization improves organic visibility on search engines, driving high-intent, free traffic to the website over the long term." },
    { q: "How do you handle negative PR or comments?", a: "Acknowledge the issue promptly and politely, move the conversation to private channels, and provide a transparent resolution." },
    { q: "Explain the AIDA model.", a: "It stands for Attention, Interest, Desire, and Action. It maps the customer journey from first hearing about a product to making a purchase." }
  ]
};

// Fallback for roles not directly mapped
export const GENERAL_INTERVIEW_DATA = [
  { q: "Tell me about yourself.", a: "Keep it professional. Cover your current role, key past achievements, and how your experience aligns with the job you are applying for." },
  { q: "Why do you want to work here?", a: "Research the company beforehand. Mention their recent projects, company culture, or values that resonate with your career goals." },
  { q: "What is your greatest weakness?", a: "Share a real, minor weakness and immediately explain the actionable steps you are taking to improve it." },
  { q: "Where do you see yourself in 5 years?", a: "Focus on your career growth, acquiring new skills, and taking on more responsibilities within the industry." },
  { q: "Do you have any questions for us?", a: "Always say yes. Ask about the team structure, the biggest challenges the role faces, or the company's future goals." }
];
