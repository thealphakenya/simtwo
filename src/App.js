import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import AdminPage from './components/AdminPage';
import WithdrawPage from './components/WithdrawPage';

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" exact component={LoginPage} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/admin" component={AdminPage} />
        <Route path="/withdraw" component={WithdrawPage} />
      </Switch>
    </Router>
  );
}

export default App;
