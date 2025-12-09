import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Grid, ArrowRight, ArrowLeft } from 'lucide-react';

const InputPage: React.FC = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [secretModeVisible, setSecretModeVisible] = useState(false);
    const [formData, setFormData] = useState({
        productType: '',
        designStyle: '',
        referenceUrl: '',
        generationMode: 'hybrid' // Default to hybrid
    });

    // Secret mode shortcut listener
    React.useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.altKey && e.shiftKey && (e.key === 'j' || e.key === 'J')) {
                setSecretModeVisible(prev => !prev);
                console.log("Secret mode toggled");
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const handleNext = () => {
        if (step === 1 && !formData.productType) {
            alert('상품명을 입력해주세요.');
            return;
        }
        // Step 2 is now reference URL (optional, no validation)
        // Step 3 is now design style (required)
        if (step === 3 && !formData.designStyle) {
            alert('디자인 스타일을 입력해주세요.');
            return;
        }
        if (step < 3) {
            setStep(step + 1);
        } else {
            handleSubmit();
        }
    };

    const handleSubmit = () => {
        navigate('/generating', { state: formData });
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
                backgroundColor: 'white'
            }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: '800', margin: 0, letterSpacing: '-0.03em' }}>
                        쇼핑몰 사이트 생성기
                    </h1>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#6b7280' }}>
                        단계 {step} / 3
                    </p>
                </div>

                <button
                    onClick={() => navigate('/gallery')}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.75rem 1.5rem',
                        backgroundColor: 'black',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        fontWeight: '600'
                    }}
                >
                    <Grid size={18} />
                    갤러리
                </button>
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
                    padding: '2.5rem'
                }}>
                    {/* Progress bar */}
                    <div style={{ marginBottom: '2rem' }}>
                        <div style={{
                            display: 'flex',
                            gap: '0.5rem',
                            marginBottom: '0.5rem'
                        }}>
                            {[1, 2, 3].map(i => (
                                <div key={i} style={{
                                    flex: 1,
                                    height: '4px',
                                    borderRadius: '2px',
                                    backgroundColor: i <= step ? 'black' : '#e5e7eb',
                                    transition: 'background-color 0.3s'
                                }} />
                            ))}
                        </div>
                    </div>

                    {/* Step 1 */}
                    {step === 1 && (
                        <div style={{
                            animation: 'fadeIn 0.3s ease-in'
                        }}>
                            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '700', margin: '0 0 0.5rem 0', color: '#111827' }}>
                                    어떤 상품을 판매하시나요?
                                </h2>
                                <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                                    판매하실 상품의 이름을 입력해주세요
                                </p>
                            </div>

                            <input
                                type="text"
                                value={formData.productType}
                                onChange={(e) => setFormData({ ...formData, productType: e.target.value })}
                                placeholder="예: 천연 재료로 만든 수제 비누"
                                autoFocus
                                onKeyPress={(e) => e.key === 'Enter' && handleNext()}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '8px',
                                    fontSize: '1rem',
                                    outline: 'none',
                                    transition: 'all 0.2s',
                                    backgroundColor: 'white'
                                }}
                                onFocus={(e) => {
                                    e.target.style.borderColor = '#000';
                                }}
                                onBlur={(e) => {
                                    e.target.style.borderColor = '#e5e7eb';
                                }}
                            />
                        </div>
                    )}

                    {/* Step 2 - Reference URL */}
                    {step === 2 && (
                        <div style={{
                            animation: 'fadeIn 0.3s ease-in'
                        }}>
                            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '700', margin: '0 0 0.5rem 0', color: '#111827' }}>
                                    레퍼런스가 있나요?
                                </h2>
                                <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                                    참고하고 싶은 웹사이트 URL (선택사항)
                                </p>
                            </div>

                            <input
                                type="url"
                                value={formData.referenceUrl}
                                onChange={(e) => setFormData({ ...formData, referenceUrl: e.target.value })}
                                placeholder="예: https://www.example-shop.com"
                                autoFocus
                                onKeyPress={(e) => e.key === 'Enter' && handleNext()}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '8px',
                                    fontSize: '1rem',
                                    outline: 'none',
                                    transition: 'all 0.2s',
                                    backgroundColor: 'white'
                                }}
                                onFocus={(e) => {
                                    e.target.style.borderColor = '#000';
                                }}
                                onBlur={(e) => {
                                    e.target.style.borderColor = '#e5e7eb';
                                }}
                            />
                            <p style={{
                                margin: '1rem 0 1.5rem 0',
                                fontSize: '0.75rem',
                                color: '#9ca3af',
                                lineHeight: '1.5',
                                textAlign: 'center'
                            }}>
                                입력하지 않아도 괜찮습니다
                            </p>

                            {/* Analysis Mode Selection (Secret) */}
                            {secretModeVisible && (
                                <div style={{
                                    borderTop: '1px solid #f3f4f6',
                                    paddingTop: '1.5rem',
                                    marginTop: '1.5rem',
                                    animation: 'fadeIn 0.3s ease-in'
                                }}>
                                    <label style={{
                                        display: 'block',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: '#ef4444', // Red color to indicate advanced/secret
                                        marginBottom: '0.5rem'
                                    }}>
                                        🕵️ [SECRET] Generation Mode
                                    </label>
                                    <select
                                        value={formData.generationMode || 'hybrid'}
                                        onChange={(e) => setFormData({ ...formData, generationMode: e.target.value })}
                                        style={{
                                            width: '100%',
                                            padding: '0.75rem',
                                            border: '1px solid #ef4444',
                                            borderRadius: '8px',
                                            fontSize: '0.875rem',
                                            backgroundColor: '#fef2f2',
                                            outline: 'none',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        <option value="hybrid">Hybrid (Vision + URL Context)</option>
                                        <option value="vision">Vision Only</option>
                                        <option value="url_context">URL Context Only</option>
                                        <option value="html">HTML Parsing Only</option>
                                    </select>
                                    <p style={{
                                        fontSize: '0.75rem',
                                        color: '#ef4444',
                                        marginTop: '0.5rem',
                                        fontWeight: 500
                                    }}>
                                        * 개발자 전용 모드
                                    </p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Step 3 - Design Style */}
                    {step === 3 && (
                        <div style={{
                            animation: 'fadeIn 0.3s ease-in'
                        }}>
                            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '700', margin: '0 0 0.5rem 0', color: '#111827' }}>
                                    어떤 디자인을 원하시나요?
                                </h2>
                                <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                                    원하는 디자인 스타일이나 느낌을 설명해주세요
                                </p>
                            </div>

                            <textarea
                                value={formData.designStyle}
                                onChange={(e) => setFormData({ ...formData, designStyle: e.target.value })}
                                placeholder="예: 전체적으로 자연스러운 베이지 톤으로 따뜻한 느낌을 주고, 상품 이미지가 돋보이도록 깔끔한 레이아웃을 원합니다. 모바일에서도 쉽게 탐색할 수 있으면 좋겠습니다."
                                rows={6}
                                maxLength={1000}
                                autoFocus
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '8px',
                                    fontSize: '1rem',
                                    outline: 'none',
                                    transition: 'all 0.2s',
                                    backgroundColor: 'white',
                                    resize: 'vertical',
                                    fontFamily: 'inherit'
                                }}
                                onFocus={(e) => {
                                    e.target.style.borderColor = '#000';
                                }}
                                onBlur={(e) => {
                                    e.target.style.borderColor = '#e5e7eb';
                                }}
                            />
                            <p style={{
                                margin: '0.5rem 0 0 0',
                                fontSize: '0.75rem',
                                color: formData.designStyle.length > 900 ? '#ef4444' : '#9ca3af',
                                textAlign: 'right',
                                fontWeight: formData.designStyle.length > 900 ? '600' : '400'
                            }}>
                                {formData.designStyle.length} / 1000자
                            </p>
                        </div>
                    )}

                    {/* Navigation Buttons */}
                    <div style={{
                        display: 'flex',
                        gap: '1rem',
                        marginTop: '2rem'
                    }}>
                        {step > 1 && (
                            <button
                                onClick={() => setStep(step - 1)}
                                style={{
                                    flex: 1,
                                    padding: '1rem',
                                    backgroundColor: '#f3f4f6',
                                    color: '#374151',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '1rem',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '0.5rem'
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.backgroundColor = '#e5e7eb';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.backgroundColor = '#f3f4f6';
                                }}
                            >
                                <ArrowLeft size={20} />
                                이전
                            </button>
                        )}
                        <button
                            onClick={handleNext}
                            style={{
                                flex: step === 1 ? 1 : 2,
                                padding: '1rem',
                                backgroundColor: 'black',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                fontSize: '1rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.5rem'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = '#1f2937';
                                e.currentTarget.style.transform = 'translateY(-1px)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = 'black';
                                e.currentTarget.style.transform = 'translateY(0)';
                            }}
                        >
                            {step === 3 ? (
                                <>
                                    <Sparkles size={20} />
                                    생성 시작하기
                                </>
                            ) : (
                                <>
                                    다음
                                    <ArrowRight size={20} />
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            <style>{`
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
};

export default InputPage;
