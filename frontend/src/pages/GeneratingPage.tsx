import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';

const GeneratingPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [status, setStatus] = useState('초기화 중...');
    const [elapsedTime, setElapsedTime] = useState(0);
    const formData = location.state;

    useEffect(() => {
        const timer = setInterval(() => {
            setElapsedTime(prev => prev + 1);
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        if (!formData) {
            navigate('/');
            return;
        }

        const startGeneration = async () => {
            try {
                setStatus('사이트 생성을 시작합니다...');
                const response = await fetch('http://localhost:8000/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_type: formData.productType,
                        reference_url: formData.referenceUrl,
                        design_style: formData.designStyle
                    })
                });

                const data = await response.json();
                const siteId = data.id;

                setStatus('사이트를 제작 중입니다...');

                // Poll for result
                const interval = setInterval(async () => {
                    try {
                        const res = await fetch(`http://localhost:8000/results/${siteId}`);
                        if (res.ok) {
                            const siteData = await res.json();

                            if (siteData.status === 'completed') {
                                clearInterval(interval);
                                navigate(`/result/${siteId}`);
                            } else if (siteData.status === 'error') {
                                clearInterval(interval);
                                throw new Error(siteData.error_message || 'Unknown error from server');
                            }
                            // If pending, continue polling
                        }
                    } catch (e: any) {
                        console.error("Polling Error:", e);
                        clearInterval(interval);
                        setStatus(`오류 발생: ${e.message}`);
                    }
                }, 2000);

            } catch (e: any) {
                console.error("Generation Error:", e);
                let errorMessage = '생성 시작 중 오류가 발생했습니다.';
                if (e.message) {
                    errorMessage += ` (${e.message})`;
                }
                setStatus(errorMessage + ' 백엔드 서버가 켜져 있는지 확인해주세요.');
            }
        };

        startGeneration();
    }, [formData, navigate]);

    return (
        <Layout>
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="w-full max-w-md text-center">
                    <h1 className="text-2xl mb-2 font-bold">{status}</h1>
                    <p className="text-gray-500 mb-8">진행 시간: {elapsedTime}초</p>

                    <div className="loading-bar w-full mb-8"></div>

                    <div className="p-6 bg-gray-50 rounded-lg border border-gray-200 text-left text-sm text-gray-600">
                        <p className="mb-2">💡 <strong>알고 계셨나요?</strong></p>
                        <p>AI가 복잡한 디자인 요구사항도 이해하고 반영하여 사이트를 생성합니다.</p>
                        <p className="mt-2 text-xs text-gray-400">평균 소요 시간: 약 30~60초</p>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default GeneratingPage;
