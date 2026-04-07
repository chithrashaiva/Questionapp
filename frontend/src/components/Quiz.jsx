import { useState, useEffect } from 'react';

export default function Quiz() {
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedOption, setSelectedOption] = useState(null);
  const [isAnswersDisabled, setIsAnswersDisabled] = useState(false);
  const [score, setScore] = useState(0);
  const [showScore, setShowScore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [correctAnswerStr, setCorrectAnswerStr] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/questions')
      .then(res => res.json())
      .then(data => {
        setQuestions(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching questions: ", err);
        setLoading(false);
      });
  }, []);

  const handleOptionClick = (option) => {
    setSelectedOption(option);
    setIsAnswersDisabled(true);
    
    fetch('http://localhost:8000/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_id: questions[currentIdx].id,
        answer: option
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.correct) {
        setScore(prevScore => prevScore + 1);
        setCorrectAnswerStr(option);
      } else {
        setCorrectAnswerStr(data.correct_answer);
      }
    })
    .catch(err => {
      console.error("Validation error: ", err);
      // Fallback
      setIsAnswersDisabled(false);
      setSelectedOption(null);
    });
  };

  const handleNextBtn = () => {
    setSelectedOption(null);
    setCorrectAnswerStr(null);
    setIsAnswersDisabled(false);
    
    if (currentIdx + 1 < questions.length) {
      setCurrentIdx(currentIdx + 1);
    } else {
      setShowScore(true);
    }
  };

  const restartQuiz = () => {
    setCurrentIdx(0);
    setScore(0);
    setSelectedOption(null);
    setCorrectAnswerStr(null);
    setIsAnswersDisabled(false);
    setShowScore(false);
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loader"></div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="card">
        <h2 style={{ textAlign: 'center' }}>No questions available.</h2>
      </div>
    );
  }

  if (showScore) {
    return (
      <div className="card" style={{ animation: 'slideUp 0.6s ease-out' }}>
        <h1 className="title">Quiz Complete!</h1>
        <div className="score-container">
          <div className="score-circle">
            <span className="score-number">{score}</span>
            <span className="score-label">out of {questions.length}</span>
          </div>
          <p style={{ marginBottom: '2rem', fontSize: '1.2rem', color: 'var(--text-muted)' }}>
            {score === questions.length ? 'Perfect Score! 🏆' : 
             score >= questions.length / 2 ? 'Good Job! 👍' : 'Keep Learning! 📚'}
          </p>
          <button className="btn-primary" onClick={restartQuiz}>
            Play Again
          </button>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIdx];

  return (
    <div className="card" key={currentIdx}>
      <h1 className="title">Tech Quiz</h1>
      
      <div className="question-text">
        {currentIdx + 1}. {currentQ.question}
      </div>

      <div className="options-grid">
        {currentQ.options.map((option, index) => {
          let btnClass = "option-btn";
          
          if (isAnswersDisabled && correctAnswerStr) {
            if (option === correctAnswerStr) {
              btnClass += " correct";
            } else if (option === selectedOption) {
              btnClass += " wrong";
            }
          } else if (option === selectedOption) {
            btnClass += " selected";
          }

          return (
            <button
              key={index}
              className={btnClass}
              onClick={() => handleOptionClick(option)}
              disabled={isAnswersDisabled}
            >
              {option}
            </button>
          );
        })}
      </div>

      <div className="footer">
        <div className="progress-text">
          Question {currentIdx + 1} of {questions.length}
        </div>
        <button 
          className="btn-primary" 
          onClick={handleNextBtn}
          disabled={!selectedOption}
        >
          {currentIdx === questions.length - 1 ? 'Finish' : 'Next'}
        </button>
      </div>
    </div>
  );
}
