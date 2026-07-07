document.addEventListener("DOMContentLoaded", function () {

    console.log("========== JavaScript Loaded ==========");

    const modal = document.getElementById("formModal");
    const openBtn = document.getElementById("openForm");
    const closeBtn = document.querySelector(".close");
    const form = document.getElementById("predictionForm");
    const resultBox = document.getElementById("result");

    let modalOpen = false;

    // OPEN MODAL
    openBtn.onclick = function () {
        modal.style.display = "flex";
        modalOpen = true;

        // 👉 Add history state for back button support
        history.pushState({ modal: true }, null, "");
    };

    // CLOSE MODAL FUNCTION
    function closeModal() {
        modal.style.display = "none";
        modalOpen = false;
    }

    // CLOSE BUTTON
    closeBtn.onclick = function () {
        closeModal();
    };

    // CLOSE ON OUTSIDE CLICK
    window.onclick = function (e) {
        if (e.target === modal) {
            closeModal();
        }
    };

    // 👉 BACK BUTTON SUPPORT (browser back)
    window.addEventListener("popstate", function () {
        if (modalOpen) {
            closeModal();
        }
    });

    // FORM SUBMIT
    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        resultBox.innerHTML = "<h2>Predicting...</h2>";

        const formData = new FormData(form);

        try {

            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            console.log("Response:", data);
            console.log(data.results);

            if (data.error) {
                resultBox.innerHTML = "<h2 style='color:red'>" + data.error + "</h2>";
                return;
            }

            let html = `<h2>Results for ${data.name}</h2>`;
            html += "<table border='1' cellpadding='8'>";
            html += "<tr><th>College</th><th>Probability (%)</th><th>Website</th></tr>";

           data.results.forEach((college) => {

                let website = college.website || "";

                if (
                        website &&
                        !website.startsWith("http://") &&
                        !website.startsWith("https://")
                    ) {
                        website = "https://" + website;
                        }

                        html += `<tr>
                                    <td>${college.college}</td>
                                    <td>${Number(college.probability).toFixed(2)}%</td>
                                    <td>
                                        ${
                                            website
                                                ? `<a href="${website}" target="_blank">Visit Website</a>`
                                                : "Not Available"
                                        }
                                    </td>
                                </tr>`;
                    });

            html += "</table>";

            // 👉 BACK BUTTON ADDED HERE
            html += `
                <div style="margin-top:15px; text-align:center;">
                    <button id="backBtn" style="
                        padding: 8px 15px;
                        background: white;
                        color: black;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: bold;
                    ">⬅ Back</button>
                </div>
            `;

            resultBox.innerHTML = html;

            resultBox.classList.add("show");
            resultBox.classList.add("glass");

            modal.style.display = "none";
            modalOpen = false;

            resultBox.scrollIntoView({ behavior: "smooth" });

            // 👉 BACK BUTTON FUNCTIONALITY
            document.getElementById("backBtn").addEventListener("click", function () {

                // hide result
                resultBox.innerHTML = "";
                resultBox.classList.remove("show");
                resultBox.classList.remove("glass");

                // reopen form modal
                modal.style.display = "flex";
                modalOpen = true;

                history.pushState({ modal: true }, null, "");
            });

        } catch (err) {
            console.error(err);
            resultBox.innerHTML = "<h2 style='color:red'>Request Failed</h2>";
        }

    });

});