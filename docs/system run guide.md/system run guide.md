System Testing Guide (Web & Mobile)
Follow these steps to experience the full AI Medicinal Plant Detection system.

1. Start the Backend API (Required for both)
The backend is the engine that handles ML predictions and data.

Directory: d:\PROJECT STAGE 1\backend
Command:
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Verification: Open http://localhost:8000/docs in your browser.
2. Test on Web
The web dashboard provides the premium presentation experience.

Directory: d:\PROJECT STAGE 1\frontend
Command:
npm run dev
Action: Open http://localhost:3000 to see the new Milestones, Intelligence Dashboard, and Neural Scanner.
3. Test on Mobile (Physical Device)
To test on a real phone (essential for a final presentation), follow these network steps:

A. Sync your IP Address
Open PowerShell and run: ipconfig
Find your IPv4 Address (usually starts with 192.168.x.x).
Open 
mobile/config.js
 and update the DEV_API_URL_ANDROID or DEV_API_URL_IOS:
const DEV_API_URL_ANDROID = 'http://YOUR_IP_HERE:8000';
const DEV_API_URL_IOS = 'http://YOUR_IP_HERE:8000';
B. Launch Expo
Directory: d:\PROJECT STAGE 1\mobile
Command:
npx expo start
Action:
Install the Expo Go app on your phone (Android or iOS).
Scan the QR code displayed in your terminal.
Ensure your phone and PC are on the same Wi-Fi network.
Tips for a "Wow" Presentation:
Use Real Leaves: For the most impressive results, use the Mobile App to scan real medicinal leaves during the demo.
Show XAI on Web: Use the Web dashboard for the "Why AI chose this?" deep dive, as it provides high-definition heatmaps.
Highlight Logs: Point out the "Neural Logs" on the web during analysis to show technical sophistication.