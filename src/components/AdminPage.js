import React from 'react';
import { Link } from 'react-router-dom';

const AdminPage = () => {
  return (
    <div className="admin-page">
      <h2>Admin Page</h2>
      <nav>
        <ul>
          <li><Link to="#">Manage Rewards</Link></li>
          <li><Link to="#">View Transactions</Link></li>
          <li><Link to="#">Add Survey/Ads</Link></li>
        </ul>
      </nav>
    </div>
  );
};

export default AdminPage;
