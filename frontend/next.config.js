/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        domains: ['localhost', 'your-s3-bucket.s3.amazonaws.com', 'res.cloudinary.com'],
        unoptimized: true, // Output standalone html if needed
    },
    env: {
        API_URL: process.env.API_URL || 'http://localhost:8000',
    },
}

module.exports = nextConfig
