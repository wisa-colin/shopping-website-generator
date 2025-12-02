import React, { useEffect, useRef, useState, useCallback } from 'react';

const Tetris: React.FC = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [score, setScore] = useState(0);
    const [gameOver, setGameOver] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);

    // Game constants
    const COLS = 10;
    const ROWS = 20;
    const BLOCK_SIZE = 20;
    const COLORS = ['#000000', '#333333', '#666666', '#999999'];

    // Use refs for mutable state to avoid closure staleness in event listeners
    const boardRef = useRef(Array.from({ length: ROWS }, () => Array(COLS).fill(0)));
    const pieceRef = useRef<any>(null);
    const requestRef = useRef<number | null>(null);
    const lastTimeRef = useRef<number>(0);
    const dropCounterRef = useRef<number>(0);
    const dropInterval = 1000; // 1 second drop speed

    const SHAPES = [
        [[1, 1, 1, 1]], // I
        [[1, 1], [1, 1]], // O
        [[1, 1, 1], [0, 1, 0]], // T
        [[1, 1, 1], [1, 0, 0]], // L
        [[1, 1, 1], [0, 0, 1]], // J
        [[1, 1, 0], [0, 1, 1]], // S
        [[0, 1, 1], [1, 1, 0]]  // Z
    ];

    const createPiece = () => {
        const shape = SHAPES[Math.floor(Math.random() * SHAPES.length)];
        const color = COLORS[Math.floor(Math.random() * COLORS.length)];
        return {
            shape,
            color,
            x: Math.floor(COLS / 2) - Math.floor(shape[0].length / 2),
            y: 0
        };
    };

    const isValidMove = (x: number, y: number, shape: any) => {
        return shape.every((row: any, dy: number) => {
            return row.every((cell: any, dx: number) => {
                if (!cell) return true;
                const newX = x + dx;
                const newY = y + dy;
                return (
                    newX >= 0 &&
                    newX < COLS &&
                    newY < ROWS &&
                    (newY < 0 || boardRef.current[newY][newX] === 0)
                );
            });
        });
    };

    const placePiece = () => {
        const piece = pieceRef.current;
        if (!piece) return;

        piece.shape.forEach((row: any, dy: number) => {
            row.forEach((cell: any, dx: number) => {
                if (cell) {
                    const newY = piece.y + dy;
                    const newX = piece.x + dx;
                    if (newY >= 0 && newY < ROWS) {
                        boardRef.current[newY][newX] = piece.color;
                    } else {
                        setGameOver(true);
                        setIsPlaying(false);
                    }
                }
            });
        });

        // Clear lines
        let linesCleared = 0;
        for (let y = ROWS - 1; y >= 0; y--) {
            if (boardRef.current[y].every((cell: any) => cell !== 0)) {
                boardRef.current.splice(y, 1);
                boardRef.current.unshift(Array(COLS).fill(0));
                linesCleared++;
                y++;
            }
        }

        if (linesCleared > 0) {
            setScore(s => s + linesCleared * 100);
        }

        pieceRef.current = createPiece();
        // Check if new piece can be placed
        if (!isValidMove(pieceRef.current.x, pieceRef.current.y, pieceRef.current.shape)) {
            setGameOver(true);
            setIsPlaying(false);
        }
    };

    const update = (time: number) => {
        if (!isPlaying || gameOver) return;

        const deltaTime = time - lastTimeRef.current;
        lastTimeRef.current = time;

        dropCounterRef.current += deltaTime;
        if (dropCounterRef.current > dropInterval) {
            if (pieceRef.current) {
                if (isValidMove(pieceRef.current.x, pieceRef.current.y + 1, pieceRef.current.shape)) {
                    pieceRef.current.y++;
                } else {
                    placePiece();
                }
            }
            dropCounterRef.current = 0;
        }

        draw();
        requestRef.current = requestAnimationFrame(update);
    };

    const draw = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw Board
        boardRef.current.forEach((row: any, y: number) => {
            row.forEach((cell: any, x: number) => {
                if (cell) {
                    ctx.fillStyle = cell;
                    ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1);
                }
            });
        });

        // Draw Current Piece
        if (pieceRef.current) {
            ctx.fillStyle = pieceRef.current.color;
            pieceRef.current.shape.forEach((row: any, dy: number) => {
                row.forEach((cell: any, dx: number) => {
                    if (cell) {
                        ctx.fillRect(
                            (pieceRef.current.x + dx) * BLOCK_SIZE,
                            (pieceRef.current.y + dy) * BLOCK_SIZE,
                            BLOCK_SIZE - 1,
                            BLOCK_SIZE - 1
                        );
                    }
                });
            });
        }
    };

    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        if (!isPlaying || gameOver || !pieceRef.current) return;

        const piece = pieceRef.current;

        if (e.key === 'ArrowLeft') {
            if (isValidMove(piece.x - 1, piece.y, piece.shape)) {
                piece.x--;
            }
        } else if (e.key === 'ArrowRight') {
            if (isValidMove(piece.x + 1, piece.y, piece.shape)) {
                piece.x++;
            }
        } else if (e.key === 'ArrowDown') {
            if (isValidMove(piece.x, piece.y + 1, piece.shape)) {
                piece.y++;
                dropCounterRef.current = 0; // Reset drop timer on manual drop
            }
        } else if (e.key === 'ArrowUp') {
            const rotated = piece.shape[0].map((_: any, i: number) =>
                piece.shape.map((row: any) => row[i]).reverse()
            );
            if (isValidMove(piece.x, piece.y, rotated)) {
                piece.shape = rotated;
            }
        }
        draw();
    }, [isPlaying, gameOver]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    const startGame = () => {
        boardRef.current = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
        pieceRef.current = createPiece();
        setScore(0);
        setGameOver(false);
        setIsPlaying(true);
        lastTimeRef.current = performance.now();
        dropCounterRef.current = 0;
        // Start the game loop
        requestRef.current = requestAnimationFrame(update);
    };

    useEffect(() => {
        if (isPlaying) {
            // Ensure the loop starts if isPlaying becomes true
            // and cancel any existing loop if it was already running
            if (requestRef.current) cancelAnimationFrame(requestRef.current);
            requestRef.current = requestAnimationFrame(update);
        }
        return () => {
            if (requestRef.current) cancelAnimationFrame(requestRef.current);
        };
    }, [isPlaying]); // Re-run effect when isPlaying changes

    return (
        <div className="text-center">
            <div className="mb-2 font-bold">점수: {score}</div>
            <canvas
                ref={canvasRef}
                width={COLS * BLOCK_SIZE}
                height={ROWS * BLOCK_SIZE}
                className="border-4 border-black bg-white mx-auto"
            />
            <div className="mt-4">
                {!isPlaying && (
                    <button onClick={startGame} className="text-xs px-4 py-2">
                        {gameOver ? '다시 시작' : '게임 시작'}
                    </button>
                )}
            </div>
            <p className="mt-2 text-xs text-gray-500">방향키로 조작하세요</p>
        </div>
    );
};

export default Tetris;
