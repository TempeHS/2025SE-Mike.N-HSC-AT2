document
  .getElementById("api-key-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const resultDiv = document.getElementById("result");

    try {
      const response = await fetch("/get_api_key", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        resultDiv.innerHTML = `<p class="text-success">Your API Key: <code>${data.api_key}</code></p>`;
      } else {
        resultDiv.innerHTML = `<p class="text-danger">${data.error}</p>`;
      }
    } catch (error) {
      resultDiv.innerHTML = `<p class="text-danger">An error occurred: ${error.message}</p>`;
    }
  });
