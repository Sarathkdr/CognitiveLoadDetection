
const typingArea = document.getElementById("typingArea");
const startBtn = document.getElementById("startBtn");
const finishBtn = document.getElementById("finishBtn");
const saveBtn = document.getElementById("saveBtn");
const downloadBtn = document.getElementById("downloadBtn");
const cognitiveLoad = document.getElementById("cognitiveLoad");

let startTime = 0;
let lastKeyTime = 0;

let keyIntervals = [];
let pauses = [];
let backspaceCount = 0;
let totalCharacters = 0;

let active = false;
let currentSession = null;

// Keep collected sessions even after refreshing the page
let dataset = JSON.parse(
    localStorage.getItem("typingDataset") || "[]"
);

// Start typing test
startBtn.addEventListener("click", function () {

    startTime = Date.now();
    lastKeyTime = 0;

    keyIntervals = [];
    pauses = [];
    backspaceCount = 0;
    totalCharacters = 0;
    currentSession = null;

    typingArea.value = "";
    typingArea.disabled = false;

    cognitiveLoad.value = "";
    saveBtn.disabled = true;

    active = true;

    startBtn.disabled = true;
    finishBtn.disabled = false;

    typingArea.focus();

    document.getElementById("status").innerText =
        "Typing test in progress...";

});

// Collect typing behavior
typingArea.addEventListener("keydown", function (event) {

    if (!active || event.ctrlKey || event.altKey || event.metaKey) {
        return;
    }

    const currentTime = Date.now();

    if (event.key.length === 1) {
        totalCharacters++;
    }

    if (event.key === "Backspace") {
        backspaceCount++;
    }

    if (
        event.key.length === 1 ||
        event.key === "Backspace" ||
        event.key === "Delete"
    ) {

        if (lastKeyTime !== 0) {

            const difference = currentTime - lastKeyTime;

            keyIntervals.push(difference);

            if (difference > 1500) {
                pauses.push(difference);
            }
        }

        lastKeyTime = currentTime;
    }

});

// Finish test
finishBtn.addEventListener("click", function () {

    if (!active) return;

    active = false;

    const endTime = Date.now();

    const durationSeconds =
        (endTime - startTime) / 1000;

    const minutes = durationSeconds / 60;

    const words = typingArea.value.trim()
        ? typingArea.value.trim().split(/\s+/).length
        : 0;

    const wpm = minutes > 0
        ? words / minutes
        : 0;

    const averagePause = pauses.length > 0
        ? pauses.reduce((a, b) => a + b, 0)
            / pauses.length / 1000
        : 0;

    const averageInterval = keyIntervals.length > 0
        ? keyIntervals.reduce((a, b) => a + b, 0)
            / keyIntervals.length / 1000
        : 0;

    document.getElementById("speed").innerText =
        Math.round(wpm);

    document.getElementById("pause").innerText =
        averagePause.toFixed(2);

    document.getElementById("errors").innerText =
        backspaceCount;

    document.getElementById("interval").innerText =
        averageInterval.toFixed(2);

    typingArea.disabled = true;

    startBtn.disabled = false;
    finishBtn.disabled = true;

    currentSession = {
        typing_speed: Number(wpm.toFixed(2)),
        average_pause: Number(averagePause.toFixed(3)),
        backspace_count: backspaceCount,
        average_key_interval: Number(averageInterval.toFixed(3)),
        duration_seconds: Number(durationSeconds.toFixed(2)),
        total_characters: totalCharacters
    };

    saveBtn.disabled = false;

    document.getElementById("status").innerText =
        "Test completed! Select your perceived workload and save.";
});

// Save session
saveBtn.addEventListener("click", function () {

    if (!currentSession) return;

    const load = cognitiveLoad.value;

    if (!load) {
        alert("Please select your perceived workload.");
        return;
    }

    const record = {
        ...currentSession,
        cognitive_load: load
    };

    dataset.push(record);

    localStorage.setItem(
        "typingDataset",
        JSON.stringify(dataset)
    );

    document.getElementById("status").innerText =
        "Session saved! Total records: " + dataset.length;

    currentSession = null;
    saveBtn.disabled = true;
    cognitiveLoad.value = "";
});

// Download CSV
downloadBtn.addEventListener("click", function () {

    if (dataset.length === 0) {
        alert("No data available. Complete and save a typing test first.");
        return;
    }

    const headers = [
        "typing_speed",
        "average_pause",
        "backspace_count",
        "average_key_interval",
        "duration_seconds",
        "total_characters",
        "cognitive_load"
    ];

    const rows = dataset.map(record =>
        headers.map(header => record[header]).join(",")
    );

    const csvContent = [
        headers.join(","),
        ...rows
    ].join("\n");

    const blob = new Blob(
        [csvContent],
        { type: "text/csv;charset=utf-8;" }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "typing_data.csv";

    link.click();

    URL.revokeObjectURL(url);
});
