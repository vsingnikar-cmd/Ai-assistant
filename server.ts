/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { createServer as createViteServer } from 'vite';
import { GoogleGenAI } from '@google/genai';
import { spawn } from 'child_process';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = parseInt(process.env.PORT || '3000', 10);

app.use(express.json({ limit: '10mb' }));

const getGeminiClient = () => {
  const apiKey = process.env.GEMINI_API_KEY || '';
  if (!apiKey) {
    throw new Error('GEMINI_API_KEY is not configured in .env or environment.');
  }
  return new GoogleGenAI({ apiKey });
};

const getModelName = () => {
  return process.env.GEMINI_MODEL || 'gemini-3.5-flash-lite';
};

// --------------------------------------------------------------------
// 1. AI ACADEMIC CHAT ROUTE
// --------------------------------------------------------------------
app.post('/api/chat', async (req: Request, res: Response) => {
  try {
    const { query, style = 'detailed', profile = {}, history = [] } = req.body;

    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Query is required.' });
    }

    const ai = getGeminiClient();
    const model = getModelName();

    const course = profile.course || 'Undergraduate Computer Science';
    const branch = profile.branch || 'Engineering';
    const semester = profile.semester || 'Current Semester';

    const styleInstructions: Record<string, string> = {
      '2_marks': `Format strictly as a clean 2-Mark Exam Answer:
### 1. Formal Definition
(1-2 clear sentences defining the term with bold key words)

### 2. Key Characteristic or Formula
(1-2 bullet points with exact formula or property)

### 3. Quick Example
(1 line example)`,

      '5_marks': `Format as a clean, highly structured 5-Mark Exam Answer:
### 1. Definition & Core Purpose
(2 concise sentences with bold terminology)

### 2. Key Working Principles
* **Concept 1:** Clear explanation.
* **Concept 2:** Clear explanation.
* **Concept 3:** Clear explanation.

### 3. Working Example or Code
(Short 4-6 line well-commented code block or concise formula)

### 4. Advantages & Use Cases
* Bullet points for key advantages.

> 💡 **Exam Tip:** 1 sentence key point students must write to get full marks.`,

      '10_marks': `Format as an organized, high-scoring 10-Mark University Exam Answer:
### 1. Introduction & Formal Definition
(Clear, comprehensive opening paragraph with technical terms in bold)

### 2. Working Mechanism & Architecture
Step-by-step numbered breakdown:
1. **Phase 1:** Detailed explanation.
2. **Phase 2:** Detailed explanation.
3. **Phase 3:** Detailed explanation.

### 3. Practical Implementation / Code Snippet
(Clean, readable code block or mathematical derivation)

### 4. Structured Comparison Table
| Feature | Type A / Approach 1 | Type B / Approach 2 |
| :--- | :--- | :--- |
(At least 3-4 clear comparison rows)

### 5. Advantages & Trade-offs
* **Advantage:** Bullet point.
* **Limitation:** Bullet point.

> 💡 **University Exam Key Takeaway:** 1-2 sentences on common examiner criteria.`,

      'comparison': `Format as a clean comparison analysis:
### Overview
Brief 1-sentence intro to the two concepts.

### Detailed Comparison Table
| Criteria | Concept A | Concept B |
| :--- | :--- | :--- |
| **Definition** | ... | ... |
| **Working Principle** | ... | ... |
| **Time/Space Complexity** | ... | ... |
| **Resource Overhead** | ... | ... |
| **Best Used For** | ... | ... |

### 🎯 When to Choose Which
* **Choose Concept A when:** ...
* **Choose Concept B when:** ...`,

      'simple': `Format as an intuitive, beginner-friendly explanation:
### 🎯 In Simple Terms
(1-2 sentences explaining what it is without confusing jargon)

### 🌟 Real-World Analogy
(A relatable everyday story or metaphor that makes the concept instantly click)

### 📌 3 Key Things to Remember
* **First:** ...
* **Second:** ...
* **Third:** ...

### 💻 Simple Example
(A clean, basic example showing it in action)`
    };

    const selectedStyle = styleInstructions[style] || styleInstructions['5_marks'];

    const systemInstruction = `You are the AI Student Assistant Agent, an expert university academic mentor.
Student Profile:
- Degree: ${course}
- Branch: ${branch}
- Semester: ${semester}

VISUAL & PEDAGOGICAL PRESENTATION RULES:
1. Make every answer clear, clean, scannable, and visually pleasant.
2. NEVER output messy, sprawling ASCII drawings or dense walls of unstructured text.
3. Use markdown headers (###), bold lead phrases (* **Concept:** explanation), and clean tables.
4. Adhere strictly to the requested format template:
${selectedStyle}
5. Keep explanations direct, pedagogically sound, and easy to memorize for exams.`;

    // Build context with recent conversation turns
    let conversationContext = '';
    if (Array.isArray(history) && history.length > 0) {
      const recent = history.slice(-5);
      conversationContext = 'Recent Conversation History:\n' + recent.map(
        (m: { role: string; content: string }) => `${m.role === 'user' ? 'Student' : 'Assistant'}: ${m.content}`
      ).join('\n') + '\n\n';
    }

    const prompt = `${conversationContext}Student Question: ${query}`;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        systemInstruction,
        temperature: 0.7
      }
    });

    const reply = response.text || 'No response generated.';
    return res.json({ reply });
  } catch (error: any) {
    console.error('[API /api/chat error]:', error);
    return res.status(500).json({
      error: error?.message || 'Failed to generate AI response. Please check API credentials.'
    });
  }
});

