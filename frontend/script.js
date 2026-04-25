async function sendMessage() {

    let input = document.getElementById("input");
    let msg = input.value.trim();

    if (!msg) return;

    let chat = document.getElementById("chat-box");

    // USER MESSAGE
    chat.innerHTML += `<div class="message user">${msg}</div>`;
    input.value = "";

    // LOADING
    let loadingDiv = document.createElement("div");
    loadingDiv.className = "message bot";
    loadingDiv.innerText = "Thinking...";
    chat.appendChild(loadingDiv);

    chat.scrollTop = chat.scrollHeight;

    try {
        let res = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ query: msg })
        });

        let data = await res.json();

        // remove loading
        chat.removeChild(loadingDiv);

        let formatted;

        if (data.answer.toLowerCase().includes("out of domain")) {
            formatted = `<div class="card"><p>${data.answer}</p></div>`;
        } else {
            formatted = format(data.answer, msg);
        }

        chat.innerHTML += `<div class="message bot">${formatted}</div>`;
        chat.scrollTop = chat.scrollHeight;

    } catch (error) {
        chat.removeChild(loadingDiv);
        chat.innerHTML += `<div class="message bot">Error: Server not responding</div>`;
    }
}


// -----------------------------
// FORMAT FUNCTION (FIXED)
// -----------------------------
function format(text, userQuery) {

    function section(name) {
        let regex = new RegExp(name + ":(.*?)(?=\\n[A-Z]|$)", "s");
        let m = text.match(regex);
        return m ? m[1].trim() : "";
    }

    let name = section("Recipe Name");
    let ing = section("Ingredients");
    let steps = section("Steps");
    let miss = section("Missing Ingredients");

    // -----------------------------
    // INGREDIENT LIST
    // -----------------------------
    let ingList = ing.split("\n")
        .filter(i => i.trim())
        .map(i => `<li>${i.replace("-", "").trim()}</li>`)
        .join("");

    // -----------------------------
    // STEP LIST
    // -----------------------------
    let stepList = steps.split("\n")
        .filter(s => s.trim())
        .map(s => `<li>${s.replace(/^\d+\./, "").trim()}</li>`)
        .join("");

    // -----------------------------
    // CHECK IF DISH QUERY
    // -----------------------------
    let isDishQuery =
        userQuery.toLowerCase().includes("how to") ||
        userQuery.toLowerCase().includes("recipe") ||
        userQuery.toLowerCase().includes("procedure") ||
        userQuery.toLowerCase().includes("prepare");

    // -----------------------------
    // MISSING INGREDIENTS
    // -----------------------------
    let missList = "";

    if (!isDishQuery && miss && miss.trim() !== "" && miss !== "None") {
        missList = `
            <h4>Missing Ingredients</h4>
            <ul>
                ${miss.split(",").map(m => `<li>${m.trim()}</li>`).join("")}
            </ul>
        `;
    }

    // -----------------------------
    // FINAL HTML
    // -----------------------------
    return `
        <div class="card">
            <h3>${name}</h3>

            <h4>Ingredients</h4>
            <ul>${ingList}</ul>

            <h4>Steps</h4>
            <ol>${stepList}</ol>

            ${missList}
        </div>
    `;
}