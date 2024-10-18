import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

interface PullRequest {
  number: number;
  title: string;
}

interface RepoPullRequests {
  repo_name: string;
  pull_requests: PullRequest[];
}

interface Organization {
  org_name: string;
  org_url: string;
}

const PullRequests = () => {
  const [prs, setPrs] = useState<PullRequest[]>([]);
  const [repoPrs, setRepoPrs] = useState<RepoPullRequests[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedPr, setSelectedPr] = useState<number | null>(null);
  const [review, setReview] = useState('');
  const [diff, setDiff] = useState('');
  const [cliOutput, setCliOutput] = useState<string | null>(null);
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null);

  // Fetch open PRs for the main repository
  useEffect(() => {
    axios.get('http://localhost:8000/open_prs')
      .then(response => setPrs(response.data))
      .catch(error => console.error('Error fetching PRs:', error));
  }, []);

  // Fetch open PRs for all repositories of REPO_USER
  useEffect(() => {
    if (selectedOrg) {
      // Fetch pull requests for the selected organization
      axios.get(`http://localhost:8000/org_pull_requests/${selectedOrg}`)
        .then(response => setRepoPrs(response.data.repo_prs))
        .catch(error => console.error('Error fetching organization PRs:', error));
    } else {
      axios.get('http://localhost:8000/repo_pull_requests')
        .then(response => setRepoPrs(response.data.repo_prs))
        .catch(error => console.error('Error fetching repository PRs:', error));
    }
  }, [selectedOrg]);

  // Fetch the organizations and teams the user is part of
  useEffect(() => {
    axios.get('http://localhost:8000/user_groups')
      .then(response => setOrganizations(response.data.organizations))
      .catch(error => console.error('Error fetching organizations:', error));
  }, []);

  // Fetch review and diff for selected PR
  useEffect(() => {
    if (selectedPr !== null) {
      axios.get(`http://localhost:8000/review_pr/${selectedPr}`)
        .then(response => {
          setReview(response.data.review);
          setDiff(response.data.diff); // Assuming diff is returned
        })
        .catch(error => console.error('Error fetching review:', error));
    }
  }, [selectedPr]);

  // Function to trigger the CLI command for reviewing a PR
  const runCliReview = (prNumber: number) => {
    axios.post(`http://localhost:8000/run_cli_review/${prNumber}`)
      .then(response => setCliOutput(response.data.output))
      .catch(error => {
        console.error('Error running CLI review:', error);
        setCliOutput('Failed to run review');
      });
  };

  return (
    <div>
      <h1>Open Pull Requests</h1>
      
      <div style={{ display: 'flex' }}>
        {/* Column for Organizations/Groups */}
        <div style={{ width: '20%', marginRight: '20px' }}>
          <h2>Organizations & Teams</h2>
          <ul>
            {organizations.map(org => (
              <li key={org.org_name}>
                <button onClick={() => setSelectedOrg(org.org_name)}>
                  {org.org_name}
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Column for Pull Requests */}
        <div style={{ width: '80%' }}>
          <ul>
            {prs.map(pr => (
              <li key={pr.number}>
                <button onClick={() => setSelectedPr(pr.number)}>
                  PR #{pr.number}: {pr.title}
                </button>
                <button onClick={() => runCliReview(pr.number)} style={{ marginLeft: '10px' }}>
                  Run CLI Review
                </button>
              </li>
            ))}
          </ul>

          {selectedPr && (
            <>
              <h2>Review for PR #{selectedPr}</h2>
              <p>{review}</p>

              <h2>Diff for PR #{selectedPr}</h2>
              <SyntaxHighlighter language="diff" style={docco}>
                {diff}
              </SyntaxHighlighter>
            </>
          )}

          {cliOutput && (
            <div>
              <h2>CLI Output</h2>
              <pre>{cliOutput}</pre>
            </div>
          )}

          <h2>Pull Requests from All Repositories</h2>
          {repoPrs.map(repo => (
            <div key={repo.repo_name}>
              <h3>{repo.repo_name}</h3>
              <ul>
                {repo.pull_requests.map(pr => (
                  <li key={pr.number}>
                    PR #{pr.number}: {pr.title}
                    <button onClick={() => runCliReview(pr.number)} style={{ marginLeft: '10px' }}>
                      Run CLI Review
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PullRequests;
