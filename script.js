document.getElementById("inputText").addEventListener("input", function () {
    const n = this.value.length;
    document.getElementById("charCount").textContent =
        n === 1 ? "1 character" : n.toLocaleString() + " characters";
});

async function checkPlagiarism() {
    const text = document.getElementById("inputText").value.trim();
    const resultArea = document.getElementById("result");

    if (!text) {
        document.getElementById("inputText").focus();
        return;
    }

    resultArea.innerHTML = `<div class="idle-state">Scanning for matches…</div>`;

    try {
        const response = await fetch("/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error("Server error " + response.status);

        const data = await response.json();
        const results = data.results || [];

        if (results.length === 0) {
            resultArea.innerHTML = `<div class="idle-state">No matches found.</div>`;
            return;
        }

        let html = `
            <div class="top-result-box">
                <h2>Top Matching Result</h2>
                <p><b>Most Similar File:</b> ${data.top_file}</p>
                <p><b>Similarity:</b> ${data.top_similarity}%</p>
                <p><b>Status:</b> ${data.status}</p>
            </div>
            <hr>
        `;

        results.forEach((item, i) => {
            const sim = parseFloat(item.similarity) || 0;
            const level = sim < 30 ? "low" : sim < 60 ? "med" : "high";
            const pct = Math.min(sim, 100).toFixed(1);

            const matchesHTML = item.matched_sentences?.length
                ? `<div class="matched-section">
                       <div class="matched-title">Matched Sentences:</div>
                       ${item.matched_sentences.map(s => `<div class="matched-text">${s}</div>`).join("")}
                   </div>`
                : "";

            html += `
                <div class="result-card">
                    <div class="result-card-top">
                        <span class="result-card-name">${item.document}</span>
                        <span class="result-badge badge-${level}">${pct}% similarity</span>
                    </div>

                    <div class="result-bar">
                        <div class="result-bar-fill fill-${level}" id="bar-${i}" style="width:0%"></div>
                    </div>

                    <div class="result-card-body">
                        <div class="result-stat">
                            <div class="result-stat-label">KMP match</div>
                            <div class="result-stat-val">${item.kmp_match}</div>
                        </div>
                        <div class="result-stat">
                            <div class="result-stat-label">Rabin-Karp match</div>
                            <div class="result-stat-val">${item.rabin_karp_match}</div>
                        </div>
                    </div>

                    ${matchesHTML}
                </div>
            `;
        });

        resultArea.innerHTML = html;

        results.forEach((item, i) => {
            const sim = Math.min(parseFloat(item.similarity) || 0, 100);
            setTimeout(() => {
                const bar = document.getElementById("bar-" + i);
                if (bar) bar.style.width = sim + "%";
            }, 80 + i * 60);
        });

    } catch (error) {
        console.error("Error:", error);
        resultArea.innerHTML = `<div class="error-box">Something went wrong: ${error.message}</div>`;
    }
}