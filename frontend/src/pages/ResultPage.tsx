import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Monitor, Smartphone, Tablet, Download, ArrowLeft, Info, Palette, X } from 'lucide-react';

interface SiteData {
    id: string;
    html_content: string;
    status: string;
    meta_data: string;
}

const ResultPage: React.FC = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [site, setSite] = useState<SiteData | null>(null);
    // Detect mobile on initial load
    const [device, setDevice] = useState<'mobile' | 'tablet' | 'desktop'>(() => {
        if (typeof window !== 'undefined') {
            return window.innerWidth <= 768 ? 'mobile' : 'desktop';
        }
        return 'desktop';
    });
    const [loading, setLoading] = useState(true);
    const [showInfoModal, setShowInfoModal] = useState(false);
    const [showPaletteModal, setShowPaletteModal] = useState(false);

    useEffect(() => {
        const fetchSite = async () => {
            try {
                const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const res = await fetch(`${API_URL}/results/${id}`);
                if (res.ok) {
                    const data = await res.json();
                    setSite(data);
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchSite();
    }, [id]);

    if (loading) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>로딩 중...</div>;
    if (!site) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>사이트를 찾을 수 없습니다.</div>;

    const meta = JSON.parse(site.meta_data || '{}');
    const { explanation, color_palette, product_type, design_style, reference_url } = meta;

    const getFrameWidth = () => {
        switch (device) {
            case 'mobile': return '375px';
            case 'tablet': return '768px';
            case 'desktop': return '100%';
        }
    };

    const handleDownload = () => {
        if (!site) return;
        const blob = new Blob([site.html_content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `site-${site.id}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    const handleDelete = async () => {
        if (!site) return;

        const confirmed = window.confirm('정말로 이 사이트를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.');
        if (!confirmed) return;

        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/sites/${site.id}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                alert('사이트가 삭제되었습니다.');
                navigate('/gallery');
            } else {
                alert('삭제 중 오류가 발생했습니다.');
            }
        } catch (e) {
            console.error(e);
            alert('삭제 중 오류가 발생했습니다.');
        }
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
            backgroundColor: '#fff'
        }}>
            {/* Top Controls */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '0.75rem 1.5rem',
                borderBottom: '1px solid #e5e5e5',
                backgroundColor: 'white',
                zIndex: 10
            }}>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <button onClick={() => navigate('/gallery')} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: 'black',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px'
                    }}>
                        <ArrowLeft size={16} /> 갤러리
                    </button>
                    <button onClick={() => setShowInfoModal(true)} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#dbeafe',
                        color: '#1d4ed8',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px'
                    }}>
                        <Info size={16} /> 정보
                    </button>
                    <button onClick={() => setShowPaletteModal(true)} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#e9d5ff',
                        color: '#7c3aed',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px'
                    }}>
                        <Palette size={16} /> 컬러
                    </button>
                </div>

                <div style={{ display: 'flex', gap: '0.25rem', backgroundColor: '#f3f4f6', padding: '0.25rem', borderRadius: '8px' }}>
                    <button
                        onClick={() => setDevice('mobile')}
                        style={{
                            padding: '0.5rem',
                            backgroundColor: device === 'mobile' ? 'white' : 'transparent',
                            color: device === 'mobile' ? 'black' : '#6b7280',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            boxShadow: device === 'mobile' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
                        }}
                    >
                        <Smartphone size={18} />
                    </button>
                    <button
                        onClick={() => setDevice('tablet')}
                        style={{
                            padding: '0.5rem',
                            backgroundColor: device === 'tablet' ? 'white' : 'transparent',
                            color: device === 'tablet' ? 'black' : '#6b7280',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            boxShadow: device === 'tablet' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
                        }}
                    >
                        <Tablet size={18} />
                    </button>
                    <button
                        onClick={() => setDevice('desktop')}
                        style={{
                            padding: '0.5rem',
                            backgroundColor: device === 'desktop' ? 'white' : 'transparent',
                            color: device === 'desktop' ? 'black' : '#6b7280',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            boxShadow: device === 'desktop' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
                        }}
                    >
                        <Monitor size={18} />
                    </button>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button onClick={handleDownload} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: 'black',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px'
                    }}>
                        <Download size={16} /> 다운로드
                    </button>

                    <button onClick={handleDelete} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#dc2626',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px'
                    }}>
                        <X size={16} /> 삭제
                    </button>
                </div>
            </div>

            {/* Main Preview - Full Browser Width */}
            <div style={{
                flex: 1,
                backgroundColor: '#f5f5f5',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'flex-start',
                overflow: 'auto',
                padding: device === 'desktop' ? '0' : '2rem 0'
            }}>
                <iframe
                    srcDoc={site.html_content}
                    title="Generated Site"
                    style={{
                        width: getFrameWidth(),
                        height: device === 'desktop' ? '100%' : 'auto',
                        minHeight: device === 'desktop' ? '100%' : '800px',
                        border: 'none',
                        backgroundColor: 'white',
                        boxShadow: device !== 'desktop' ? '0 10px 40px rgba(0,0,0,0.1)' : 'none'
                    }}
                />
            </div>

            {/* Info Modal */}
            {showInfoModal && (
                <div
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0,0,0,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                        padding: '2rem'
                    }}
                    onClick={() => setShowInfoModal(false)}
                >
                    <div
                        style={{
                            backgroundColor: 'white',
                            borderRadius: '16px',
                            maxWidth: '600px',
                            width: '100%',
                            maxHeight: '80vh',
                            overflow: 'auto',
                            padding: '2rem',
                            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>사이트 정보</h2>
                            <button onClick={() => setShowInfoModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0.5rem' }}>
                                <X size={24} />
                            </button>
                        </div>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>상품</h3>
                            <p style={{ fontSize: '1.125rem', fontWeight: '500', margin: 0 }}>{product_type}</p>
                        </div>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>스타일</h3>
                            <p style={{ color: '#374151', margin: 0, lineHeight: '1.6' }}>{design_style}</p>
                        </div>

                        {reference_url && reference_url !== 'None' && reference_url !== '' && (
                            <div style={{ marginBottom: '1.5rem' }}>
                                <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>레퍼런스 URL</h3>
                                <a href={reference_url} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'none', wordBreak: 'break-all', fontSize: '0.875rem' }}>
                                    {reference_url}
                                </a>
                            </div>
                        )}

                        {explanation && (
                            <div style={{ marginBottom: '1.5rem' }}>
                                <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>디자인 의도</h3>
                                <p style={{ color: '#374151', margin: 0, lineHeight: '1.6' }}>{explanation}</p>
                            </div>
                        )}

                        <button
                            onClick={() => setShowInfoModal(false)}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                backgroundColor: 'black',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontSize: '1rem',
                                fontWeight: '500'
                            }}
                        >
                            닫기
                        </button>
                    </div>
                </div>
            )}

            {/* Color Palette Modal */}
            {showPaletteModal && (
                <div
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0,0,0,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                        padding: '2rem'
                    }}
                    onClick={() => setShowPaletteModal(false)}
                >
                    <div
                        style={{
                            backgroundColor: 'white',
                            borderRadius: '16px',
                            maxWidth: '500px',
                            width: '100%',
                            padding: '2rem',
                            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>컬러 팔레트</h2>
                            <button onClick={() => setShowPaletteModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0.5rem' }}>
                                <X size={24} />
                            </button>
                        </div>
                        <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1.5rem' }}>색상을 클릭하면 코드가 복사됩니다</p>

                        {color_palette && color_palette.length > 0 ? (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '1rem' }}>
                                {color_palette.map((color: string, i: number) => (
                                    <div
                                        key={i}
                                        style={{ cursor: 'pointer', textAlign: 'center' }}
                                        onClick={() => {
                                            copyToClipboard(color);
                                            alert(`${color} 복사됨!`);
                                        }}
                                    >
                                        <div
                                            style={{
                                                width: '100%',
                                                height: '100px',
                                                borderRadius: '12px',
                                                border: '2px solid #e5e7eb',
                                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                                backgroundColor: color,
                                                transition: 'transform 0.2s',
                                                marginBottom: '0.5rem'
                                            }}
                                            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                        ></div>
                                        <p style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#374151', margin: 0, fontWeight: '500' }}>{color}</p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
                                <p style={{ margin: 0 }}>컬러 팔레트 정보가 없습니다.</p>
                                <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem' }}>생성된 사이트의 메타데이터에 컬러 정보가 포함되지 않았습니다.</p>
                            </div>
                        )}

                        <button
                            onClick={() => setShowPaletteModal(false)}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                backgroundColor: 'black',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontSize: '1rem',
                                fontWeight: '500',
                                marginTop: '1.5rem'
                            }}
                        >
                            닫기
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResultPage;
