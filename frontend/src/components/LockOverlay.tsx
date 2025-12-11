import React, { useState, useEffect, useRef } from 'react';

const LockOverlay: React.FC = () => {
    const [isVisible, setIsVisible] = useState(true);
    const [input, setInput] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);
    const SECRET_CODE = '7777';

    useEffect(() => {
        // 컴포넌트가 마운트될 때 입력 필드에 자동으로 포커스
        if (isVisible && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isVisible]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        // 4자리 숫자로만 제한
        if (value.length <= SECRET_CODE.length && /^\d*$/.test(value)) {
            setInput(value);

            // 4자리가 모두 입력되면 비밀번호 체크
            if (value.length === SECRET_CODE.length) {
                if (value === SECRET_CODE) {
                    // 비밀번호 일치 시 오버레이 해제
                    setIsVisible(false);
                } else {
                    // 불일치 시 입력 초기화 (잠시 후)
                    setTimeout(() => {
                        setInput('');
                    }, 300);
                }
            }
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
            flexDirection: 'column', // Input 필드와 제목을 수직으로 배치
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 99999,
        }}>
            <h1 style={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 300,
                fontSize: '2rem',
                letterSpacing: '0.0em',
                color: '#333',
                marginBottom: '20px' // 입력 필드와 간격
            }}>
                E-commerce Generator.
            </h1>
            <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={handleInputChange}
                maxLength={SECRET_CODE.length}
                placeholder=""
                style={{
                    padding: '10px',
                    fontSize: '1.5rem',
                    textAlign: 'center',
                    border: `2px solid ${input.length === SECRET_CODE.length && input !== SECRET_CODE ? 'red' : '#ccc'}`,
                    borderRadius: '5px',
                    width: '200px',
                    outline: 'none'
                }}
            />
        </div>
    );
};

export default LockOverlay;