let violations = parseInt(localStorage.getItem("violations")) || 0;
let lastViolation = 0;

function updateViolationDisplay() {
    const counter = document.getElementById("violation-count");
    if (counter) {
        counter.textContent = violations;
    }
}

function showWarning(reason) {
    const banner = document.getElementById("lockdown-warning");
    if (!banner) return;

    banner.classList.remove("d-none");
    banner.innerHTML = `
        <strong>LockIn Security Tracking Notification</strong><br>
        ${reason}<br>
        Current Total Infractions: ${violations}
    `;

    setTimeout(() => {
        banner.classList.add("d-none");
    }, 5000);
}

async function sendInfractionToServer(reason) {
    const courseId = document.querySelector('input[name="course_id"]')?.value || 1;
    const submissionId = document.querySelector('input[name="submission_id"]')?.value || null;

    try {
        await fetch("/lockdown/log-incident", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                reason: reason,
                course_id: parseInt(courseId),
                submission_id: submissionId ? parseInt(submissionId) : null
            })
        });
        console.log(`📡 Telemetry reported: ${reason}`);
    } catch (err) {
        console.error("Telemetry server sync offline:", err);
    }
}

function addViolation(reason) {
    const now = Date.now();

    if (now - lastViolation < 2000) {
        return;
    }

    lastViolation = now;
    violations++;
    localStorage.setItem("violations", violations);

    updateViolationDisplay();
    showWarning(reason);
    
    sendInfractionToServer(reason);

    if (window.lockdownMode === "hard" && violations >= 3) {
        const banner = document.getElementById("lockdown-warning");
        if (banner) {
            banner.classList.remove("d-none");
            banner.innerHTML = `
                <strong>Assessment Terminated</strong><br>
                Maximum violation volume exceeded. Auto-submitting workspace...
            `;
        }

        const examForm = document.getElementById("exam-form");
        if (examForm) {
            setTimeout(() => {
                examForm.submit();
                localStorage.removeItem("violations"); // Reset on completion
            }, 1500);
        }
    }
}

async function activateFullscreen() {
    try {
        if (document.documentElement.requestFullscreen && !document.fullscreenElement) {
            await document.documentElement.requestFullscreen();
        }
    } catch (err) {
        console.error("Fullscreen policy rejected:", err);
    }
}

function startSoftLockdown() {
    window.lockdownMode = "soft";
    activateFullscreen();
    console.log("Soft Lockdown Active");
}

function startHardLockdown() {
    window.lockdownMode = "hard";
    activateFullscreen();
    console.log("Hard Lockdown Active");
}

document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        addViolation("Tab switch or minimization tracking event");
    }
});

window.addEventListener("blur", () => {
    setTimeout(() => {
        if (!document.hidden) {
            addViolation("Application boundary focus dropped");
        }
    }, 150);
});

document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement) {
        addViolation("Exited secure fullscreen viewing bounds");
    }
});

// Clipboard Block Handlers
document.addEventListener("contextmenu", e => {
    e.preventDefault();
    addViolation("Context right-click action blocked");
});

document.addEventListener("copy", e => {
    e.preventDefault();
    addViolation("Copy shortcut execution blocked");
});

document.addEventListener("cut", e => {
    e.preventDefault();
    addViolation("Cut shortcut execution blocked");
});

document.addEventListener("paste", e => {
    e.preventDefault();
    addViolation("Paste shortcut execution blocked");
});

document.addEventListener("DOMContentLoaded", () => {
    updateViolationDisplay();
    
    if (window.lockdownMode === "preview") {
        console.log("🔒 LockIn Dashboard: Standing by in Preview Mode. Listeners paused.");
        return; 
    }
    
    if (!window.lockdownMode) {
        window.lockdownMode = "soft";
    }
});
