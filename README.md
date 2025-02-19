My Reward App - Frontend
Overview

This project is the frontend for the My Reward App, a React-based application that allows users to log in, view their dashboard, withdraw earnings, and access an admin page for managing the platform. The app also includes Progressive Web App (PWA) support for offline functionality and app-like behavior.
Features

    Login Page: Users can log in using their phone number and password.
    Dashboard: After logging in, users are redirected to their personal dashboard where they can manage their account and earnings.
    Admin Page: Admin users can manage rewards, view transactions, and add surveys/ads.
    Withdraw Earnings: Users can withdraw earnings to their linked phone number.
    PWA Support: The app is installable and supports offline caching using a service worker.

Directory Structure

/frontend
├── /public
│   ├── index.html
│   ├── manifest.json
│   └── service-worker.js
├── /src
│   ├── App.js
│   ├── index.js
│   ├── /components
│   │   ├── LoginPage.js
│   │   ├── Dashboard.js
│   │   ├── AdminPage.js
│   │   └── WithdrawPage.js
│   ├── /assets
│   │   └── logo.png
│   ├── /utils
│   │   └── api.js
│   └── /styles
│       └── main.css
├── package.json
└── .gitignore

Prerequisites

Before you start, make sure you have:

    Node.js (v14 or later)
    npm (Node Package Manager)

Setup Instructions

    Clone the repository to your local machine:

git clone https://github.com/yourusername/my-reward-app.git
cd my-reward-app/frontend

Install dependencies:

npm install

Run the application:

To start the app in development mode, run:

    npm start

    The app will open at http://localhost:3000.

Build for Production

To build the app for production, run the following command:

npm run build

This will generate an optimized production build in the build folder.
File Descriptions

    /public/index.html: Main HTML file that contains the root div where the React app is mounted.
    /public/manifest.json: Manifest file for PWA configuration.
    /public/service-worker.js: Service worker for offline support and caching.
    /src/index.js: The entry point for the React application.
    /src/App.js: Main React component that handles routing between pages.
    /src/components/LoginPage.js: Component for the login page where users enter their phone number and password.
    /src/components/Dashboard.js: The user dashboard page after a successful login.
    /src/components/AdminPage.js: Admin page for managing rewards, transactions, and ads.
    /src/components/WithdrawPage.js: Page where users can withdraw their earnings.
    /src/utils/api.js: Utility functions for making API calls to the backend.
    /src/styles/main.css: The main CSS file for styling the application.

Usage

    Login Page: Users can log in using their phone number and password. Upon successful login, they will be redirected to the dashboard.

    Dashboard: After logging in, users can:
        Withdraw Earnings: Navigate to the withdrawal page.
        Access Admin Page: If the user is an admin, they can manage rewards and transactions.

    Withdraw Earnings: On the withdraw page, users can specify the amount they want to withdraw. A confirmation will be shown after submitting the request.

Technologies Used

    React: Frontend framework for building the user interface.
    React Router: For handling routing between different pages.
    CSS: For styling the app.
    Service Worker: For enabling offline functionality in PWA.

Deployment

For deployment, you can create a production build using npm run build and then deploy it to platforms like:

    Netlify
    Vercel
    GitHub Pages

License

This project is licensed under the MIT License - see the LICENSE file for details.
