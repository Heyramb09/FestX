const API_KEY = "YOUR_GEMINI_API_KEY";  // Replace with your actual Gemini API Key
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${API_KEY}`;

async function fetchQuiz(prompt) {
    try {
        const response = await fetch(GEMINI_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });

        const data = await response.json();
        const quizText = data.candidates[0].content.parts[0].text;
        return JSON.parse(quizText);
    } catch (error) {
        console.error("Error fetching quiz:", error);
        return [];
    }
}

function generateQuiz() {
    const prompt = "Generate a JSON quiz with 3 multiple-choice questions about JavaScript. Each question should have a question text, 4 options (A, B, C, D), and the correct answer.";
    
    fetchQuiz(prompt).then(quiz => {
        if (quiz.length === 0) {
            document.getElementById("quiz-container").innerHTML = "<p>Error generating quiz. Try again.</p>";
            return;
        }

        const quizContainer = document.getElementById("quiz-container");
        quizContainer.innerHTML = "";
        quiz.forEach((q, index) => {
            const questionHTML = `
                <div class="question">${index + 1}. ${q.question}</div>
                <div class="options">
                    <label><input type="radio" name="q${index}" value="A"> A) ${q.options.A}</label>
                    <label><input type="radio" name="q${index}" value="B"> B) ${q.options.B}</label>
                    <label><input type="radio" name="q${index}" value="C"> C) ${q.options.C}</label>
                    <label><input type="radio" name="q${index}" value="D"> D) ${q.options.D}</label>
                </div>
            `;
            quizContainer.innerHTML += questionHTML;
        });

        document.getElementById("submit-btn").style.display = "block";
        document.getElementById("result").innerText = "";
    });
}

function checkAnswers() {
    const quizContainer = document.getElementById("quiz-container").children;
    let score = 0;

    fetchQuiz("Provide correct answers for the last generated quiz in JSON format.").then(answers => {
        for (let i = 0; i < answers.length; i++) {
            const selected = document.querySelector(`input[name="q${i}"]:checked`);
            if (selected && selected.value === answers[i].correct) {
                score++;
            }
        }

        document.getElementById("result").innerText = `You scored ${score} / ${answers.length}`;
    });
}
