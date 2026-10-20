async function sendTimeZone() {
    const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const token = document.querySelector('meta[name="csrf-token"]').content;

    try {
        const response = await fetch('/set-timezone', {
            method: 'POST',
            headers: {
                'X-CSRFToken': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userTimeZone)
        });
        
        if (!response.ok) {
            console.error("Failed to save timezone");
        }
    } catch (error) {
        console.error(error);
    }
}
sendTimeZone();