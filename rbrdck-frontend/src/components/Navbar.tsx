import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">RBRDCK</Link>
        <div className="space-x-4">
            <Link to="/projects" className='hover:underline'>Projects</Link>
          <Link to="/pull-requests" className="hover:underline">Pull Requests</Link>
          <Link to="/work-in-progress" className="hover:underline">Work in Progress</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;