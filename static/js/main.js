// AI Interview CRM - Main JavaScript File

// Global variables
let mediaRecorder;
let audioChunks = [];
let currentInterviewId = null;
let currentQuestion = null;
let questions = [];
let currentQuestionIndex = 0;
let isRecording = false;
let isLoggedIn = false;
let selectedLanguage = "en"; // Default language

// API base URL
const API_BASE = window.location.origin + "/api";

// Initialize the application
document.addEventListener("DOMContentLoaded", function () {
  checkAuthStatus();
  initializeEventListeners();
  initializeNavigation();
});

// Check if user is authenticated
function checkAuthStatus() {
  const token = localStorage.getItem("token");
  const userData = localStorage.getItem("userData");

  if (token && userData) {
    isLoggedIn = true;
    updateUIForLoggedInUser(JSON.parse(userData));
  } else {
    isLoggedIn = false;
    updateUIForLoggedOutUser();
  }
}

// Update UI for logged in user
function updateUIForLoggedInUser(userData) {
  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const dashboardLink = document.getElementById("dashboardLink");

  if (loginBtn) loginBtn.style.display = "none";
  if (logoutBtn) {
    logoutBtn.style.display = "inline-block";
    logoutBtn.textContent = `Logout (${userData.full_name || userData.email})`;
  }
  if (dashboardLink) dashboardLink.style.display = "inline-block";
}

// Update UI for logged out user
function updateUIForLoggedOutUser() {
  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const dashboardLink = document.getElementById("dashboardLink");

  if (loginBtn) loginBtn.style.display = "inline-block";
  if (logoutBtn) logoutBtn.style.display = "none";
  if (dashboardLink) dashboardLink.style.display = "none";
}

// Initialize event listeners
function initializeEventListeners() {
  // Navigation
  const hamburger = document.getElementById("hamburger");
  const navLinks = document.getElementById("navLinks");

  if (hamburger && navLinks) {
    hamburger.addEventListener("click", () => {
      navLinks.classList.toggle("active");
    });
  }

  // Hero buttons
  const startInterviewBtn = document.getElementById("startInterviewBtn");
  const getStartedBtn = document.getElementById("getStartedBtn");
  const learnMoreBtn = document.getElementById("learnMoreBtn");

  if (startInterviewBtn) {
    startInterviewBtn.addEventListener("click", handleStartInterview);
  }

  if (getStartedBtn) {
    getStartedBtn.addEventListener("click", handleGetStarted);
  }

  if (learnMoreBtn) {
    learnMoreBtn.addEventListener("click", () => {
      document.getElementById("features").scrollIntoView({ behavior: "smooth" });
    });
  }

  // Authentication
  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");

  if (loginBtn) {
    loginBtn.addEventListener("click", () => showModal("login"));
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", handleLogout);
  }

  // Modal events
  initializeModal();

  // Resume upload events
  initializeResumeUpload();

  // Audio recording events
  initializeAudioRecording();

  // Interview events
  initializeInterviewEvents();

  // Language selection
  initializeLanguageSelection();
}

// Initialize navigation
function initializeNavigation() {
  // Smooth scrolling for anchor links
  const links = document.querySelectorAll('a[href^="#"]');
  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });
}

// Handle start interview button
function handleStartInterview() {
  if (!isLoggedIn) {
    showModal("login");
    return;
  }
  window.location.href = "/interview";
}

// Handle get started button
function handleGetStarted() {
  if (!isLoggedIn) {
    showModal("register");
    return;
  }
  window.location.href = "/dashboard";
}

// Handle logout
async function handleLogout() {
  try {
    localStorage.removeItem("token");
    localStorage.removeItem("userData");
    isLoggedIn = false;
    updateUIForLoggedOutUser();

    // Redirect to home if on protected page
    if (window.location.pathname !== "/") {
      window.location.href = "/";
    }

    showNotification("Logged out successfully", "success");
  } catch (error) {
    console.error("Logout error:", error);
    showNotification("Logout failed", "error");
  }
}

