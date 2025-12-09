import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import InputPage from './pages/InputPage';
import GeneratingPage from './pages/GeneratingPage';
import ResultPage from './pages/ResultPage';
import GalleryPage from './pages/GalleryPage';

import LockOverlay from './components/LockOverlay';

const App: React.FC = () => {
  return (
    <Router>
      <LockOverlay />
      <Routes>
        <Route path="/" element={<InputPage />} />
        <Route path="/generating" element={<GeneratingPage />} />
        <Route path="/result/:id" element={<ResultPage />} />
        <Route path="/gallery" element={<GalleryPage />} />
      </Routes>
    </Router>
  );
};

export default App;
