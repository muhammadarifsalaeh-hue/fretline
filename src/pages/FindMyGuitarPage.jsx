import { useEffect, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import QuizFlow from '@/components/quiz/QuizFlow';
import QuizResults from '@/components/quiz/QuizResults';
import { readAnswers } from '@/utils/quizScoring';

/**
 * /find-my-guitar            → Quiz (intro + คำถามทีละข้อ)
 * /find-my-guitar?type=...   → ผลลัพธ์ (คำตอบอยู่ใน URL จึงแชร์/กด Back ได้)
 */
export default function FindMyGuitarPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const key = params.toString();
  const answers = useMemo(() => readAnswers(new URLSearchParams(key)), [key]);

  useEffect(() => {
    document.title = answers ? 'Your guitar matches — Fretline' : 'Find my guitar — Fretline';
  }, [answers]);

  if (answers) return <QuizResults answers={answers} onRetake={() => navigate('/find-my-guitar')} />;
  return <QuizFlow onFinish={(a) => navigate(`/find-my-guitar?${new URLSearchParams(a).toString()}`)} />;
}
