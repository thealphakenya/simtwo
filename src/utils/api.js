export const apiRequest = async (url, method = 'GET', body = null) => {
  try {
    const headers = {
      'Content-Type': 'application/json',
    };

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    if (!response.ok) throw new Error('Network response was not ok');
    return await response.json();
  } catch (error) {
    console.error('API request error: ', error);
    return { error: error.message };
  }
};