// Modal functionality
function initializeModal() {
  const modal = document.getElementById("loginModal");
  const closeModal = document.getElementById("closeModal");
  const switchMode = document.getElementById("switchMode");
  const authForm = document.getElementById("authForm");

  if (!modal) return;

  // Close modal events
  if (closeModal) {
    closeModal.addEventListener("click", hideModal);
  }

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      hideModal();
    }
  });

  // Switch between login and register
  if (switchMode) {
    switchMode.addEventListener("click", (e) => {
      e.preventDefault();
      const modalTitle = document.getElementById("modalTitle");
      const authSubmit = document.getElementById("authSubmit");
      const switchText = document.getElementById("switchText");
      const nameGroup = document.getElementById("nameGroup");

      if (modalTitle.textContent === "Login") {
        // Switch to register
        modalTitle.textContent = "Sign Up";
        authSubmit.textContent = "Sign Up";
        switchText.innerHTML = 'Already have an account? <a href="#" id="switchMode">Login</a>';
        nameGroup.style.display = "block";
        nameGroup.querySelector("input").required = true;
      } else {
        // Switch to login
        modalTitle.textContent = "Login";
        authSubmit.textContent = "Login";
        switchText.innerHTML = 'Don\'t have an account? <a href="#" id="switchMode">Sign up</a>';
        nameGroup.style.display = "none";
        nameGroup.querySelector("input").required = false;
      }

      // Re-attach event listener to new switch link
      document.getElementById("switchMode").addEventListener("click", arguments.callee);
    });
  }

  // Form submission
  if (authForm) {
    authForm.addEventListener("submit", handleAuthSubmit);
  }
}

// Show modal
function showModal(mode = "login") {
  const modal = document.getElementById("loginModal");
  const modalTitle = document.getElementById("modalTitle");
  const authSubmit = document.getElementById("authSubmit");
  const switchText = document.getElementById("switchText");
  const nameGroup = document.getElementById("nameGroup");

  if (!modal) return;

  if (mode === "register") {
    modalTitle.textContent = "Sign Up";
    authSubmit.textContent = "Sign Up";
    switchText.innerHTML = 'Already have an account? <a href="#" id="switchMode">Login</a>';
    nameGroup.style.display = "block";
    nameGroup.querySelector("input").required = true;
  } else {
    modalTitle.textContent = "Login";
    authSubmit.textContent = "Login";
    switchText.innerHTML = 'Don\'t have an account? <a href="#" id="switchMode">Sign up</a>';
    nameGroup.style.display = "none";
    nameGroup.querySelector("input").required = false;
  }

  modal.style.display = "block";

  // Re-initialize switch mode event
  document.getElementById("switchMode")?.addEventListener("click", (e) => {
    e.preventDefault();
    const currentMode = modalTitle.textContent === "Login" ? "register" : "login";
    showModal(currentMode);
  });
}

// Hide modal
function hideModal() {
  const modal = document.getElementById("loginModal");
  if (modal) {
    modal.style.display = "none";
    // Clear form
    const form = document.getElementById("authForm");
    if (form) form.reset();
  }
}

// Handle authentication form submission
async function handleAuthSubmit(e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const email = formData.get("email");
  const password = formData.get("password");
  const fullName = formData.get("fullName");
  const isRegister = document.getElementById("modalTitle").textContent === "Sign Up";

  if (!email || !password) {
    showNotification("Please fill in all required fields", "error");
    return;
  }

  if (isRegister && !fullName) {
    showNotification("Please enter your full name", "error");
    return;
  }

  showLoading(true);

  try {
    const endpoint = isRegister ? "/auth/register" : "/auth/login";
    const body = isRegister ? { email, password, full_name: fullName } : { email, password };

    const response = await fetch(API_BASE + endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (response.ok) {
      if (isRegister) {
        showNotification("Registration successful! Please login.", "success");
        showModal("login");
      } else {
        // Store auth data
        localStorage.setItem("token", data.token);
        localStorage.setItem(
          "userData",
          JSON.stringify({
            user_id: data.user_id,
            full_name: data.full_name,
            email: email,
          })
        );

        isLoggedIn = true;
        updateUIForLoggedInUser({ full_name: data.full_name, email });
        hideModal();
        showNotification("Login successful!", "success");

        // Redirect to dashboard if on home page
        if (window.location.pathname === "/") {
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 1000);
        }
      }
    } else {
      showNotification(data.error || "Authentication failed", "error");
    }
  } catch (error) {
    console.error("Auth error:", error);
    showNotification("Network error. Please try again.", "error");
  } finally {
    showLoading(false);
  }
}

