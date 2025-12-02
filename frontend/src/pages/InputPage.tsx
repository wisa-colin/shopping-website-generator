import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Grid, ArrowRight, ArrowLeft } from 'lucide-react';

const InputPage: React.FC = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        productType: '',
        designStyle: '',
        referenceUrl: ''
    });

    const handleNext = () => {
        if (step === 1 && !formData.productType) {
            alert('상품명을 입력해주세요.');
            return;
        }
        if (step === 2 && !formData.designStyle) {
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
                backgroundColor: 'white',
                zIndex: 10
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
                                <div style={{
                                    width: '64px',
                                    height: '64px',
                                    borderRadius: '50%',
                                    backgroundColor: '#f3f4f6',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    margin: '0 auto 1rem auto'
                                }}>
                                    <span style={{ fontSize: '2rem' }}>🛍️</span>
                                </div>
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
                                placeholder="예: 수제 비누, 친환경 화장품, 수공예 가방"
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

                    {/* Step 2 */}
                    {step === 2 && (
                        <div style={{
                            animation: 'fadeIn 0.3s ease-in'
                        }}>
                            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                                <div style={{
                                    width: '64px',
                                    height: '64px',
                                    borderRadius: '50%',
                                    backgroundColor: '#f3f4f6',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    margin: '0 auto 1rem auto'
                                }}>
                                    <span style={{ fontSize: '2rem' }}>🎨</span>
                                </div>
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
                                placeholder="예: 자연스럽고 따뜻한 느낌, 미니멀한 디자인, 레트로 스타일 등"
                                rows={6}
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
                        </div>
                    )}

                    {/* Step 3 */}
                    {step === 3 && (
                        <div style={{
                            animation: 'fadeIn 0.3s ease-in'
                        }}>
                            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                                <div style={{
                                    width: '64px',
                                    height: '64px',
                                    borderRadius: '50%',
                                    backgroundColor: '#f3f4f6',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    margin: '0 auto 1rem auto'
                                }}>
                                    <span style={{ fontSize: '2rem' }}>🔗</span>
                                </div>
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
                                placeholder="https://example.com"
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
                                margin: '1rem 0 0 0',
                                fontSize: '0.75rem',
                                color: '#9ca3af',
                                lineHeight: '1.5',
                                textAlign: 'center'
                            }}>
                                입력하지 않아도 괜찮습니다
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