// --------------------------------------------------------------------
// 2. PDF GROUNDED Q&A ROUTE
// --------------------------------------------------------------------
app.post('/api/pdf-qa', async (req: Request, res: Response) => {
  try {
    const { query, documentName = 'Uploaded PDF', documentContext = '' } = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query is required.' });
    }

    const ai = getGeminiClient();
    const model = getModelName();

    const systemInstruction = `You are an AI Document Study Assistant.
You must answer the student's question thoroughly using ONLY the facts and concepts found in the provided document excerpts.
Always cite the source page using format "[Page X]" whenever referencing facts from the excerpt.

CRITICAL MULTI-CONCEPT REQUIREMENT:
If the student asks about multiple concepts, acronyms, or topics (such as "What is AR, VR, MR?", "Compare TCP and UDP", or lists of terms):
- You MUST explicitly address EVERY SINGLE requested concept (e.g. provide definition and details for AR, for VR, and for MR).
- Check the entire document excerpts for each term.
- If multiple terms are present in the excerpts, provide clear, individual explanations with citations for each term.
- If a specific term from the question is truly absent from the excerpts, explicitly state: "[Term] is not mentioned in the provided excerpts", while still giving the complete answers for all other terms that ARE present in the document.
- Never stop after answering only the first term.
- Organize the output with clean headings or bullet points for each requested term so it is crystal clear for students.`;

    const prompt = `Document Name: ${documentName}

[DOCUMENT EXCERPTS START]
${documentContext || 'The document contains lecture notes.'}
[DOCUMENT EXCERPTS END]

Student Question: ${query}`;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        systemInstruction,
        temperature: 0.3
      }
    });

    return res.json({ reply: response.text || '' });
  } catch (error: any) {
    console.error('[API /api/pdf-qa error]:', error);
    return res.status(500).json({ error: error?.message || 'PDF Q&A failed.' });
  }
});

// --------------------------------------------------------------------
// 2.5 PDF & DOCUMENT UPLOAD ROUTE (PyMuPDF Extraction Bridge)
// --------------------------------------------------------------------
app.post('/api/upload-pdf', async (req: Request, res: Response) => {
  try {
    const { base64, filename = 'document.pdf', textContent } = req.body;

    // Direct text / markdown content
    if (textContent && typeof textContent === 'string') {
      const lines = textContent.split('\n');
      const chunkSize = 800;
      const chunks: Array<{ id: number; page_number: number; content: string }> = [];
      let current = '';
      let page = 1;
      let id = 1;

      for (const line of lines) {
        if (current.length + line.length > chunkSize) {
          chunks.push({ id: id++, page_number: page, content: current.trim() });
          current = line + '\n';
          if (id % 3 === 0) page++;
        } else {
          current += line + '\n';
        }
      }
      if (current.trim()) {
        chunks.push({ id: id++, page_number: page, content: current.trim() });
      }

      return res.json({
        success: true,
        filename,
        total_pages: page,
        chunks
      });
    }

    if (!base64) {
      return res.status(400).json({ success: false, message: 'No file data received.' });
    }

    // Call python PyMuPDF extraction bridge
    const child = spawn('python3', ['services/cli_pdf_extract.py']);
    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (d) => { stdout += d.toString(); });
    child.stderr.on('data', (d) => { stderr += d.toString(); });

    child.on('close', (code) => {
      try {
        const parsed = JSON.parse(stdout.trim());
        return res.json(parsed);
      } catch (err) {
        return res.status(500).json({
          success: false,
          message: `PDF extraction failed: ${stderr || 'Could not parse document text.'}`
        });
      }
    });

    child.stdin.write(JSON.stringify({ base64, filename }));
    child.stdin.end();
  } catch (error: any) {
    console.error('[API /api/upload-pdf error]:', error);
    return res.status(500).json({ success: false, message: error?.message || 'Upload failed.' });
  }
});