// Resume upload functionality
function initializeResumeUpload() {
  const fileOption = document.getElementById("fileOption");
  const textOption = document.getElementById("textOption");
  const fileInput = document.getElementById("resumeFile");
  const submitResumeBtn = document.getElementById("submitResume");

  // Upload option selection
  if (fileOption) {
    fileOption.addEventListener("click", () => {
      selectUploadOption("file");
    });
  }

  if (textOption) {
    textOption.addEventListener("click", () => {
      selectUploadOption("text");
    });
  }

  // File input change
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        document.getElementById("fileName").textContent = file.name;
        selectUploadOption("file");
      }
    });
  }

  // Submit resume
  if (submitResumeBtn) {
    submitResumeBtn.addEventListener("click", handleResumeSubmission);
  }
}

// Select upload option
function selectUploadOption(type) {
  const fileOption = document.getElementById("fileOption");
  const textOption = document.getElementById("textOption");
  const fileSection = document.getElementById("fileSection");
  const textSection = document.getElementById("textSection");

  // Remove active class from all
  fileOption?.classList.remove("active");
  textOption?.classList.remove("active");

  // Hide all sections
  if (fileSection) fileSection.style.display = "none";
  if (textSection) textSection.style.display = "none";

  // Show selected option
  if (type === "file") {
    fileOption?.classList.add("active");
    if (fileSection) fileSection.style.display = "block";
  } else {
    textOption?.classList.add("active");
    if (textSection) textSection.style.display = "block";
  }
}

// Handle resume submission
async function handleResumeSubmission() {
  const token = localStorage.getItem("token");
  if (!token) {
    showNotification("Please login first", "error");
    return;
  }

  const fileInput = document.getElementById("resumeFile");
  const textArea = document.getElementById("resumeText");

  const formData = new FormData();

  if (fileInput?.files[0]) {
    formData.append("file", fileInput.files[0]);
  } else if (textArea?.value.trim()) {
    // For text input, we need to send JSON
    const response = await submitResumeText(textArea.value.trim());
    return response;
  } else {
    showNotification("Please provide your resume", "error");
    return;
  }

  showLoading(true);

  try {
    const response = await fetch(API_BASE + "/interview/resume", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      showNotification("Resume processed successfully!", "success");
      // Start interview with this resume
      startInterviewWithResume(data.resume_id);
    } else {
      showNotification(data.error || "Resume processing failed", "error");
    }
  } catch (error) {
    console.error("Resume submission error:", error);
    showNotification("Network error. Please try again.", "error");
  } finally {
    showLoading(false);
  }
}

