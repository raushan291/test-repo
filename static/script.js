// JavaScript for the counter application
document.addEventListener('DOMContentLoaded', () => {
    const counterDisplay = document.getElementById('counter-display');
    const incrementButton = document.getElementById('increment-button');

    let count = 0;

    if (counterDisplay) {
        // Initialize display content if it's empty or not '0'
        if (counterDisplay.textContent === '' || isNaN(parseInt(counterDisplay.textContent))) {
            counterDisplay.textContent = '0';
        } else {
            count = parseInt(counterDisplay.textContent);
        }
    }

    if (incrementButton) {
        incrementButton.addEventListener('click', () => {
            count++;
            if (counterDisplay) {
                counterDisplay.textContent = count;
            }
        });
    } else {
        console.error("Increment button not found. Make sure an element with id 'increment-button' exists.");
    }
});