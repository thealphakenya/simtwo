import React, { useState } from 'react';

const WithdrawPage = () => {
  const [amount, setAmount] = useState('');

  const handleWithdraw = () => {
    // Call API to initiate withdrawal
    alert(`Withdrawing Ksh ${amount}`);
  };

  return (
    <div className="withdraw-page">
      <h2>Withdraw Earnings</h2>
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <button onClick={handleWithdraw}>Withdraw</button>
    </div>
  );
};

export default WithdrawPage;