// Submit resume text
async function submitResumeText(text) {
  const token = localStorage.getItem("token");

  showLoading(true);

  try {
    const response = await fetch(API_BASE + "/interview/resume", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();

    if (response.ok) {
      showNotification("Resume processed successfully!", "success");
      startInterviewWithResume(data.resume_id);
    } else {
      showNotification(data.error || "Resume processing failed", "error");
    }
  } catch (error) {
    console.error("Resume text submission error:", error);
    showNotification("Network error. Please try again.", "error");
  } finally {
    showLoading(false);
  }
}

// Start interview with resume
async function startInterviewWithResume(resumeId) {
  const token = localStorage.getItem("token");

  showLoading(true);

  try {
    const response = await fetch(API_BASE + "/interview/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        resume_id: resumeId,
        language: selectedLanguage,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      currentInterviewId = data.interview_id;
      questions = data.questions;
      currentQuestionIndex = 0;

      // Hide upload section and show interview section
      hideUploadSection();
      showInterviewSection();
      displayQuestion();

      showNotification("Interview started successfully!", "success");
    } else {
      showNotification(data.error || "Failed to start interview", "error");
    }
  } catch (error) {
    console.error("Start interview error:", error);
    showNotification("Network error. Please try again.", "error");
  } finally {
    showLoading(false);
  }
}

// Hide upload section
function hideUploadSection() {
  const uploadSection = document.getElementById("uploadSection");
  if (uploadSection) {
    uploadSection.style.display = "none";
  }
}

// Show interview section
function showInterviewSection() {
  const interviewSection = document.getElementById("interviewSection");
  if (interviewSection) {
    interviewSection.style.display = "block";
  }
}

// Display current question
function displayQuestion() {
  if (currentQuestionIndex >= questions.length) {
    // Interview completed
    setTimeout(completeInterview, 7000);
    return;
  }

  currentQuestion = questions[currentQuestionIndex];
  const questionDisplay = document.getElementById("questionDisplay");
  const progressBar = document.getElementById("progressBar");
  const questionCounter = document.getElementById("questionCounter");

  if (questionDisplay) {
    questionDisplay.innerHTML = `
            <h3>Question ${currentQuestionIndex + 1}</h3>
            <p>${currentQuestion}</p>
        `;
  }

  if (progressBar) {
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    progressBar.style.width = `${progress}%`;
  }

  if (questionCounter) {
    questionCounter.textContent = `${currentQuestionIndex + 1} of ${questions.length}`;
  }

  // Clear previous answer
  clearAnswerInputs();
}

// Clear answer inputs
function clearAnswerInputs() {
  const textAnswer = document.getElementById("textAnswer");
  const audioStatus = document.getElementById("audioStatus");
  const audioFileName = document.getElementById("audioFileName");
  const audioFileInput = document.getElementById("audioFile");

  if (textAnswer) textAnswer.value = "";
  if (audioStatus) audioStatus.textContent = "Click record to start";
  if (audioFileName) audioFileName.textContent = "";
  if (audioFileInput) audioFileInput.value = "";

  // Reset recording state
  isRecording = false;
  audioChunks = [];
  window.currentAudioBlob = null;
  window.currentAudioFile = null;
  updateRecordButton();
}

// Initialize audio recording
function initializeAudioRecording() {
  const recordBtn = document.getElementById("recordBtn");
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");
  const audioFileInput = document.getElementById("audioFile");

  // Tab switching
  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const tabName = button.dataset.tab;
      switchTab(tabName);
    });
  });

  // Record button
  if (recordBtn) {
    recordBtn.addEventListener("click", toggleRecording);
  }

  // Audio file input
  if (audioFileInput) {
    audioFileInput.addEventListener("change", handleAudioFileUpload);
  }

  // Submit answer buttons
  const submitTextBtn = document.getElementById("submitTextAnswer");
  const submitAudioBtn = document.getElementById("submitAudioAnswer");

  if (submitTextBtn) {
    submitTextBtn.addEventListener("click", () => submitAnswer("text"));
  }

  if (submitAudioBtn) {
    submitAudioBtn.addEventListener("click", () => submitAnswer("audio"));
  }
}

// Handle audio file upload
function handleAudioFileUpload(e) {
  const file = e.target.files[0];
  if (file) {
    window.currentAudioFile = file;
    document.getElementById("audioFileName").textContent = file.name;
    // Clear recorded audio if a file is selected
    window.currentAudioBlob = null;
    const audioPreview = document.getElementById("audioPreview");
    if (audioPreview) {
      audioPreview.style.display = "none";
      audioPreview.src = "";
    }
  }
}

// Switch tab
function switchTab(tabName) {
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((btn) => btn.classList.remove("active"));
  tabContents.forEach((content) => content.classList.remove("active"));

  const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
  const activeContent = document.getElementById(`${tabName}Tab`);

  if (activeButton) activeButton.classList.add("active");
  if (activeContent) activeContent.classList.add("active");
}

// Toggle recording
async function toggleRecording() {
  if (!isRecording) {
    await startRecording();
  } else {
    stopRecording();
  }
}

// Start recording
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      // Store the blob for submission
      window.currentAudioBlob = audioBlob;

      const audioUrl = URL.createObjectURL(audioBlob);
      const audioPreview = document.getElementById("audioPreview");
      if (audioPreview) {
        audioPreview.src = audioUrl;
        audioPreview.style.display = "block";
      }
    };

    mediaRecorder.start();
    isRecording = true;
    updateRecordButton();

    // Update status
    const audioStatus = document.getElementById("audioStatus");
    if (audioStatus) {
      audioStatus.textContent = "Recording... Click to stop";
    }
  } catch (error) {
    console.error("Recording error:", error);
    showNotification("Could not access microphone", "error");
  }
}

