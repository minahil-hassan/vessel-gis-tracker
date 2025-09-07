// frontend/src/App.js
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import TrajectoryPage from './components/TrajectoryPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Root path shows your normal layout/map */}
        <Route path="/" element={<AppLayout />} />
        {/* Trajectory page for the new tab */}
       <Route path="/trajectory" element={<TrajectoryPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;






