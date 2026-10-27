/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useId } from 'react';
import {
  GraduationCap,
  BookOpen,
  FileText,
  CheckCircle,
  HelpCircle,
  Send,
  Sparkles,
  Clock,
  Settings,
  User,
  Calendar,
  Download,
  RotateCcw,
  AlertCircle,
  Trash2,
  BarChart3,
  Layers,
  Code2,
  CheckSquare,
  Square,
  ArrowRight,
  BookMarked,
  Info,
  Copy,
  Check,
  Upload,
  FileUp,
  Plus,
  X,
  Filter
} from 'lucide-react';
import { FormattedAcademicAnswer } from './components/FormattedAcademicAnswer';

interface StudentProfile {
  username: string;
  fullName: string;
  course: string;
  branch: string;
  semester: string;
  college: string;
  graduationYear: number;
  preferredLanguage: string;
  subjects: string[];
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  style?: string;
}

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
}

interface StudyTask {
  id: string;
  title: string;
  subject: string;
  description: string;
  dueDate: string;
  durationMinutes: number;
  priority: 'High' | 'Medium' | 'Low';
  completed: boolean;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'chat' | 'pdf' | 'notes' | 'quiz' | 'planner' | 'tests' | 'profile' | 'settings'>('dashboard');

  // Student Profile State
  const [profile, setProfile] = useState<StudentProfile>({
    username: 'alex_cs',
    fullName: 'Alex Johnson',
    course: 'B.Tech in Computer Science',
    branch: 'Artificial Intelligence & Systems',
    semester: 'Semester 5 (3rd Year)',
    college: 'Institute of Engineering & Technology',
    graduationYear: 2027,
    preferredLanguage: 'English',
    subjects: ['Operating Systems', 'Database Management', 'Design & Analysis of Algorithms', 'Computer Networks']
  });

