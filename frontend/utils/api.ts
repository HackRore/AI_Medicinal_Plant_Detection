export const getApiBase = () => {
    if (typeof window !== 'undefined') {
        if (window.location.hostname.includes('vercel.app')) {
            return "https://plantoai-backend.onrender.com";
        }
    }
    return process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com";
};
