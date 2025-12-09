import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const GeneratingPage: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const formData = location.state as { productType: string; referenceUrl: string; designStyle: string; generationMode?: string };

    const [status, setStatus] = useState('준비 중...');
    const [elapsedTime, setElapsedTime] = useState(0);

    // Refs for cleanup and state management
    const isMounted = useRef(true);
    const pollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const timerIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        isMounted.current = true;

        if (!formData) {
            navigate('/');
            return;
        }

        // 1. Start Elapsed Timer
        timerIntervalRef.current = setInterval(() => {
            if (isMounted.current) {
                setElapsedTime(prev => prev + 1);
            }
        }, 1000);

        const startGeneration = async () => {
            try {
                if (!isMounted.current) return;
                setStatus('AI가 당신만의 쇼핑몰을 디자인하고 있습니다...');

                const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

                // Initial Generation Request
                const res = await fetch(`${API_URL}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_type: formData.productType,
                        reference_url: formData.referenceUrl || '',
                        design_style: formData.designStyle,
                        generation_mode: formData.generationMode || 'vision',
                    }),
                });

                if (!res.ok) throw new Error('Generation failed');

                const data = await res.json();
                const siteId = data.id;

                if (!isMounted.current) return;
                setStatus('코드를 작성하고 있습니다...');

                // 2. Start Polling (Recursive setTimeout with 3s delay)
                let pollAttempts = 0;
                const maxPollAttempts = 120;

                const poll = async () => {
                    if (!isMounted.current) return;

                    pollAttempts++;
                    if (pollAttempts > maxPollAttempts) {
                        setStatus('시간 초과: 생성에 너무 오래 걸렸습니다.');
                        clearInterval(timerIntervalRef.current!);
                        return;
                    }

                    try {
                        const resultRes = await fetch(`${API_URL}/results/${siteId}`);

                        if (resultRes.ok) {
                            const site = await resultRes.json();
                            if (site.status === 'completed') {
                                setStatus('완성되었습니다!');
                                clearInterval(timerIntervalRef.current!);
                                setTimeout(() => {
                                    if (isMounted.current) navigate(`/result/${siteId}`);
                                }, 800);
                                return; // Stop polling
                            } else if (site.status === 'error') {
                                setStatus('오류가 발생했습니다: ' + site.error_message);
                                clearInterval(timerIntervalRef.current!);
                                return; // Stop polling
                            }
                        }
                    } catch (e) {
                        console.error("Polling error", e);
                    }

                    // Schedule next poll ONLY if not finished
                    // Increased delay to 3000ms to prevent "bombing"
                    if (isMounted.current) {
                        pollTimeoutRef.current = setTimeout(poll, 3000);
                    }
                };

                // Start first poll
                poll();

            } catch (err) {
                if (isMounted.current) {
                    setStatus('생성 중 오류가 발생했습니다. 다시 시도해주세요.');
                    clearInterval(timerIntervalRef.current!);
                }
            }
        };

        startGeneration();

        // Cleanup function
        return () => {
            isMounted.current = false;
            if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
            if (pollTimeoutRef.current) clearTimeout(pollTimeoutRef.current);
        };
    }, [formData, navigate]);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const getWittyMessage = () => {
        if (elapsedTime < 10) return '멋진 디자인을 구상하고 있어요 ✨';
        if (elapsedTime < 30) return '완벽한 색상 조합을 찾는 중이에요 🎨';
        if (elapsedTime < 60) return '레이아웃을 세심하게 배치하고 있어요 📐';
        if (elapsedTime < 90) return '인터랙션을 추가하고 있어요 ⚡';
        if (elapsedTime < 120) return '마지막 손질을 하고 있어요 🔧';
        return '거의 다 됐어요! 조금만 더 기다려주세요 🎉';
    };

    return (
        <div style={{
            width: '100vw',
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'fixed',
            top: 0,
            left: 0,
            backgroundColor: '#fafafa'
        }}>
            <div style={{
                flex: 1,
                overflow: 'auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '2rem'
            }}>
                {/* Animation Wrapper */}
                <div style={{
                    position: 'relative',
                    width: '100%',
                    maxWidth: '500px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                }}>
                    {/* Undulating Glow Layer (꿀렁이는 빛) */}
                    <div style={{
                        position: 'absolute',
                        top: '-20px', left: '-20px', right: '-20px', bottom: '-20px',
                        background: 'linear-gradient(45deg, #ff9a9e, #fad0c4, #ffecd2, #a18cd1, #fbc2eb)',
                        backgroundSize: '300% 300%',
                        borderRadius: '60% 40% 30% 70% / 60% 30% 70% 40%', // Organic shape
                        filter: 'blur(25px)', // Soft glow
                        animation: 'undulate 8s ease-in-out infinite alternate, gradientShift 10s ease infinite',
                        zIndex: 0,
                        opacity: 0.6
                    }}></div>

                    {/* Second Layer for more complexity */}
                    <div style={{
                        position: 'absolute',
                        top: '-15px', left: '-15px', right: '-15px', bottom: '-15px',
                        background: 'linear-gradient(135deg, #84fab0, #8fd3f4, #a1c4fd, #c2e9fb)',
                        backgroundSize: '300% 300%',
                        borderRadius: '30% 70% 70% 30% / 30% 30% 70% 70%',
                        filter: 'blur(20px)',
                        animation: 'undulate 10s ease-in-out infinite alternate-reverse, gradientShift 12s ease infinite',
                        zIndex: 0,
                        opacity: 0.5
                    }}></div>

                    {/* Content Card */}
                    <div style={{
                        position: 'relative',
                        zIndex: 1,
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: '24px',
                        padding: '3rem 2.5rem',
                        textAlign: 'center',
                        boxShadow: '0 10px 40px rgba(0,0,0,0.08)',
                        width: '100%'
                    }}>
                        <h2 style={{
                            fontSize: '1.5rem',
                            fontWeight: '700',
                            margin: '0 0 1rem 0',
                            color: '#111827'
                        }}>
                            {status}
                        </h2>

                        <p style={{
                            fontSize: '0.875rem',
                            color: '#6b7280',
                            margin: '0 0 2rem 0',
                            lineHeight: '1.6'
                        }}>
                            {getWittyMessage()}
                        </p>

                        <div style={{
                            display: 'inline-block',
                            padding: '0.5rem 1.5rem',
                            backgroundColor: '#f9fafb',
                            borderRadius: '12px',
                            border: '1px solid #e5e7eb'
                        }}>
                            <p style={{
                                fontSize: '0.875rem',
                                color: '#374151',
                                margin: 0,
                                fontWeight: '600',
                                fontFamily: 'monospace'
                            }}>
                                경과 시간: {formatTime(elapsedTime)}
                            </p>
                        </div>

                        {/* Average Time Notice */}
                        <p style={{
                            fontSize: '0.75rem',
                            color: '#9ca3af',
                            margin: '0.5rem 0 0 0'
                        }}>
                            평균 소요시간: 약 2분 내외이지만..
                            무료 클라우드 서비스라서 좀 더 걸릴지도..
                        </p>

                        <div style={{
                            marginTop: '2rem',
                            padding: '1.5rem',
                            backgroundColor: '#f9fafb',
                            borderRadius: '16px',
                            border: '1px solid #e5e7eb',
                            textAlign: 'left'
                        }}>
                            <div style={{ marginBottom: '0.75rem' }}>
                                <p style={{
                                    fontSize: '0.75rem',
                                    color: '#9ca3af',
                                    margin: '0 0 0.25rem 0',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em'
                                }}>
                                    상품
                                </p>
                                <p style={{
                                    fontSize: '0.875rem',
                                    color: '#111827',
                                    margin: 0,
                                    fontWeight: '600'
                                }}>
                                    {formData?.productType}
                                </p>
                            </div>
                            <div>
                                <p style={{
                                    fontSize: '0.75rem',
                                    color: '#9ca3af',
                                    margin: '0 0 0.25rem 0',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em'
                                }}>
                                    디자인 스타일
                                </p>
                                <p style={{
                                    fontSize: '0.875rem',
                                    color: '#111827',
                                    margin: 0,
                                    fontWeight: '400',
                                    lineHeight: '1.5'
                                }}>
                                    {formData?.designStyle}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                @keyframes undulate {
                    0% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; transform: scale(1); }
                    33% { border-radius: 50% 50% 60% 40% / 50% 60% 30% 60%; transform: scale(1.02); }
                    66% { border-radius: 40% 60% 50% 50% / 40% 40% 60% 50%; transform: scale(0.98); }
                    100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; transform: scale(1); }
                }

                @keyframes gradientShift {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
            `}</style>
        </div>
    );
};

export default GeneratingPage;
