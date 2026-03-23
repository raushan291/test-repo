// Ensure the DOM is fully loaded before trying to access elements
document.addEventListener('DOMContentLoaded', () => {
    // Get references to the increment button and counter display element
    const incrementButton = document.getElementById('increment-button');
    const counterDisplay = document.getElementById('counter-display');

    // Check if both elements exist on the page
    if (incrementButton && counterDisplay) {
        // Add a click event listener to the increment button
        incrementButton.addEventListener('click', async () => {
            try {
                // Send a POST request to the /increment endpoint
                const response = await fetch('/increment', {
                    method: 'POST', // Specify the HTTP method as POST
                    headers: {
                        'Content-Type': 'application/json' // Indicate that we're sending JSON (though body is empty for this POST)
                    }
                });

                // Check if the request was successful (status code 2xx)
                if (response.ok) {
                    const data = await response.json(); // Parse the JSON response
                    // Update the text content of the counter display with the new count
                    counterDisplay.textContent = data.count;
                } else {
                    // If the request failed, log the error and provide user feedback
                    const errorData = await response.json();
                    console.error('Failed to increment counter:', errorData.error || response.statusText);
                    alert('Error incrementing counter. Please try again.');
                }
            } catch (error) {
                // Catch any network errors or other exceptions during the fetch operation
                console.error('Network error or other issue:', error);
                alert('An unexpected error occurred. Please check your connection.');
            }
        });
    } else {
        // Log an error if required HTML elements are not found, which might indicate a problem with the HTML structure
        console.error('Required HTML elements (increment-button or counter-display) not found.');
    }
});