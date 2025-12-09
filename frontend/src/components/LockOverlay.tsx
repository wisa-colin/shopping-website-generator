import React, { useState, useEffect } from 'react';

const LockOverlay: React.FC = () => {
    const [isVisible, setIsVisible] = useState(true);
    const [keystrokes, setKeystrokes] = useState<string[]>([]);
    const SECRET_CODE = ['w', 'o', 'n'];
    // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/naming-convention
    const _keystrokesAlias = keystrokes;
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!isVisible) return;

            // Block input to underlying elements
            e.preventDefault();
            e.stopPropagation();

            setKeystrokes(prev => {
                const newKeys = [...prev, e.key.toLowerCase()];
                // Keep only the last N keys needed for the code
                if (newKeys.length > SECRET_CODE.length) {
                    newKeys.shift();
                }

                // Check pattern
                if (newKeys.join('') === SECRET_CODE.join('')) {
                    setIsVisible(false);
                }
                return newKeys;
            });
        };

        // Use 'capture' phase to intercept events before bubble
        window.addEventListener('keydown', handleKeyDown, true);
        return () => window.removeEventListener('keydown', handleKeyDown, true);
    }, [isVisible]);

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
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 99999, // Highest priority
            cursor: 'none' // Hide cursor for cleaner look
        }}>
            <h1 style={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 300,
                fontSize: '2rem',
                letterSpacing: '0.2em',
                color: '#333'
            }}>
                E-commerce Generator.
            </h1>
        </div>
    );
};

export default LockOverlay;
