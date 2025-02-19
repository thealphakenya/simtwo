import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <h2>Welcome to your Dashboard</h2>
      <nav>
        <ul>
          <li><Link to="/withdraw">Withdraw Earnings</Link></li>
          <li><Link to="/admin">Admin Page</Link></li>
        </ul>
      </nav>
    </div>
  );
};

export default Dashboard;
