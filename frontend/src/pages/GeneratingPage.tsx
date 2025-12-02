import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

const GeneratingPage: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const formData = location.state as { productType: string; referenceUrl: string; designStyle: string };

    const [status, setStatus] = useState('준비 중...');
    const [elapsedTime, setElapsedTime] = useState(0);

    useEffect(() => {
        if (!formData) {
            navigate('/');
            return;
        }

        // Timer
        const timer = setInterval(() => {
            setElapsedTime(prev => prev + 1);
        }, 1000);

        const generate = async () => {
            try {
                setStatus('AI가 당신만의 쇼핑몰을 디자인하고 있습니다...');

                const res = await fetch('http://localhost:8000/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_type: formData.productType,
                        reference_url: formData.referenceUrl || '',
                        design_style: formData.designStyle,
                    }),
                });

                if (!res.ok) throw new Error('Generation failed');

                const data = await res.json();
                const siteId = data.id;

                // Poll for completion
                setStatus('코드를 작성하고 있습니다...');
                const pollInterval = setInterval(async () => {
                    const resultRes = await fetch(`http://localhost:8000/results/${siteId}`);
                    if (resultRes.ok) {
                        const site = await resultRes.json();
                        if (site.status === 'completed') {
                            clearInterval(pollInterval);
                            clearInterval(timer);
                            setStatus('완성되었습니다!');
                            setTimeout(() => navigate(`/result/${siteId}`), 800);
                        } else if (site.status === 'error') {
                            clearInterval(pollInterval);
                            clearInterval(timer);
                            setStatus('오류가 발생했습니다: ' + site.error_message);
                        }
                    }
                }, 2000);

                return () => {
                    clearInterval(pollInterval);
                    clearInterval(timer);
                };
            } catch (err) {
                clearInterval(timer);
                setStatus('생성 중 오류가 발생했습니다. 다시 시도해주세요.');
            }
        };

        generate();

        return () => clearInterval(timer);
    }, [formData, navigate]);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Witty messages based on elapsed time
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
            {/* Top Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1.5rem 2rem',
                borderBottom: '1px solid #e5e5e5',
                backgroundColor: 'white',
                zIndex: 10
            }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: '800', margin: 0, letterSpacing: '-0.03em' }}>
                        생성 중
                    </h1>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#6b7280' }}>
                        평균 소요시간: 약 2분 내외
                    </p>
                </div>
            </div>

            {/* Main Content Area */}
            <div style={{
                flex: 1,
                overflow: 'auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '2rem'
            }}>
                <div style={{
                    backgroundColor: 'white',
                    borderRadius: '16px',
                    border: '1px solid #e5e5e5',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    maxWidth: '600px',
                    width: '100%',
                    padding: '3rem 2.5rem',
                    textAlign: 'center'
                }}>
                    {/* Animated Icon */}
                    <div style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        backgroundColor: '#f3f4f6',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 2rem auto',
                        animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                    }}>
                        <Sparkles size={40} color="#000" />
                    </div>

                    {/* Status */}
                    <h2 style={{
                        fontSize: '1.5rem',
                        fontWeight: '700',
                        margin: '0 0 1rem 0',
                        color: '#111827'
                    }}>
                        {status}
                    </h2>

                    {/* Witty Message */}
                    <p style={{
                        fontSize: '0.875rem',
                        color: '#6b7280',
                        margin: '0 0 2rem 0',
                        lineHeight: '1.6'
                    }}>
                        {getWittyMessage()}
                    </p>

                    {/* Progress Bar */}
                    <div style={{
                        width: '100%',
                        height: '8px',
                        backgroundColor: '#f3f4f6',
                        borderRadius: '4px',
                        overflow: 'hidden',
                        marginBottom: '1.5rem'
                    }}>
                        <div style={{
                            height: '100%',
                            backgroundColor: 'black',
                            width: '100%',
                            animation: 'loading 1.5s ease-in-out infinite'
                        }} />
                    </div>

                    {/* Elapsed Time */}
                    <div style={{
                        display: 'inline-block',
                        padding: '0.5rem 1.5rem',
                        backgroundColor: '#f9fafb',
                        borderRadius: '8px',
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

                    {/* Product Info */}
                    <div style={{
                        marginTop: '2rem',
                        padding: '1.5rem',
                        backgroundColor: '#f9fafb',
                        borderRadius: '8px',
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

            <style>{`
                @keyframes pulse {
                    0%, 100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                    50% {
                        opacity: 0.7;
                        transform: scale(1.05);
                    }
                }

                @keyframes loading {
                    0% {
                        transform: translateX(-100%);
                    }
                    50% {
                        transform: translateX(0%);
                    }
                    100% {
                        transform: translateX(100%);
                    }
                }
            `}</style>
        </div>
    );
};

export default GeneratingPage;
