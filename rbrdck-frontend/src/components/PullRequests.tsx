import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import { Button } from './ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card'
import { ScrollArea } from './ui/ScrollArea'

interface PullRequest {
  number: number
  title: string
}

interface RepoPullRequests {
  repo_name: string
  pull_requests: PullRequest[]
}

interface Organization {
  org_name: string
  org_url: string
}

export default function PullRequests() {
  const [prs, setPrs] = useState<PullRequest[]>([])
  const [repoPrs, setRepoPrs] = useState<RepoPullRequests[]>([])
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [selectedPr, setSelectedPr] = useState<number | null>(null)
  const [review, setReview] = useState('')
  const [diff, setDiff] = useState('')
  const [cliOutput, setCliOutput] = useState<string | null>(null)
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null)

  useEffect(() => {
    axios.get('http://localhost:8000/open_prs')
      .then(response => setPrs(response.data))
      .catch(error => console.error('Error fetching PRs:', error))
  }, [])

  useEffect(() => {
    if (selectedOrg) {
      axios.get(`http://localhost:8000/org_pull_requests/${selectedOrg}`)
        .then(response => setRepoPrs(response.data.repo_prs))
        .catch(error => console.error('Error fetching organization PRs:', error))
    } else {
      axios.get('http://localhost:8000/repo_pull_requests')
        .then(response => setRepoPrs(response.data.repo_prs))
        .catch(error => console.error('Error fetching repository PRs:', error))
    }
  }, [selectedOrg])

  useEffect(() => {
    axios.get('http://localhost:8000/user_groups')
      .then(response => setOrganizations(response.data.organizations))
      .catch(error => console.error('Error fetching organizations:', error))
  }, [])

  useEffect(() => {
    if (selectedPr !== null) {
      axios.get(`http://localhost:8000/review_pr/${selectedPr}`)
        .then(response => {
          setReview(response.data.review)
          setDiff(response.data.diff)
        })
        .catch(error => console.error('Error fetching review:', error))
    }
  }, [selectedPr])

  const runCliReview = (prNumber: number) => {
    axios.post(`http://localhost:8000/run_cli_review/${prNumber}`)
      .then(response => setCliOutput(response.data.output))
      .catch(error => {
        console.error('Error running CLI review:', error)
        setCliOutput('Failed to run review')
      })
  }

  return (
    <div className="container mx-auto p-6 bg-background">
      <h1 className="text-3xl font-bold mb-6">Open Pull Requests</h1>
      <div className="flex gap-6">
        <Card className="w-1/4">
          <CardHeader>
            <CardTitle>Organizations & Teams</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              {organizations.map(org => (
                <Button
                  key={org.org_name}
                  className="w-full mb-2 bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={() => setSelectedOrg(org.org_name)}
                >
                  {org.org_name}
                </Button>
              ))}
            </ScrollArea>
          </CardContent>
        </Card>

        <div className="w-3/4 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Pull Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                {prs.map(pr => (
                  <div key={pr.number} className="flex items-center mb-2">
                    <Button
                      className="mr-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
                      onClick={() => setSelectedPr(pr.number)}
                    >
                      PR #{pr.number}: {pr.title}
                    </Button>
                    <Button
                      className="bg-primary text-primary-foreground hover:bg-primary/90"
                      onClick={() => runCliReview(pr.number)}
                    >
                      Run CLI Review
                    </Button>
                  </div>
                ))}
              </ScrollArea>
            </CardContent>
          </Card>

          {selectedPr && (
            <Card>
              <CardHeader>
                <CardTitle>Review for PR #{selectedPr}</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{review}</p>
                <h3 className="text-lg font-semibold mt-4 mb-2">Diff</h3>
                <SyntaxHighlighter language="diff" style={docco}>
                  {diff}
                </SyntaxHighlighter>
              </CardContent>
            </Card>
          )}

          {cliOutput && (
            <Card>
              <CardHeader>
                <CardTitle>CLI Output</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="whitespace-pre-wrap">{cliOutput}</pre>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Pull Requests from All Repositories</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                {repoPrs.map(repo => (
                  <div key={repo.repo_name} className="mb-4">
                    <h3 className="text-lg font-semibold mb-2">{repo.repo_name}</h3>
                    {repo.pull_requests.map(pr => (
                      <div key={pr.number} className="flex items-center mb-2">
                        <span className="mr-2">
                          PR #{pr.number}: {pr.title}
                        </span>
                        <Button
                          className="bg-primary text-primary-foreground hover:bg-primary/90"
                          onClick={() => runCliReview(pr.number)}
                        >
                          Run CLI Review
                        </Button>
                      </div>
                    ))}
                  </div>
                ))}
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}