import React, { useState, useEffect, useRef } from 'react';

const LockOverlay: React.FC = () => {
    const [isVisible, setIsVisible] = useState(true);
    const [input, setInput] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);

    const SECRET_CODE = '7777';
    const CODE_LENGTH = SECRET_CODE.length;

    useEffect(() => {
        // 컴포넌트 마운트 및 가시 상태 시 자동 포커스
        if (isVisible && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isVisible]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;

        // 4자리 숫자로만 제한
        if (value.length <= CODE_LENGTH && /^\d*$/.test(value)) {
            setInput(value);

            // 4자리가 모두 입력되면 비밀번호 체크
            if (value.length === CODE_LENGTH) {
                if (value === SECRET_CODE) {
                    setIsVisible(false); // 비밀번호 일치 시 오버레이 해제
                } else {
                    // 불일치 시 입력 초기화
                    setTimeout(() => {
                        setInput('');
                    }, 1000);
                }
            }
        }
    };

    // 입력 필드의 각 칸에 표시될 값을 계산
    const inputBoxes = Array(CODE_LENGTH).fill('');
    input.split('').forEach((char, index) => {
        inputBoxes[index] = char;
    });
    const handleFocusRestore = () => {
        if (isVisible && inputRef.current) {
            inputRef.current.focus();
        }
    };

    if (!isVisible) return null;

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: '#ffffff',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 99999,
        }}>
            <h1 style={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 300,
                fontSize: '2rem',
                color: '#333',
                marginBottom: '40px'
            }}>

            </h1>

            {/* 실제 입력 필드 (투명하게 숨김) */}
            <input
                ref={inputRef}
                type="tel" // 모바일에서 숫자 키패드 유도
                value={input}
                onChange={handleInputChange}
                maxLength={CODE_LENGTH}
                onBlur={handleFocusRestore}
                style={{
                    position: 'absolute', // 가상 박스 위에 겹치도록 배치
                    opacity: 0,           // 투명하게 숨김
                    width: '250px',       // 가상 박스 전체 너비
                    height: '50px',
                    zIndex: 1,            // 가장 위에 배치하여 이벤트 처리
                    cursor: 'text'
                }}
                autoFocus
            />

            {/* 4개의 가상 입력 박스 (시각적인 요소) */}
            <div style={{ display: 'flex', gap: '10px' }}>
                {inputBoxes.map((char, index) => (
                    <div
                        key={index}
                        style={{
                            width: '50px',
                            height: '50px',
                            lineHeight: '50px',
                            textAlign: 'center',
                            fontSize: '1.5rem',
                            border: `2px solid ${
                                // 4자리 입력 후 실패 시 빨간색 테두리
                                input.length === CODE_LENGTH && input !== SECRET_CODE
                                    ? 'red'
                                    : // 현재 입력 중인 칸에 포커스 효과
                                    index === input.length ? '#333' : '#ccc'
                                }`,
                            borderRadius: '5px',
                            backgroundColor: '#f9f9f9',
                            transition: 'border-color 0.3s'
                        }}
                    >
                        {char}
                    </div>
                ))}
            </div>

            {/* 비밀번호 입력 실패 메시지 (옵션) */}
            {input.length === CODE_LENGTH && input !== SECRET_CODE && (
                <p style={{ color: 'red', marginTop: '10px' }}>Wrong.</p>
            )}
        </div>
    );
};

export default LockOverlay;