// Stop recording
function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    updateRecordButton();

    // Stop all tracks
    mediaRecorder.stream.getTracks().forEach((track) => track.stop());

    // Update status
    const audioStatus = document.getElementById("audioStatus");
    if (audioStatus) {
      audioStatus.textContent = "Recording complete. You can play it back or submit.";
    }
  }
}

// Update record button
function updateRecordButton() {
  const recordBtn = document.getElementById("recordBtn");
  if (!recordBtn) return;

  if (isRecording) {
    recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
    recordBtn.classList.add("recording");
    recordBtn.title = "Stop recording";
  } else {
    recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    recordBtn.classList.remove("recording");
    recordBtn.title = "Start recording";
  }
}

// Submit answer
async function submitAnswer(type) {
  const token = localStorage.getItem("token");
  if (!token || !currentInterviewId || !currentQuestion) {
    showNotification("Invalid interview state", "error");
    return;
  }

  const formData = new FormData();
  formData.append("interview_id", currentInterviewId);
  formData.append("question", currentQuestion);

  if (type === "text") {
    const textAnswer = document.getElementById("textAnswer");
    if (!textAnswer?.value.trim()) {
      showNotification("Please enter your answer", "error");
      return;
    }
    formData.append("text_answer", textAnswer.value.trim());
  } else {
    if (window.currentAudioFile) {
      formData.append("audio", window.currentAudioFile, window.currentAudioFile.name);
    } else if (window.currentAudioBlob) {
      formData.append("audio", window.currentAudioBlob, "answer.wav");
    } else {
      showNotification("Please record or upload your answer first", "error");
      return;
    }
  }

  showLoading(true);

  try {
    const response = await fetch(API_BASE + "/interview/process", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      // Show evaluation
      displayEvaluation(data.evaluation);

      // Move to next question after a delay
      setTimeout(() => {
        currentQuestionIndex++;
        displayQuestion();
      }, 3000);
    } else {
      showNotification(data.error || "Failed to process answer", "error");
    }
  } catch (error) {
    console.error("Submit answer error:", error);
    showNotification("Network error. Please try again.", "error");
  } finally {
    showLoading(false);
  }
}

// Display evaluation
function displayEvaluation(evaluation) {
  const evaluationDisplay = document.getElementById("evaluationDisplay");
  if (!evaluationDisplay) return;

  const score = evaluation.score || 0;
  const strengths = evaluation.strengths || [];
  const improvements = evaluation.improvements || [];
  const suggestions = evaluation.suggestions || [];

  evaluationDisplay.innerHTML = `
        <div class="score-display">
            <div class="score-circle" style="--score: ${score}">
                <div class="score-text">${score}/100</div>
            </div>
            <h4>Your Score</h4>
        </div>

        ${
          strengths.length > 0
            ? `
        <div class="feedback-section">
            <h4><i class="fas fa-thumbs-up" style="color: #48bb78;"></i> Strengths</h4>
            <ul class="feedback-list">
                ${strengths.map((strength) => `<li>${strength}</li>`).join("")}
            </ul>
        </div>
        `
            : ""
        }

        ${
          improvements.length > 0
            ? `
        <div class="feedback-section">
            <h4><i class="fas fa-arrow-up" style="color: #ed8936;"></i> Areas for Improvement</h4>
            <ul class="feedback-list">
                ${improvements.map((improvement) => `<li>${improvement}</li>`).join("")}
            </ul>
        </div>
        `
            : ""
        }

        ${
          suggestions.length > 0
            ? `
        <div class="feedback-section">
            <h4><i class="fas fa-lightbulb" style="color: #667eea;"></i> Suggestions</h4>
            <ul class="feedback-list">
                ${suggestions.map((suggestion) => `<li>${suggestion}</li>`).join("")}
            </ul>
        </div>
        `
            : ""
        }
    `;

  evaluationDisplay.style.display = "block";

  // Hide after a few seconds
  // setTimeout(() => {
  //     evaluationDisplay.style.display = 'none';
  // }, 5000);
}

