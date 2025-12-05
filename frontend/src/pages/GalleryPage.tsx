import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Calendar, Tag, ChevronLeft, ChevronRight } from 'lucide-react';

interface Site {
    id: string;
    product_type: string;
    design_style: string;
    created_at: string;
    html_content?: string;
}

const ITEMS_PER_PAGE = 8;

const GalleryPage: React.FC = () => {
    const [sites, setSites] = useState<Site[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchSites = async () => {
            try {
                const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const res = await fetch(`${API_URL}/gallery`);
                if (res.ok) {
                    const data = await res.json();
                    setSites(data);
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchSites();
    }, []);

    const totalPages = Math.ceil(sites.length / ITEMS_PER_PAGE);
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const currentSites = sites.slice(startIndex, endIndex);

    const goToPage = (page: number) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1.5rem 2rem',
                borderBottom: '1px solid #e5e5e5',
                backgroundColor: 'white',
                zIndex: 10
            }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: '800', margin: 0, letterSpacing: '-0.03em' }}>갤러리</h1>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#6b7280' }}>
                        생성된 사이트 {sites.length}개
                    </p>
                </div>
                <button
                    onClick={() => navigate('/')}
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
                    <Plus size={18} />
                    새로 만들기
                </button>
            </div>

            <div style={{ flex: 1, overflow: 'auto', padding: '2rem' }}>
                {loading ? (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '60vh',
                        fontSize: '1rem',
                        color: '#6b7280'
                    }}>
                        로딩 중...
                    </div>
                ) : sites.length === 0 ? (
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '60vh',
                        textAlign: 'center'
                    }}>
                        <div style={{
                            width: '80px',
                            height: '80px',
                            borderRadius: '50%',
                            backgroundColor: '#f3f4f6',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            marginBottom: '1.5rem'
                        }}>
                            <Plus size={40} color="#9ca3af" />
                        </div>
                        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: '0 0 0.5rem 0', color: '#111827' }}>
                            아직 생성된 사이트가 없습니다
                        </h2>
                        <p style={{ margin: '0 0 2rem 0', color: '#6b7280', fontSize: '0.875rem' }}>
                            첫 번째 사이트를 만들어보세요!
                        </p>
                        <button
                            onClick={() => navigate('/')}
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
                            <Plus size={18} />
                            시작하기
                        </button>
                    </div>
                ) : (
                    <>
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                            gap: '1.5rem',
                            maxWidth: '1400px',
                            margin: '0 auto',
                            marginBottom: '2rem'
                        }}>
                            {currentSites.map(site => (
                                <div
                                    key={site.id}
                                    onClick={() => navigate(`/result/${site.id}`)}
                                    style={{
                                        backgroundColor: 'white',
                                        borderRadius: '12px',
                                        border: '1px solid #e5e5e5',
                                        cursor: 'pointer',
                                        overflow: 'hidden',
                                        transition: 'all 0.2s ease',
                                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                                        position: 'relative',
                                        isolation: 'isolate'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.transform = 'translateY(-4px)';
                                        e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = 'translateY(0)';
                                        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
                                    }}
                                >
                                    {/* Thumbnail Preview - iframe */}
                                    <div style={{
                                        height: '200px',
                                        backgroundColor: 'white',
                                        borderBottom: '1px solid #e5e5e5',
                                        position: 'relative',
                                        overflow: 'hidden'
                                    }}>
                                        {site.html_content ? (
                                            <div style={{
                                                width: '312.5%', // 100% / 0.32
                                                height: '312.5%',
                                                transform: 'scale(0.32)',
                                                transformOrigin: 'top left',
                                                position: 'absolute',
                                                top: 0,
                                                left: 0,
                                                pointerEvents: 'none',
                                                overflow: 'hidden',
                                                backgroundColor: 'white'
                                            }}>
                                                <iframe
                                                    srcDoc={site.html_content}
                                                    title={`Preview of ${site.product_type}`}
                                                    style={{
                                                        width: '100%',
                                                        height: '100%',
                                                        border: 'none',
                                                        backgroundColor: 'white',
                                                        display: 'block'
                                                    }}
                                                    loading="lazy"
                                                />
                                            </div>
                                        ) : (
                                            <div style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                height: '100%',
                                                backgroundColor: 'white'
                                            }}>
                                                <p style={{
                                                    fontSize: '0.875rem',
                                                    color: '#9ca3af',
                                                    margin: 0
                                                }}>미리보기 없음</p>
                                            </div>
                                        )}
                                    </div>

                                    {/* Info Section */}
                                    <div style={{ padding: '1.25rem' }}>
                                        <h3 style={{
                                            fontSize: '1.125rem',
                                            fontWeight: '600',
                                            margin: '0 0 0.5rem 0',
                                            color: '#111827',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap'
                                        }}>
                                            {site.product_type}
                                        </h3>

                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.375rem',
                                            marginBottom: '0.75rem'
                                        }}>
                                            <Tag size={14} color="#9ca3af" />
                                            <p style={{
                                                fontSize: '0.875rem',
                                                color: '#6b7280',
                                                margin: 0,
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap'
                                            }}>
                                                {site.design_style}
                                            </p>
                                        </div>

                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.375rem',
                                            paddingTop: '0.75rem',
                                            borderTop: '1px solid #f3f4f6'
                                        }}>
                                            <Calendar size={14} color="#9ca3af" />
                                            <p style={{
                                                fontSize: '0.75rem',
                                                color: '#9ca3af',
                                                margin: 0
                                            }}>
                                                {new Date(site.created_at).toLocaleDateString('ko-KR', {
                                                    year: 'numeric',
                                                    month: 'long',
                                                    day: 'numeric'
                                                })}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {totalPages > 1 && (
                            <div style={{
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '2rem 0',
                                maxWidth: '1400px',
                                margin: '0 auto'
                            }}>
                                <button
                                    onClick={() => goToPage(currentPage - 1)}
                                    disabled={currentPage === 1}
                                    style={{
                                        padding: '0.5rem',
                                        backgroundColor: currentPage === 1 ? '#f3f4f6' : 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '6px',
                                        cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        opacity: currentPage === 1 ? 0.5 : 1
                                    }}
                                >
                                    <ChevronLeft size={20} />
                                </button>

                                {[...Array(totalPages)].map((_, index) => {
                                    const page = index + 1;
                                    return (
                                        <button
                                            key={page}
                                            onClick={() => goToPage(page)}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                backgroundColor: currentPage === page ? 'black' : 'white',
                                                color: currentPage === page ? 'white' : '#374151',
                                                border: '1px solid #e5e7eb',
                                                borderRadius: '6px',
                                                cursor: 'pointer',
                                                fontSize: '0.875rem',
                                                fontWeight: currentPage === page ? '600' : '400',
                                                minWidth: '40px'
                                            }}
                                        >
                                            {page}
                                        </button>
                                    );
                                })}

                                <button
                                    onClick={() => goToPage(currentPage + 1)}
                                    disabled={currentPage === totalPages}
                                    style={{
                                        padding: '0.5rem',
                                        backgroundColor: currentPage === totalPages ? '#f3f4f6' : 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '6px',
                                        cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        opacity: currentPage === totalPages ? 0.5 : 1
                                    }}
                                >
                                    <ChevronRight size={20} />
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default GalleryPage;
