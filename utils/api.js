export const loginUser = async (phoneNumber, password) => {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ phoneNumber, password }),
  });
  return await response.json();
};

export const withdrawMoney = async (phoneNumber, amount) => {
  const response = await fetch('/api/withdraw', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ phoneNumber, amount }),
  });
  return await response.json();
};