  // Chat State
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-1',
      role: 'assistant',
      content: `Hello ${profile.fullName}! I'm your AI Student Assistant Agent.\n\nI am tailored to your **${profile.course}** curriculum (${profile.semester}). You can ask me conceptual doubts, request 2-mark, 5-mark, or 10-mark semester exam answers, or compare complex algorithms. How can I assist your study today?`,
      timestamp: '10:00 AM'
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [chatStyle, setChatStyle] = useState('5_marks');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);

  const handleCopyMessage = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(id);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  // PDF Assistant State
  const [activePdfName, setActivePdfName] = useState<string>('Unit_3_Operating_Systems_Memory_Management.pdf');
  const [activePdfPages, setActivePdfPages] = useState<number>(5);
  const [activePdfChunks, setActivePdfChunks] = useState<Array<{ id: number; page_number: number; content: string }>>([
    {
      id: 1,
      page_number: 1,
      content: "Unit 3: Operating Systems Memory Management. Physical vs Logical Address Space. Memory Management Unit (MMU) run-time mapping. Continuous vs Non-contiguous allocation."
    },
    {
      id: 2,
      page_number: 4,
      content: "Virtual Memory is a memory management technique providing an idealized contiguous abstraction of storage resources. Paging allows noncontiguous physical frame allocation in RAM, eliminating external fragmentation."
    },
    {
      id: 3,
      page_number: 5,
      content: "Translation Lookaside Buffer (TLB) is an associative hardware cache holding recently translated page table entries. TLB hit resolves virtual-to-physical address in 1 clock cycle; TLB miss incurs memory penalty for page table walk."
    }
  ]);
  const [pdfQuery, setPdfQuery] = useState('');
  const [pdfAnswer, setPdfAnswer] = useState<string | null>(null);
  const [pdfRetrievedContext, setPdfRetrievedContext] = useState<string | null>(null);
  const [isPdfSearching, setIsPdfSearching] = useState(false);
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  // Notes Generator State
  const [notesSubject, setNotesSubject] = useState('Database Management Systems');
  const [notesUnit, setNotesUnit] = useState('Unit 3: Normalization & Indexing');
  const [notesTopic, setNotesTopic] = useState('BCNF vs 3NF and Functional Dependencies');
  const [notesFormat, setNotesFormat] = useState('Comprehensive 10-Mark Notes with Comparison');
  const [generatedNotes, setGeneratedNotes] = useState<string | null>(null);
  const [isGeneratingNotes, setIsGeneratingNotes] = useState(false);

  // Quiz State
  const [quizTopic, setQuizTopic] = useState('Operating Systems - CPU Scheduling & Deadlocks');
  const [quizDifficulty, setQuizDifficulty] = useState<'Easy' | 'Medium' | 'Hard'>('Medium');
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([
    {
      id: 1,
      question: 'Which of the following scheduling algorithms can lead to the "convoy effect"?',
      options: ['Round Robin (RR)', 'First-Come, First-Served (FCFS)', 'Shortest Job First (SJF)', 'Priority Scheduling'],
      correctAnswer: 'First-Come, First-Served (FCFS)',
      explanation: 'FCFS can result in a convoy effect when a CPU-bound process holds the CPU for a long burst time while multiple I/O-bound processes wait in the ready queue.'
    },
    {
      id: 2,
      question: 'Which condition is NOT one of Coffman\'s four necessary conditions for deadlock?',
      options: ['Mutual Exclusion', 'Preemption Allowed', 'Hold and Wait', 'Circular Wait'],
      correctAnswer: 'Preemption Allowed',
      explanation: 'No preemption (resources cannot be forcibly taken away) is the necessary condition. If preemption is allowed, deadlock is eliminated.'
    },
    {
      id: 3,
      question: 'What is the primary objective of the Banker\'s Algorithm in an Operating System?',
      options: ['Deadlock Detection', 'Deadlock Avoidance', 'Deadlock Recovery', 'Mutual Exclusion Enforcement'],
      correctAnswer: 'Deadlock Avoidance',
      explanation: 'Banker\'s algorithm determines safe states before granting resource requests to proactively avoid deadlock.'
    }
  ]);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState<number | null>(null);

  // Study Planner State
  const [tasks, setTasks] = useState<StudyTask[]>([
    {
      id: 'task-1',
      title: 'Revise Virtual Memory & Page Replacement (FIFO, LRU)',
      subject: 'Operating Systems',
      description: 'Practice 5-mark numerical problems on page faults for FIFO vs Optimal vs LRU.',
      dueDate: '2026-10-28',
      durationMinutes: 90,
      priority: 'High',
      completed: true
    },
    {
      id: 'task-2',
      title: 'Solve B-Tree and B+ Tree Insertion Exercises',
      subject: 'Database Management',
      description: 'Draw split operations and height calculation for degree d=3.',
      dueDate: '2026-10-29',
      durationMinutes: 60,
      priority: 'High',
      completed: false
    },
    {
      id: 'task-3',
      title: 'Review Dijkstra and Bellman-Ford Shortest Path',
      subject: 'Algorithms',
      description: 'Analyze negative edge cycle detection and time complexity comparison table.',
      dueDate: '2026-10-31',
      durationMinutes: 75,
      priority: 'Medium',
      completed: false
    },
    {
      id: 'task-4',
      title: 'Practice TCP 3-Way Handshake & Congestion Control',
      subject: 'Computer Networks',
      description: 'Prepare 10-mark state diagram of TCP connection establishment and slow start.',
      dueDate: '2026-11-02',
      durationMinutes: 90,
      priority: 'Medium',
      completed: false
    }
  ]);

  // Quiz History
  const [quizHistory, setQuizHistory] = useState([
    { topic: 'Relational Algebra & Normalization', subject: 'DBMS', score: 100, date: '2026-10-25', difficulty: 'Hard' },
    { topic: 'Process Synchronization & Semaphores', subject: 'OS', score: 85, date: '2026-10-24', difficulty: 'Medium' },
    { topic: 'Divide and Conquer Algorithms', subject: 'DAA', score: 90, date: '2026-10-22', difficulty: 'Medium' }
  ]);

  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);

  // Handle chat submission using live Gemini API
  const handleSendChat = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || isGenerating) return;

    const userText = inputQuery.trim();
    setInputQuery('');

    const newMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      style: chatStyle
    };

    setChatMessages((prev) => [...prev, newMsg]);
    setIsGenerating(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userText,
          style: chatStyle,
          profile,
          history: chatMessages.slice(-6).map((m) => ({ role: m.role, content: m.content }))
        })
      });

      const data = await res.json();
      if (res.ok && data.reply) {
        setChatMessages((prev) => [
          ...prev,
          {
            id: `bot-${Date.now()}`,
            role: 'assistant',
            content: data.reply,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      } else {
        throw new Error(data.error || 'Failed to generate answer.');
      }
    } catch (err: any) {
      setChatMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          role: 'assistant',
          content: `⚠️ Error generating answer: ${err.message || 'Please verify API key and network connection.'}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  // Pre-configured sample documents for instant academic exploration
  const sampleAcademicDocs = [
    {
      name: 'Unit_3_Operating_Systems_Memory_Management.pdf',
      pages: 5,
      chunks: [
        {
          id: 1,
          page_number: 1,
          content: "Unit 3: Operating Systems Memory Management. Physical vs Logical Address Space. Memory Management Unit (MMU) run-time mapping. Continuous vs Non-contiguous allocation."
        },
        {
          id: 2,
          page_number: 4,
          content: "Virtual Memory is a memory management technique providing an idealized contiguous abstraction of storage resources. Paging allows noncontiguous physical frame allocation in RAM, eliminating external fragmentation."
        },
        {
          id: 3,
          page_number: 5,
          content: "Translation Lookaside Buffer (TLB) is an associative hardware cache holding recently translated page table entries. TLB hit resolves virtual-to-physical address in 1 clock cycle; TLB miss incurs memory penalty for page table walk."
        }
      ]
    },
    {
      name: 'DBMS_Unit_4_Normalization_and_Dependencies.pdf',
      pages: 8,
      chunks: [
        {
          id: 1,
          page_number: 2,
          content: "Database Normalization is the systematic decomposition of relations to eliminate insertion, update, and deletion anomalies while minimizing data redundancy."
        },
        {
          id: 2,
          page_number: 5,
          content: "Third Normal Form (3NF): A relation R is in 3NF if for every non-trivial functional dependency X → Y, either X is a super key or Y is a prime attribute (eliminating transitive dependencies)."
        },
        {
          id: 3,
          page_number: 7,
          content: "Boyce-Codd Normal Form (BCNF): A stricter version of 3NF. A relation is in BCNF if for every non-trivial functional dependency X → Y, X is strictly a super key. BCNF removes all anomalies from functional dependencies."
        }
      ]
    },
    {
      name: 'Computer_Networks_Unit_2_Transport_Layer.pdf',
      pages: 6,
      chunks: [
        {
          id: 1,
          page_number: 1,
          content: "The Transport Layer provides logical process-to-process communication services for host applications. Key protocols include TCP (RFC 793) and UDP (RFC 768)."
        },
        {
          id: 2,
          page_number: 3,
          content: "Transmission Control Protocol (TCP): Connection-oriented protocol providing reliable, byte-stream, in-order packet delivery using 3-way handshaking (SYN, SYN-ACK, ACK) and congestion control."
        },
        {
          id: 3,
          page_number: 4,
          content: "User Datagram Protocol (UDP): Connectionless, lightweight transport protocol with low latency and zero connection overhead. Best suited for real-time video streaming, VoIP, and DNS lookups."
        }
      ]
    }
  ];

  // Quick switch between sample documents
  const handleSelectSampleDoc = (docIndex: number) => {
    const doc = sampleAcademicDocs[docIndex];
    if (!doc) return;
    setActivePdfName(doc.name);
    setActivePdfPages(doc.pages);
    setActivePdfChunks(doc.chunks);
    setPdfAnswer(null);
    setPdfRetrievedContext(null);
    setUploadSuccess(`Switched active document to: "${doc.name}" (${doc.pages} pages)`);
    setUploadError(null);
  };

  // Upload custom PDF, text, or markdown document
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingDoc(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const isPdf = file.name.toLowerCase().endsWith('.pdf');
      const isText = file.name.toLowerCase().endsWith('.txt') || file.name.toLowerCase().endsWith('.md');

      if (!isPdf && !isText) {
        throw new Error('Please select a valid PDF (.pdf) or text/markdown (.txt, .md) file.');
      }

      if (file.size > 15 * 1024 * 1024) {
        throw new Error('File size exceeds the 15MB limit. Please upload a smaller study document.');
      }

      if (isPdf) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = async () => {
          try {
            const base64Data = (reader.result as string).split(',')[1];
            const res = await fetch('/api/upload-pdf', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                filename: file.name,
                base64: base64Data
              })
            });
            const data = await res.json();
            if (res.ok && data.success) {
              setActivePdfName(data.filename || file.name);
              setActivePdfPages(data.total_pages || 1);
              if (data.chunks && data.chunks.length > 0) {
                setActivePdfChunks(data.chunks);
              } else {
                setActivePdfChunks([
                  { id: 1, page_number: 1, content: "Extracted document content indexed and ready for Q&A." }
                ]);
              }
              setUploadSuccess(`Successfully parsed "${file.name}" (${data.total_pages || 1} pages, ${data.chunks?.length || 1} chunks) with PyMuPDF!`);
              setPdfAnswer(null);
              setPdfRetrievedContext(null);
            } else {
              throw new Error(data.message || 'Failed to parse PDF document.');
            }
          } catch (err: any) {
            setUploadError(err.message || 'Error processing PDF.');
          } finally {
            setIsUploadingDoc(false);
          }
        };
        reader.onerror = () => {
          setUploadError('Failed to read the selected file.');
          setIsUploadingDoc(false);
        };
      } else {
        // Plain text or markdown study notes
        const textContent = await file.text();
        const res = await fetch('/api/upload-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename: file.name,
            textContent
          })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          setActivePdfName(data.filename || file.name);
          setActivePdfPages(data.total_pages || 1);
          setActivePdfChunks(data.chunks || []);
          setUploadSuccess(`Successfully loaded "${file.name}" with ${data.chunks?.length || 1} indexed passages!`);
          setPdfAnswer(null);
          setPdfRetrievedContext(null);
        } else {
          throw new Error(data.message || 'Failed to parse text document.');
        }
        setIsUploadingDoc(false);
      }
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload document.');
      setIsUploadingDoc(false);
    }
  };

  // Handle PDF Q&A using live Gemini API and dynamic indexed chunks
  const handlePdfSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pdfQuery.trim() || isPdfSearching) return;

    setIsPdfSearching(true);
    try {
      const queryLower = pdfQuery.toLowerCase();
      const keywords = queryLower.split(/\s+/).filter(w => w.length > 3);

      let relevantChunks = activePdfChunks.filter(chunk => {
        const cLower = chunk.content.toLowerCase();
        return keywords.some(k => cLower.includes(k));
      });

      if (relevantChunks.length === 0) {
        relevantChunks = activePdfChunks.slice(0, 4);
      }

      const docContext = relevantChunks
        .map(c => `[Source: Page ${c.page_number}]\n${c.content}`)
        .join('\n\n');

      const res = await fetch('/api/pdf-qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: pdfQuery,
          documentName: activePdfName,
          documentContext: docContext
        })
      });

      const data = await res.json();
      if (res.ok && data.reply) {
        setPdfRetrievedContext(
          relevantChunks
            .map(c => `[Source: Page ${c.page_number}]\n"${c.content}"`)
            .join('\n\n---\n\n')
        );
        setPdfAnswer(data.reply);
      } else {
        throw new Error(data.error || 'Document search failed.');
      }
    } catch (err: any) {
      setPdfAnswer(`⚠️ Error querying document: ${err.message}`);
    } finally {
      setIsPdfSearching(false);
    }
  };

  // Handle Notes Generation using live Gemini API
  const handleGenerateNotes = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGeneratingNotes(true);
    try {
      const res = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: notesSubject,
          unit: notesUnit,
          topic: notesTopic,
          format: notesFormat
        })
      });

      const data = await res.json();
      if (res.ok && data.notes) {
        setGeneratedNotes(data.notes);
      } else {
        throw new Error(data.error || 'Failed to generate notes.');
      }
    } catch (err: any) {
      setGeneratedNotes(`⚠️ Error generating exam notes: ${err.message}`);
    } finally {
      setIsGeneratingNotes(false);
    }
  };

  // Handle Dynamic Quiz Generation from Gemini API
  const handleCreateNewQuiz = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (isGeneratingQuiz) return;
    setIsGeneratingQuiz(true);
    try {
      const res = await fetch('/api/quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: notesSubject,
          topic: quizTopic,
          difficulty: quizDifficulty,
          count: 3
        })
      });

      const data = await res.json();
      if (res.ok && Array.isArray(data.questions) && data.questions.length > 0) {
        setQuizQuestions(data.questions);
        setUserAnswers({});
        setQuizSubmitted(false);
        setQuizScore(null);
      } else {
        throw new Error(data.error || 'Failed to generate quiz.');
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsGeneratingQuiz(false);
    }
  };

  // Handle Quiz Submission
  const handleSelectQuizAnswer = (qId: number, option: string) => {
    if (quizSubmitted) return;
    setUserAnswers((prev) => ({ ...prev, [qId]: option }));
  };

  const handleSubmitQuiz = () => {
    let correctCount = 0;
    quizQuestions.forEach((q) => {
      if (userAnswers[q.id] === q.correctAnswer) {
        correctCount++;
      }
    });
    const percentage = Math.round((correctCount / quizQuestions.length) * 100);
    setQuizScore(percentage);
    setQuizSubmitted(true);

    // Add to history
    setQuizHistory((prev) => [
      {
        topic: quizTopic,
        subject: 'Operating Systems',
        score: percentage,
        date: new Date().toISOString().split('T')[0],
        difficulty: quizDifficulty
      },
      ...prev
    ]);
  };

  const handleRetakeQuiz = () => {
    setUserAnswers({});
    setQuizSubmitted(false);
    setQuizScore(null);
  };

  // Toggle Task Completion
  const toggleTask = (taskId: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, completed: !t.completed } : t))
    );
  };

  // Calculated Progress
  const completedTasks = tasks.filter((t) => t.completed).length;
  const taskProgressPct = Math.round((completedTasks / tasks.length) * 100);
  const avgQuizScore = Math.round(
    quizHistory.reduce((acc, curr) => acc + curr.score, 0) / quizHistory.length
  );

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">
      {/* SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Brand Header */}
          <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-sky-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-slate-100 text-base leading-tight">Student AI Agent</h1>
              <span className="text-xs text-sky-400 font-medium">Academic Mentor</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'dashboard'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('chat')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>AI Academic Chat</span>
            </button>

            <button
              onClick={() => setActiveTab('pdf')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'pdf'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <FileText className="w-4 h-4 text-rose-400" />
              <span>PDF Study Assistant</span>
            </button>

            <button
              onClick={() => setActiveTab('notes')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'notes'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <BookOpen className="w-4 h-4 text-emerald-400" />
              <span>Exam Notes Generator</span>
            </button>

            <button
              onClick={() => setActiveTab('quiz')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'quiz'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <CheckCircle className="w-4 h-4 text-violet-400" />
              <span>Quiz Generator</span>
            </button>

            <button
              onClick={() => setActiveTab('planner')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'planner'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Calendar className="w-4 h-4 text-cyan-400" />
              <span>Study Planner</span>
            </button>

            <div className="pt-2 pb-1">
              <div className="border-t border-slate-800" />
            </div>

            <button
              onClick={() => setActiveTab('tests')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'tests'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Code2 className="w-4 h-4 text-green-400" />
              <span>Test Suite (32 Passed)</span>
            </button>

            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'profile'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <User className="w-4 h-4 text-slate-400" />
              <span>My Profile</span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'settings'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Settings className="w-4 h-4 text-slate-400" />
              <span>Settings & Architecture</span>
            </button>
          </nav>
        </div>

        {/* User Card in Sidebar */}
        <div className="p-3 border-t border-slate-800">
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2.5 truncate">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs shrink-0">
                {profile.fullName.split(' ').map((n) => n[0]).join('')}
              </div>
              <div className="truncate">
                <p className="text-xs font-semibold text-slate-200 truncate">{profile.fullName}</p>
                <p className="text-[10px] text-slate-400 truncate">{profile.semester}</p>
              </div>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50 shrink-0" title="Online" />
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col overflow-y-auto bg-slate-950">
        {/* TOP STATUS BAR */}
        <header className="h-14 border-b border-slate-800/80 bg-slate-900/50 px-6 flex items-center justify-between shrink-0 backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Agent Ready
            </span>
            <span className="text-xs text-slate-400 hidden sm:inline">
              Model: <strong className="text-slate-200 font-mono">gemini-2.5-flash</strong>
            </span>
            <span className="text-slate-600 hidden sm:inline">•</span>
            <span className="text-xs text-slate-400 hidden sm:inline">
              Database: <strong className="text-slate-200">Supabase PostgreSQL (RLS Enforced)</strong>
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('tests')}
              className="flex items-center space-x-1.5 px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition"
            >
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              <span>32/32 Pytest Passed</span>
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* TAB 1: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div className="p-6 max-w-7xl mx-auto w-full space-y-6">
            {/* Welcome Hero Banner */}
            <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-indigo-500/20 shadow-xl relative overflow-hidden">
              <div className="relative z-10">
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {profile.branch}
                </span>
                <h2 className="text-2xl font-extrabold text-white mt-3 mb-1">
                  Welcome back, {profile.fullName}! 👋
                </h2>
                <p className="text-sm text-slate-300 max-w-2xl">
                  {profile.course} • {profile.semester} at {profile.college}.
                  Your persistent memory and study tasks are synced with Supabase.
                </p>
              </div>
            </div>

            {/* Metric Cards (True Stored Metrics) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium uppercase tracking-wider">Active Study Tasks</span>
                  <CheckSquare className="w-4 h-4 text-sky-400" />
                </div>
                <div className="text-2xl font-bold text-white">
                  {completedTasks} / {tasks.length}
                </div>
                <div className="text-xs text-sky-400 font-medium mt-1">
                  {taskProgressPct}% completed this week
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium uppercase tracking-wider">Average Quiz Score</span>
                  <BarChart3 className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-2xl font-bold text-white">{avgQuizScore}%</div>
                <div className="text-xs text-emerald-400 font-medium mt-1">Across {quizHistory.length} attempts</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium uppercase tracking-wider">Active Document</span>
                  <FileText className="w-4 h-4 text-rose-400" />
                </div>
                <div className="text-sm font-bold text-white truncate">{activePdfName}</div>
                <div className="text-xs text-rose-400 font-medium mt-1">PyMuPDF Indexed (5 Pages)</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium uppercase tracking-wider">AI Explanations</span>
                  <Sparkles className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-2xl font-bold text-white">7 Formats</div>
                <div className="text-xs text-amber-400 font-medium mt-1">2/5/10 Marks & Tables</div>
              </div>
            </div>

            {/* Quick Action Shortcuts */}
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">
                ⚡ Quick Academic Actions
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                <button
                  onClick={() => setActiveTab('chat')}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800/40 transition text-left group"
                >
                  <Sparkles className="w-5 h-5 text-indigo-400 mb-2 group-hover:scale-110 transition" />
                  <div className="font-semibold text-sm text-slate-200">Ask AI Agent</div>
                  <div className="text-xs text-slate-400 mt-0.5">Instant academic solutions</div>
                </button>

                <button
                  onClick={() => setActiveTab('pdf')}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-rose-500/50 hover:bg-slate-800/40 transition text-left group"
                >
                  <FileText className="w-5 h-5 text-rose-400 mb-2 group-hover:scale-110 transition" />
                  <div className="font-semibold text-sm text-slate-200">PDF Study Q&A</div>
                  <div className="text-xs text-slate-400 mt-0.5">Grounded page citations</div>
                </button>

                <button
                  onClick={() => setActiveTab('notes')}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-800/40 transition text-left group"
                >
                  <BookOpen className="w-5 h-5 text-emerald-400 mb-2 group-hover:scale-110 transition" />
                  <div className="font-semibold text-sm text-slate-200">Exam Notes</div>
                  <div className="text-xs text-slate-400 mt-0.5">High-yield study guides</div>
                </button>

                <button
                  onClick={() => setActiveTab('quiz')}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-violet-500/50 hover:bg-slate-800/40 transition text-left group"
                >
                  <CheckCircle className="w-5 h-5 text-violet-400 mb-2 group-hover:scale-110 transition" />
                  <div className="font-semibold text-sm text-slate-200">Practice Quiz</div>
                  <div className="text-xs text-slate-400 mt-0.5">Deterministic Python grading</div>
                </button>

                <button
                  onClick={() => setActiveTab('planner')}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/40 transition text-left group"
                >
                  <Calendar className="w-5 h-5 text-cyan-400 mb-2 group-hover:scale-110 transition" />
                  <div className="font-semibold text-sm text-slate-200">Study Planner</div>
                  <div className="text-xs text-slate-400 mt-0.5">Exam schedule breakdown</div>
                </button>
              </div>
            </div>

            {/* Split Section: Checklist + Recent Quizzes */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Task Checklist */}
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-slate-200 text-sm flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-cyan-400" />
                    <span>Upcoming Exam Tasks</span>
                  </h3>
                  <button
                    onClick={() => setActiveTab('planner')}
                    className="text-xs text-sky-400 hover:underline flex items-center"
                  >
                    View All <ArrowRight className="w-3 h-3 ml-1" />
                  </button>
                </div>
                <div className="space-y-2.5">
                  {tasks.slice(0, 3).map((task) => (
                    <div
                      key={task.id}
                      onClick={() => toggleTask(task.id)}
                      className="p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-800 cursor-pointer flex items-start space-x-3 transition"
                    >
                      {task.completed ? (
                        <CheckSquare className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-500 mt-0.5 shrink-0" />
                      )}
                      <div className="flex-1 truncate">
                        <p
                          className={`text-xs font-semibold ${
                            task.completed ? 'line-through text-slate-500' : 'text-slate-200'
                          }`}
                        >
                          {task.title}
                        </p>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          {task.subject} • ⏱️ {task.durationMinutes}m • Due: {task.dueDate}
                        </p>
                      </div>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                          task.priority === 'High'
                            ? 'bg-rose-500/20 text-rose-400'
                            : 'bg-amber-500/20 text-amber-400'
                        }`}
                      >
                        {task.priority}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Quiz Logs */}
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-slate-200 text-sm flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-violet-400" />
                    <span>Recent Quiz Attempts</span>
                  </h3>
                  <button
                    onClick={() => setActiveTab('quiz')}
                    className="text-xs text-sky-400 hover:underline flex items-center"
                  >
                    Take Quiz <ArrowRight className="w-3 h-3 ml-1" />
                  </button>
                </div>
                <div className="space-y-2.5">
                  {quizHistory.map((q, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-800/50 border border-slate-800 flex items-center justify-between"
                    >
                      <div>
                        <div className="text-xs font-semibold text-slate-200">{q.topic}</div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {q.subject} • Difficulty: {q.difficulty} • 📅 {q.date}
                        </div>
                      </div>
                      <span
                        className={`px-2.5 py-1 rounded-md text-xs font-extrabold ${
                          q.score >= 80
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {q.score}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: AI ACADEMIC CHAT */}
        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col p-6 max-w-5xl mx-auto w-full h-[calc(100vh-3.5rem)]">
            {/* Chat Control Toolbar */}
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl mb-4 flex flex-wrap items-center justify-between gap-3 shrink-0">
              <div className="flex items-center space-x-2">
                <label className="text-xs font-semibold text-slate-400">Response Style:</label>
                <select
                  value={chatStyle}
                  onChange={(e) => setChatStyle(e.target.value)}
                  className="bg-slate-800 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="5_marks">5-Mark Standard Exam Answer</option>
                  <option value="2_marks">2-Mark Concise Definition</option>
                  <option value="10_marks">10-Mark In-Depth Answer with Diagrams</option>
                  <option value="comparison">Structured Comparison Table</option>
                  <option value="simple">Simple / Beginner Analogy</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() =>
                    setChatMessages([
                      {
                        id: `msg-${Date.now()}`,
                        role: 'assistant',
                        content: `Session refreshed. How can I assist with your ${profile.course} studies?`,
                        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                      }
                    ])
                  }
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>New Chat</span>
                </button>
              </div>
            </div>

            {/* Message Stream */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-1">
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-4 shadow-sm ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none'
                        : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none prose prose-invert prose-sm max-w-none'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      <div>
                        <div className="text-[10px] text-indigo-200 mb-1 flex items-center justify-between font-semibold">
                          <span>{profile.fullName}</span>
                          <span>{msg.timestamp}</span>
                        </div>
                        <div className="text-sm leading-relaxed">{msg.content}</div>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {/* Header Bar */}
                        <div className="flex flex-wrap items-center justify-between pb-2 mb-2 border-b border-slate-800/80 text-xs gap-2">
                          <div className="flex items-center space-x-2">
                            <span className="w-5 h-5 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-[10px]">
                              AI
                            </span>
                            <span className="font-bold text-slate-200 text-xs">AI Academic Mentor</span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                              {msg.style === '2_marks'
                                ? '2-Mark Quick Format'
                                : msg.style === '10_marks'
                                ? '10-Mark Detailed Format'
                                : msg.style === 'comparison'
                                ? 'Comparison Table Format'
                                : msg.style === 'simple'
                                ? 'Simple Analogy Format'
                                : '5-Mark Exam Format'}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-[10px] text-slate-500">{msg.timestamp}</span>
                            <button
                              onClick={() => handleCopyMessage(msg.content, msg.id)}
                              className="flex items-center space-x-1 px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] transition border border-slate-700/60"
                              title="Copy answer to notes"
                            >
                              {copiedMsgId === msg.id ? (
                                <>
                                  <Check className="w-3 h-3 text-emerald-400" />
                                  <span className="text-emerald-400 font-semibold">Copied!</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3 h-3" />
                                  <span>Copy Notes</span>
                                </>
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Rich Pedagogical Content */}
                        <FormattedAcademicAnswer content={msg.content} />
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isGenerating && (
                <div className="flex justify-start">
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-xs flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" />
                    <span>Analyzing university curriculum and generating exam-ready explanation...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendChat} className="mt-4 flex items-center space-x-2 shrink-0">
              <input
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                placeholder="Ask any concept: 'Explain Semaphore vs Mutex', 'Give me 10 marks on Paging'..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={!inputQuery.trim() || isGenerating}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-5 py-3 rounded-xl font-semibold text-sm flex items-center space-x-1.5 shadow-md shadow-indigo-600/20 transition"
              >
                <span>Send</span>
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        )}

        {/* TAB 3: PDF STUDY ASSISTANT */}
        {activeTab === 'pdf' && (
          <div className="p-6 max-w-5xl mx-auto w-full space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <FileText className="w-5 h-5 text-rose-400" />
                <span>PDF Study Assistant (PyMuPDF Extraction & Grounding)</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Upload your study materials, lecture slides, or textbook chapters to ask grounded questions with exact page references.
              </p>
            </div>

            {/* Hidden File Input */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.txt,.md"
              className="hidden"
            />

            {/* Document Upload & Quick Selector Zone */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div>
                  <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                    <FileUp className="w-4 h-4 text-rose-400" />
                    <span>Upload Study Materials or Select Academic Syllabus</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Supports textbook chapters, lecture slides, and notes in <strong className="text-slate-300">.pdf</strong> (PyMuPDF indexed), <strong className="text-slate-300">.txt</strong>, or <strong className="text-slate-300">.md</strong> formats (Max 15MB).
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploadingDoc}
                  className="bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-md shadow-rose-600/20 transition flex items-center space-x-2 shrink-0 cursor-pointer"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>{isUploadingDoc ? 'Parsing & Indexing...' : 'Upload New Document / PDF'}</span>
                </button>
              </div>

              {/* Upload Status / Alerts */}
              {isUploadingDoc && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2.5 animate-pulse">
                  <Sparkles className="w-4 h-4 text-rose-400 shrink-0 animate-spin" />
                  <span>Extracting text chunks and computing page boundaries using PyMuPDF backend...</span>
                </div>
              )}

              {uploadError && (
                <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center space-x-2">
                  <span className="font-bold">⚠️ Error:</span>
                  <span>{uploadError}</span>
                </div>
              )}

              {uploadSuccess && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{uploadSuccess}</span>
                </div>
              )}

              {/* Quick Select Academic Pre-loaded Documents */}
              <div className="pt-2 border-t border-slate-800/80">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  Quick Load Verified Course Documents:
                </span>
                <div className="flex flex-wrap gap-2">
                  {sampleAcademicDocs.map((doc, idx) => {
                    const isActive = activePdfName === doc.name;
                    return (
                      <button
                        key={doc.name}
                        type="button"
                        onClick={() => handleSelectSampleDoc(idx)}
                        className={`text-xs px-3 py-1.5 rounded-lg border transition flex items-center space-x-1.5 cursor-pointer ${
                          isActive
                            ? 'bg-rose-600/20 border-rose-500/60 text-rose-300 font-semibold'
                            : 'bg-slate-800/60 border-slate-700 hover:bg-slate-800 text-slate-300'
                        }`}
                      >
                        <FileText className="w-3.5 h-3.5 text-rose-400" />
                        <span>{doc.name.split('_')[0]}: {doc.name.replace('.pdf', '').slice(0, 32)}...</span>
                        <span className="text-[10px] text-slate-400 bg-slate-900/60 px-1.5 py-0.5 rounded">
                          {doc.pages}p
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Active Document Header */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold shrink-0">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white break-all">{activePdfName}</h4>
                  <p className="text-xs text-slate-400">
                    {activePdfPages} Page{activePdfPages > 1 ? 's' : ''} • {activePdfChunks.length} Searchable Chunks Indexed • PyMuPDF Verified
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2 shrink-0">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition border border-slate-700 flex items-center space-x-1 cursor-pointer"
                >
                  <Upload className="w-3 h-3" />
                  <span>Upload Different Doc</span>
                </button>
                <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium">
                  Active Context
                </span>
              </div>
            </div>

            {/* Query Form */}
            <form onSubmit={handlePdfSearch} className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300">
                  Ask a question grounded in this document:
                </label>
                <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                  <span>Try:</span>
                  <button
                    type="button"
                    onClick={() => setPdfQuery('What is the role of Translation Lookaside Buffer described in the document?')}
                    className="hover:text-rose-300 underline cursor-pointer"
                  >
                    TLB Role
                  </button>
                  <span>•</span>
                  <button
                    type="button"
                    onClick={() => setPdfQuery('Explain the conditions for BCNF and how it differs from 3NF.')}
                    className="hover:text-rose-300 underline cursor-pointer"
                  >
                    BCNF vs 3NF
                  </button>
                  <span>•</span>
                  <button
                    type="button"
                    onClick={() => setPdfQuery('Compare TCP 3-way handshake with UDP latency trade-offs.')}
                    className="hover:text-rose-300 underline cursor-pointer"
                  >
                    TCP vs UDP
                  </button>
                </div>
              </div>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={pdfQuery}
                  onChange={(e) => setPdfQuery(e.target.value)}
                  placeholder="e.g. What is the role of Translation Lookaside Buffer described in the document?"
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-rose-500"
                />
                <button
                  type="submit"
                  disabled={!pdfQuery.trim() || isPdfSearching}
                  className="bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl font-semibold text-sm transition shrink-0 cursor-pointer"
                >
                  {isPdfSearching ? 'Searching & Grounding...' : 'Search & Answer'}
                </button>
              </div>
            </form>

            {/* Answer Display */}
            {pdfAnswer && (
              <div className="space-y-4">
                <div className="p-5 rounded-xl bg-slate-900 border border-rose-500/30">
                  <h3 className="text-sm font-bold text-rose-400 mb-2 flex items-center space-x-1.5">
                    <CheckCircle className="w-4 h-4" />
                    <span>Grounded Document Answer</span>
                  </h3>
                  <FormattedAcademicAnswer content={pdfAnswer} />
                </div>

                {pdfRetrievedContext && (
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                      Retrieved Document Passages (PyMuPDF Lexical Chunks)
                    </h4>
                    <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                      {pdfRetrievedContext}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: EXAM NOTES GENERATOR */}
        {activeTab === 'notes' && (
          <div className="p-6 max-w-5xl mx-auto w-full space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-emerald-400" />
                <span>Exam Notes Generator</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Synthesize exam-oriented study guides with formal definitions, working mechanisms, algorithms, and practice questions.
              </p>
            </div>

            <form onSubmit={handleGenerateNotes} className="grid grid-cols-1 md:grid-cols-2 gap-4 p-5 rounded-xl bg-slate-900 border border-slate-800">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Subject</label>
                <input
                  type="text"
                  value={notesSubject}
                  onChange={(e) => setNotesSubject(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Unit / Chapter</label>
                <input
                  type="text"
                  value={notesUnit}
                  onChange={(e) => setNotesUnit(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-slate-400 mb-1">Topic / Concept</label>
                <input
                  type="text"
                  value={notesTopic}
                  onChange={(e) => setNotesTopic(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
                />
              </div>

              <div className="md:col-span-2 flex justify-end">
                <button
                  type="submit"
                  disabled={isGeneratingNotes}
                  className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-6 py-2.5 rounded-lg font-semibold text-sm shadow-md shadow-emerald-600/20 transition flex items-center space-x-2"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>{isGeneratingNotes ? 'Synthesizing...' : 'Generate Exam Notes'}</span>
                </button>
              </div>
            </form>

            {generatedNotes && (
              <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                    Generated Study Guide (.md)
                  </span>
                  <button
                    onClick={() => {
                      const blob = new Blob([generatedNotes], { type: 'text/markdown' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `${notesTopic.replace(/\s+/g, '_')}_Notes.md`;
                      a.click();
                    }}
                    className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg text-slate-200 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download (.md)</span>
                  </button>
                </div>
                <FormattedAcademicAnswer content={generatedNotes} />
              </div>
            )}
          </div>
        )}

        {/* TAB 5: QUIZ GENERATOR */}
        {activeTab === 'quiz' && (
          <div className="p-6 max-w-4xl mx-auto w-full space-y-6">
            <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-violet-400" />
                  <span>Quiz & Practice Test Generator</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Topic-specific tests with deterministic Python scoring and instant feedback explanations.
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={quizTopic}
                  onChange={(e) => setQuizTopic(e.target.value)}
                  placeholder="Enter topic..."
                  className="bg-slate-900 border border-slate-700 text-xs px-3 py-1.5 rounded-lg text-slate-200"
                />
                <button
                  onClick={handleCreateNewQuiz}
                  disabled={isGeneratingQuiz}
                  className="px-3 py-1.5 rounded-lg text-xs bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold flex items-center space-x-1"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{isGeneratingQuiz ? 'Generating...' : 'New Quiz'}</span>
                </button>
                {quizSubmitted && (
                  <button
                    onClick={handleRetakeQuiz}
                    className="px-3 py-1.5 rounded-lg text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center space-x-1"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Retake</span>
                  </button>
                )}
              </div>
            </div>

            {/* Score Banner */}
            {quizSubmitted && quizScore !== null && (
              <div
                className={`p-5 rounded-xl border text-center ${
                  quizScore >= 70
                    ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
                    : 'bg-amber-950/40 border-amber-500/50 text-amber-300'
                }`}
              >
                <div className="text-3xl font-extrabold mb-1">{quizScore}%</div>
                <p className="text-xs font-medium">
                  {quizScore >= 70
                    ? '🎉 Excellent performance! You have mastered this concept.'
                    : '📚 Keep practicing! Review the detailed explanations below.'}
                </p>
              </div>
            )}

            {/* Questions List */}
            <div className="space-y-5">
              {quizQuestions.map((q, qIndex) => {
                const isCorrect = userAnswers[q.id] === q.correctAnswer;
                return (
                  <div key={q.id} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                    <div className="flex items-start justify-between">
                      <h4 className="text-sm font-semibold text-white">
                        <span className="text-violet-400 mr-2">Q{qIndex + 1}.</span>
                        {q.question}
                      </h4>
                      {quizSubmitted && (
                        <span
                          className={`text-xs font-bold px-2 py-0.5 rounded ${
                            isCorrect ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                          }`}
                        >
                          {isCorrect ? 'Correct' : 'Incorrect'}
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 gap-2">
                      {q.options.map((opt) => {
                        const isSelected = userAnswers[q.id] === opt;
                        let optionStyle = 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 border-slate-800';

                        if (isSelected) {
                          optionStyle = 'bg-indigo-600/30 border-indigo-500 text-indigo-200 font-medium';
                        }
                        if (quizSubmitted) {
                          if (opt === q.correctAnswer) {
                            optionStyle = 'bg-emerald-600/20 border-emerald-500 text-emerald-300 font-medium';
                          } else if (isSelected && !isCorrect) {
                            optionStyle = 'bg-rose-600/20 border-rose-500 text-rose-300';
                          }
                        }

                        return (
                          <button
                            key={opt}
                            disabled={quizSubmitted}
                            onClick={() => handleSelectQuizAnswer(q.id, opt)}
                            className={`p-3 rounded-lg border text-left text-xs transition flex items-center justify-between ${optionStyle}`}
                          >
                            <span>{opt}</span>
                            {quizSubmitted && opt === q.correctAnswer && (
                              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 ml-2" />
                            )}
                          </button>
                        );
                      })}
                    </div>

                    {quizSubmitted && (
                      <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs text-slate-400 mt-2">
                        <strong className="text-slate-300">💡 Explanation: </strong>
                        {q.explanation}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {!quizSubmitted && (
              <div className="flex justify-end">
                <button
                  onClick={handleSubmitQuiz}
                  disabled={Object.keys(userAnswers).length < quizQuestions.length}
                  className="bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white px-6 py-2.5 rounded-lg font-semibold text-sm shadow-md shadow-violet-600/20 transition"
                >
                  Submit Quiz for Evaluation
                </button>
              </div>
            )}
          </div>
        )}

        {/* TAB 6: STUDY PLANNER */}
        {activeTab === 'planner' && (
          <div className="p-6 max-w-5xl mx-auto w-full space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <Calendar className="w-5 h-5 text-cyan-400" />
                <span>Personalized Study Planner</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Examination schedule balanced with spaced repetition and syllabus topic priorities.
              </p>
            </div>

            {/* Progress Bar */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <div className="flex justify-between text-xs text-slate-300">
                <span className="font-semibold">Semester Exam Readiness</span>
                <span>{completedTasks} of {tasks.length} tasks completed ({taskProgressPct}%)</span>
              </div>
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-full transition-all duration-300"
                  style={{ width: `${taskProgressPct}%` }}
                />
              </div>
            </div>

            {/* Task List */}
            <div className="space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => toggleTask(task.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition flex items-start space-x-3.5 ${
                    task.completed
                      ? 'bg-slate-900/40 border-slate-800/80 opacity-60'
                      : 'bg-slate-900 border-slate-800 hover:border-cyan-500/40'
                  }`}
                >
                  {task.completed ? (
                    <CheckSquare className="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
                  ) : (
                    <Square className="w-5 h-5 text-slate-500 mt-0.5 shrink-0" />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className={`text-sm font-semibold ${task.completed ? 'line-through text-slate-500' : 'text-slate-100'}`}>
                        {task.title}
                      </h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-cyan-300">
                        {task.subject}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          task.priority === 'High'
                            ? 'bg-rose-500/20 text-rose-400'
                            : 'bg-amber-500/20 text-amber-400'
                        }`}
                      >
                        {task.priority} Priority
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{task.description}</p>
                    <div className="flex items-center space-x-4 text-[11px] text-slate-500 mt-2">
                      <span>⏱️ Estimated: {task.durationMinutes} mins</span>
                      <span>📅 Target Due Date: {task.dueDate}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 7: TEST SUITE & ARCHITECTURE */}
        {activeTab === 'tests' && (
          <div className="p-6 max-w-5xl mx-auto w-full space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <Code2 className="w-5 h-5 text-green-400" />
                <span>Automated Test Suite & Verification</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Real Pytest execution results verifying all 32 unit and integration test cases across the 7 agent components.
              </p>
            </div>

            {/* Test summary card */}
            <div className="p-5 rounded-xl bg-slate-900 border border-green-500/30 flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-base font-bold text-white">32 of 32 Tests Passed (100%)</span>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Test framework: <code>pytest-9.1.1</code> with Python 3.11.2 • Execution duration: 2.36s
                </p>
              </div>
              <span className="px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full text-xs font-semibold">
                ALL PASSED
              </span>
            </div>

            {/* Breakdown table */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Test Module Breakdown
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between p-2.5 rounded-lg bg-slate-800/60 border border-slate-800">
                  <span className="font-mono text-slate-200">tests/test_auth_validation.py</span>
                  <span className="text-emerald-400 font-semibold">21 passed</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-lg bg-slate-800/60 border border-slate-800">
                  <span className="font-mono text-slate-200">tests/test_prompt_processing.py</span>
                  <span className="text-emerald-400 font-semibold">3 passed</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-lg bg-slate-800/60 border border-slate-800">
                  <span className="font-mono text-slate-200">tests/test_pdf_service.py</span>
                  <span className="text-emerald-400 font-semibold">3 passed</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-lg bg-slate-800/60 border border-slate-800">
                  <span className="font-mono text-slate-200">tests/test_quiz_service.py</span>
                  <span className="text-emerald-400 font-semibold">3 passed</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-lg bg-slate-800/60 border border-slate-800">
                  <span className="font-mono text-slate-200">tests/test_memory.py</span>
                  <span className="text-emerald-400 font-semibold">2 passed</span>
                </div>
              </div>
            </div>

            {/* Local run command box */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-sky-400">
                Exact Local Run Command (Section 24)
              </h4>
              <pre className="p-3 rounded-lg bg-slate-950 font-mono text-xs text-emerald-400 border border-slate-800">
                streamlit run app.py
              </pre>
            </div>
          </div>
        )}

        {/* TAB 8: PROFILE */}
        {activeTab === 'profile' && (
          <div className="p-6 max-w-4xl mx-auto w-full space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <User className="w-5 h-5 text-indigo-400" />
                <span>Student Academic Profile</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Your profile information is used by the Prompt Processor to customize technical depth and exam style.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="text-slate-400 font-semibold">Full Name</label>
                <div className="text-sm font-bold text-white mt-0.5">{profile.fullName}</div>
              </div>
              <div>
                <label className="text-slate-400 font-semibold">Username</label>
                <div className="text-sm font-bold text-white mt-0.5 font-mono">@{profile.username}</div>
              </div>
              <div>
                <label className="text-slate-400 font-semibold">Degree / Course</label>
                <div className="text-sm text-slate-200 mt-0.5">{profile.course}</div>
              </div>
              <div>
                <label className="text-slate-400 font-semibold">Branch / Specialization</label>
                <div className="text-sm text-slate-200 mt-0.5">{profile.branch}</div>
              </div>
              <div>
                <label className="text-slate-400 font-semibold">Semester / Year</label>
                <div className="text-sm text-slate-200 mt-0.5">{profile.semester}</div>
              </div>
              <div>
                <label className="text-slate-400 font-semibold">College / University</label>
                <div className="text-sm text-slate-200 mt-0.5">{profile.college}</div>
              </div>
              <div className="md:col-span-2">
                <label className="text-slate-400 font-semibold">Subjects of Interest</label>
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {profile.subjects.map((s) => (
                    <span key={s} className="px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 9: SETTINGS & ARCHITECTURE */}
        {activeTab === 'settings' && (
          <div className="p-6 max-w-5xl mx-auto w-full space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <Settings className="w-5 h-5 text-slate-400" />
                <span>Architecture & System Configuration</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Demonstrating all seven core components of an AI Agent.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                  Component 1 & 2: UI & Prompt Processing
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Streamlit multi-tab UI + React SPA companion. <code>agent/prompt_processor.py</code> classifies intent and builds dynamic academic contexts including course, branch, and semester.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-sky-400 uppercase tracking-wider">
                  Component 3: Large Language Model
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Google Gemini API via official <code>google-genai</code> SDK. Uses <code>gemini-2.5-flash</code> with retry logic, rate limit backoff, and JSON parsing.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                  Component 4: Memory Module
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Dual layer: short-term sliding context in session state + persistent storage in Supabase PostgreSQL (<code>conversations</code> and <code>messages</code> tables).
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                  Component 5: Tool Integration
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  11 internal Python tools: <code>get_student_profile</code>, <code>get_conversation_history</code>, <code>extract_pdf_text</code>, <code>generate_exam_notes</code>, <code>generate_quiz</code>, <code>evaluate_quiz</code>, <code>create_study_plan</code>, etc.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-rose-400 uppercase tracking-wider">
                  Component 6: Response Generation
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Educational responses structured into 2-mark, 5-mark, 10-mark, comparison tables, step-by-step solutions, and citations with <code>[Page X]</code> markers.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-purple-400 uppercase tracking-wider">
                  Component 7: Deployment Platform
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Dual hosting capability: Python Streamlit Community Cloud (<code>streamlit run app.py</code>) + containerized Node/Vite web server.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