// --------------------------------------------------------------------
// 3. EXAM NOTES GENERATOR ROUTE
// --------------------------------------------------------------------
app.post('/api/notes', async (req: Request, res: Response) => {
  try {
    const { subject, unit, topic, format = 'Comprehensive Exam Guide' } = req.body;

    if (!topic || !subject) {
      return res.status(400).json({ error: 'Subject and Topic are required.' });
    }

    const ai = getGeminiClient();
    const model = getModelName();

    const prompt = `Generate an exam-oriented study guide and revision notes for university students.
Subject: ${subject}
Unit: ${unit || 'General'}
Topic: ${topic}
Format: ${format}

CRITICAL FORMATTING INSTRUCTIONS FOR SYMBOLS & ARROWS:
- For functional dependencies, transitions, and mappings, ALWAYS use the clean unicode arrow character '→' (e.g. X → Y, A → B, X → YZ).
- NEVER output LaTeX '\\rightarrow', '\\to', or '\\ightarrow'. Write simple clean arrows like 'X → Y'.
- Format all key concepts with bold titles and clean bullet points.

Structure:
# ${topic} - University Exam Study Guide (${subject})
## 1. Quick Overview & Formal Definition
## 2. Core Concepts & Terminology (High-Yield)
## 3. Working Mechanism & Step-by-Step Architecture (with code or examples)
## 4. Key Advantages, Limitations & Edge Cases
## 5. High-Probability Practice Questions (2-Mark, 5-Mark, 10-Mark)`;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        temperature: 0.5
      }
    });

    return res.json({ notes: response.text || '' });
  } catch (error: any) {
    console.error('[API /api/notes error]:', error);
    return res.status(500).json({ error: error?.message || 'Notes generation failed.' });
  }
});

// --------------------------------------------------------------------
// 4. QUIZ GENERATOR ROUTE
// --------------------------------------------------------------------
app.post('/api/quiz', async (req: Request, res: Response) => {
  try {
    const { subject, topic, difficulty = 'Medium', count = 3 } = req.body;

    if (!topic) {
      return res.status(400).json({ error: 'Topic is required.' });
    }

    const ai = getGeminiClient();
    const model = getModelName();

    const prompt = `Generate ${count} academic multiple-choice practice questions on:
Subject: ${subject || 'Computer Science'}
Topic: ${topic}
Difficulty: ${difficulty}

Output MUST be a valid JSON array of objects adhering strictly to this schema:
[
  {
    "id": 1,
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": "Option A",
    "explanation": "Why this answer is correct."
  }
]
Return pure JSON only without markdown wrapping.`;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        temperature: 0.2
      }
    });

    let raw = (response.text || '').trim();
    if (raw.startsWith('```')) {
      raw = raw.replace(/^```[a-zA-Z]*\n/, '').replace(/\n```$/, '');
    }

    const questions = JSON.parse(raw);
    return res.json({ questions });
  } catch (error: any) {
    console.error('[API /api/quiz error]:', error);
    return res.status(500).json({ error: error?.message || 'Quiz generation failed.' });
  }
});

// --------------------------------------------------------------------
// 5. PERSONALIZED STUDY PLANNER ROUTE
// --------------------------------------------------------------------
app.post('/api/study-plan', async (req: Request, res: Response) => {
  try {
    const {
      subject,
      topics,
      examDate,
      hoursPerDay = 2,
      preferredTime = 'Evening',
      difficulty = 'Balanced'
    } = req.body;

    if (!subject || !topics) {
      return res.status(400).json({ error: 'Subject and Topics are required to generate a study plan.' });
    }

    const ai = getGeminiClient();
    const model = getModelName();

    const prompt = `Create a realistic, personalized university academic study schedule for a student.
Subject: ${subject}
Target Topics to Cover: ${topics}
Target Exam Date: ${examDate || 'Next 2-3 weeks'}
Available Study Time per Day: ${hoursPerDay} hours
Preferred Study Hours: ${preferredTime}
Preparation Focus: ${difficulty}

Generate a structured set of 4 to 8 sequential study tasks spaced logically before the target exam date.
Each task must be practical and actionable (e.g. reading concepts, solving numericals, reviewing previous exam questions, formula revision).

Return STRICTLY a JSON object with this exact schema (no markdown, no backticks, pure JSON):
{
  "planTitle": "Personalized Study Schedule for ${subject}",
  "summary": "1-2 sentence overview of the study strategy and spaced repetition pacing.",
  "tasks": [
    {
      "id": "task-1",
      "title": "Clear action-oriented task title",
      "subject": "${subject}",
      "description": "Specific focus points, chapters to revise, or questions to practice.",
      "dueDate": "YYYY-MM-DD",
      "durationMinutes": 60,
      "priority": "High",
      "completed": false
    }
  ]
}`;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        temperature: 0.3
      }
    });

    let raw = (response.text || '').trim();
    if (raw.startsWith('```')) {
      raw = raw.replace(/^```[a-zA-Z]*\n/, '').replace(/\n```$/, '');
    }

    const plan = JSON.parse(raw);
    return res.json(plan);
  } catch (error: any) {
    console.error('[API /api/study-plan error]:', error);
    return res.status(500).json({ error: error?.message || 'Study plan generation failed.' });
  }
});

// --------------------------------------------------------------------
// VITE MIDDLEWARE & STATIC SERVING
// --------------------------------------------------------------------
async function startServer() {
  const isProd = process.env.NODE_ENV === 'production';

  if (!isProd) {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.resolve(__dirname, 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.resolve(distPath, 'index.html'));
    });
  }

  app.listen(port, '0.0.0.0', () => {
    console.log(`[AI Student Assistant] Server running on http://0.0.0.0:${port}`);
  });
}

startServer().catch((err) => {
  console.error('[Server startup error]:', err);
});