// Complete interview
async function completeInterview() {
  const token = localStorage.getItem("token");
  if (!token || !currentInterviewId) return;

  showLoading(true);

  try {
    const response = await fetch(API_BASE + `/interview/complete/${currentInterviewId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      showInterviewComplete(data);
    } else {
      showNotification(data.error || "Failed to complete interview", "error");
    }
  } catch (error) {
    console.error("Complete interview error:", error);
    showNotification("Network error. Please try again.", "error");
  } finally {
    showLoading(false);
  }
}

// Show interview complete
function showInterviewComplete(data) {
  const interviewSection = document.getElementById("interviewSection");
  if (!interviewSection) return;

  interviewSection.innerHTML = `
        <div class="interview-complete">
            <div class="completion-animation">
                <i class="fas fa-check-circle"></i>
            </div>
            <h2>Interview Complete!</h2>
            <p>Congratulations on completing your mock interview.</p>

            <div class="final-score">
                <div class="score-circle" style="--score: ${data.overall_score}">
                    <div class="score-text">${data.overall_score}/100</div>
                </div>
                <h3>Overall Score</h3>
            </div>

            <div class="completion-actions">
                <a href="/dashboard" class="btn btn-primary">View Dashboard</a>
                ${data.report_url ? `<a href="${data.report_url}" class="btn btn-secondary" download>Download Report</a>` : ""}
                <button class="btn btn-secondary" onclick="location.reload()">Start Another Interview</button>
            </div>
        </div>
    `;

  showNotification("Interview completed successfully!", "success");
}

// Initialize interview events
function initializeInterviewEvents() {
  // Dashboard specific events can be added here
  loadDashboardData();
}

// Load dashboard data
async function loadDashboardData() {
  if (window.location.pathname !== "/dashboard") return;

  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "/";
    return;
  }

  try {
    const response = await fetch(API_BASE + "/dashboard/stats", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      updateDashboard(data);
    } else {
      showNotification("Failed to load dashboard data", "error");
    }
  } catch (error) {
    console.error("Dashboard load error:", error);
    showNotification("Network error loading dashboard", "error");
  }
}

// Update dashboard
function updateDashboard(data) {
  // Update dashboard stats
  const elements = {
    totalInterviews: document.getElementById("totalInterviews"),
    completedInterviews: document.getElementById("completedInterviews"),
    averageScore: document.getElementById("averageScore"),
    improvementTrend: document.getElementById("improvementTrend"),
  };

  if (elements.totalInterviews) {
    elements.totalInterviews.textContent = data.total_interviews || 0;
  }

  if (elements.completedInterviews) {
    elements.completedInterviews.textContent = data.completed_interviews || 0;
  }

  if (elements.averageScore) {
    elements.averageScore.textContent = `${data.average_scores?.overall || 0}/100`;
  }

  if (elements.improvementTrend) {
    elements.improvementTrend.textContent = data.improvement_trend || "No data";
  }

  // Update recent interviews
  updateRecentInterviews(data.recent_interviews || []);
}

// Update recent interviews
function updateRecentInterviews(interviews) {
  const container = document.getElementById("recentInterviews");
  if (!container) return;

  if (interviews.length === 0) {
    container.innerHTML = '<p>No interviews yet. <a href="/interview">Start your first interview</a></p>';
    return;
  }

  container.innerHTML = interviews
    .map(
      (interview) => `
        <div class="interview-item">
            <div class="interview-date">${new Date(interview.date).toLocaleDateString()}</div>
            <div class="interview-score">${interview.score}/100</div>
            <div class="interview-status ${interview.completed ? "completed" : "incomplete"}">
                ${interview.completed ? "Completed" : "In Progress"}
            </div>
        </div>
    `
    )
    .join("");
}

// Utility functions

// Show loading spinner
function showLoading(show) {
  const spinner = document.getElementById("loadingSpinner");
  if (spinner) {
    spinner.style.display = show ? "flex" : "none";
  }
}

// Show notification
function showNotification(message, type = "info") {
  // Create notification element if it doesn't exist
  let notification = document.getElementById("notification");
  if (!notification) {
    notification = document.createElement("div");
    notification.id = "notification";
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: 600;
            z-index: 9999;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 300px;
        `;
    document.body.appendChild(notification);
  }

  // Set notification style based on type
  const colors = {
    success: "#48bb78",
    error: "#e53e3e",
    warning: "#ed8936",
    info: "#667eea",
  };

  notification.style.backgroundColor = colors[type] || colors.info;
  notification.textContent = message;

  // Show notification
  setTimeout(() => {
    notification.style.transform = "translateX(0)";
  }, 100);

  // Hide notification after 4 seconds
  setTimeout(() => {
    notification.style.transform = "translateX(400px)";
  }, 4000);
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

// Format duration
function formatDuration(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}

// Check if user is authenticated (utility)
function requireAuth() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "/";
    return false;
  }
  return true;
}

