"use client";

import { useEffect } from "react";

export const BackendWarmup = () => {
    useEffect(() => {
        // Silently wake up the Render backend on page load (Spec v2.0 Part 5.2)
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com";
        fetch(`${apiUrl}/ping`)
            .catch(() => {}); // silent fail — just warming up
    }, []);

    return null;
};
