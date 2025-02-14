// Function to send the URL to the Python backend
async function getSummary(url) {
  try {
    const response = await fetch('http://localhost:5000/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })  // Send the URL to the backend as JSON
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Received response:", data);  // Log the response for debugging
      return data;  // Return the response (summary, or any data from the backend)
    } else {
      console.error('Failed to get response from server');
      return null;
    }
  } catch (error) {
    console.error('Error in fetching data:', error);  // Log any fetch errors
    return null;
  }
}

// Get the current URL from the active tab and test the server connection
async function sendUrlToServer() {
  chrome.tabs.query({ active: true, currentWindow: true }, async function(tabs) {
    const currentUrl = tabs[0].url;  // Get the current URL
    console.log('Current URL:', currentUrl);  // Log the current URL for debugging

    // Send the URL to the backend (Flask server)
    const response = await getSummary(currentUrl);

    // Handle the response here (for testing, we can log it)
    if (response) {
      console.log("Server response:", response);  // Log the response from the backend
    } else {
      console.log("Failed to fetch data from server.");
    }
  });
}

// Trigger the function when the popup is opened
sendUrlToServer();