// Audio recording
document.getElementById("start-recording")?.addEventListener("click", async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      // Process this blob in submitAnswer()
    };

    mediaRecorder.start();
    audioChunks = [];

    document.getElementById("start-recording").disabled = true;
    document.getElementById("stop-recording").disabled = false;
  } catch (error) {
    console.error("Error accessing microphone:", error);
  }
});

document.getElementById("stop-recording")?.addEventListener("click", () => {
  mediaRecorder.stop();
  document.getElementById("start-recording").disabled = false;
  document.getElementById("stop-recording").disabled = true;
  document.getElementById("submit-answer").disabled = false;
});

// Submit answer
document.getElementById("submit-answer")?.addEventListener("click", async () => {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("interview_id", currentInterviewId);
  formData.append("question", currentQuestion);

  if (audioChunks.length > 0) {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    formData.append("audio", audioBlob, "answer.wav");
  } else {
    const textAnswer = document.getElementById("text-answer").value;
    if (!textAnswer) {
      alert("Please provide an answer");
      return;
    }
    formData.append("text_answer", textAnswer);
  }

  try {
    const response = await fetch("/api/interview/process", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();
    if (response.ok) {
      // Display feedback
      document.getElementById("feedback").innerHTML = `
                <h3>Feedback</h3>
                <p>Score: ${data.evaluation.score}/100</p>
                <p>${data.evaluation.feedback}</p>
            `;

      // Set next question
      if (data.next_question) {
        currentQuestion = data.next_question;
        document.getElementById("current-question").textContent = currentQuestion;
        document.getElementById("text-answer").value = "";
      } else {
        // Interview complete
        const completeResp = await fetch(`/api/interview/complete/${currentInterviewId}`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const completeData = await completeResp.json();
        if (completeResp.ok) {
          document.querySelector(".interview-section").style.display = "none";
          document.querySelector(".report-section").style.display = "block";
          document.getElementById("report-content").innerHTML = `
                        <h3>Overall Feedback</h3>
                        <p>${completeData.feedback}</p>
                        <h3>Recommendations</h3>
                        <p>${completeData.recommendations}</p>
                    `;
          document.getElementById("download-report").href = completeData.report_url;
        }
      }
    }
  } catch (error) {
    console.error("Error:", error);
  }
});

// Initialize language selection
function initializeLanguageSelection() {
  // Load user's preferred language
  loadUserLanguagePreference();

  // Add event listeners to language options
  const languageOptions = document.querySelectorAll(".language-option");
  languageOptions.forEach((option) => {
    option.addEventListener("click", function () {
      const langCode = this.getAttribute("data-lang");
      selectLanguage(langCode);
    });
  });
}

// Load user's language preference
async function loadUserLanguagePreference() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const response = await fetch(API_BASE + "/language/preference", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      selectedLanguage = data.language || "en";
      updateLanguageUI(selectedLanguage);
    }
  } catch (error) {
    console.error("Error loading language preference:", error);
  }
}

// Select a language
async function selectLanguage(langCode) {
  selectedLanguage = langCode;
  updateLanguageUI(langCode);

  // Save preference if user is logged in
  const token = localStorage.getItem("token");
  if (token) {
    try {
      await fetch(API_BASE + "/language/preference", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ language: langCode }),
      });
    } catch (error) {
      console.error("Error saving language preference:", error);
    }
  }
}

// Update language UI
function updateLanguageUI(langCode) {
  const languageOptions = document.querySelectorAll(".language-option");
  languageOptions.forEach((option) => {
    if (option.getAttribute("data-lang") === langCode) {
      option.classList.add("active");
    } else {
      option.classList.remove("active");
    }
  });
}
