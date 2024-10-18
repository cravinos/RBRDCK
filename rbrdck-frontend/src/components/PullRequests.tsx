import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface PullRequest {
  id: number;
  title: string;
  number: number;
  html_url: string;
}

const PullRequests: React.FC = () => {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchPullRequests = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/pull-requests');
      setPullRequests(response.data);
    } catch (error) {
      console.error('Error fetching pull requests:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPullRequests();
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Pull Requests</h2>
      {loading ? (
        <p>Loading pull requests...</p>
      ) : (
        <ul className="space-y-4">
          {pullRequests.map((pr) => (
            <li key={pr.id} className="bg-white shadow rounded p-4">
              <a href={pr.html_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                #{pr.number}: {pr.title}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PullRequests;