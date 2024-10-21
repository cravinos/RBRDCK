'use client'

import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import { docco } from 'react-syntax-highlighter/dist/cjs/styles/hljs'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { GitPullRequest, Users, AlertCircle } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface PullRequest {
  number: number
  title: string
  repo_name: string  // Added to associate PR with its repository
}

interface RepoPullRequests {
  repo_name: string
  pull_requests: PullRequest[]
}

interface Organization {
  org_name: string
  org_url: string
}

interface Repository {
  name: string
  url: string
}

export function PullRequests() {
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null)
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([])
  const [selectedPr, setSelectedPr] = useState<PullRequest | null>(null);
  const [review, setReview] = useState<string>('');
  const [diff, setDiff] = useState<string>('');
  const [cliOutput, setCliOutput] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [organizations, setOrganizations] = useState<Organization[]>([])

  // Fetch repositories and organizations on initial load
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [reposResponse, orgsResponse] = await Promise.all([
          axios.get('http://localhost:8000/repos/'),
          axios.get('http://localhost:8000/user_groups')
        ])
        setRepositories(reposResponse.data.repositories)
        setOrganizations(orgsResponse.data.organizations)
      } catch (err) {
        setError('Failed to fetch initial data: ' + (err instanceof Error ? err.message : String(err)))
      }
    }
    fetchInitialData()
  }, [])

  // Fetch pull requests when a repository is selected
  useEffect(() => {
    const fetchPullRequests = async () => {
      if (selectedRepo) {
        try {
          const response = await axios.get(`http://localhost:8000/repo_pull_requests/${selectedRepo}`)
          const prs: RepoPullRequests = response.data
          // Associate repo_name with each PR
          const enrichedPrs: PullRequest[] = prs.pull_requests.map(pr => ({
            ...pr,
            repo_name: prs.repo_name
          }))
          setPullRequests(enrichedPrs)
        } catch (err) {
          setError('Failed to fetch pull requests: ' + (err instanceof Error ? err.message : String(err)))
        }
      } else {
        setPullRequests([])
      }
    }
    fetchPullRequests()
  }, [selectedRepo])

  // Fetch review and diff when a PR is selected
  useEffect(() => {
    const fetchReviewAndDiff = async () => {
      if (selectedPr) {
        try {
          const response = await axios.get(
            `http://localhost:8000/review_pr/${selectedPr.repo_name}/${selectedPr.number}`
          );
          setReview(response.data.review);
          setDiff(response.data.diff);
        } catch (err) {
          setError('Failed to fetch review: ' + (err instanceof Error ? err.message : String(err)));
        }
      } else {
        setReview('');
        setDiff('');
      }
    };
    fetchReviewAndDiff();
  }, [selectedPr]);

  // Function to run CLI review for a specific PR
  const runCliReview = async (prNumber: number) => {
    try {
      const response = await axios.post(`http://localhost:8000/run_cli_review/${prNumber}`)
      setCliOutput(response.data.output)
    } catch (err) {
      setError('Failed to run CLI review: ' + (err instanceof Error ? err.message : String(err)))
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Pull Request Dashboard</h1>
      
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="prs">
        <TabsList>
          <TabsTrigger value="prs">Pull Requests</TabsTrigger>
          <TabsTrigger value="repos">Repositories</TabsTrigger>
          <TabsTrigger value="orgs">Organizations</TabsTrigger>
        </TabsList>

        {/* Pull Requests Tab */}
        <TabsContent value="prs">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Repository Selection */}
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>Select Repository</CardTitle>
              </CardHeader>
              <CardContent>
                <Select onValueChange={(value) => setSelectedRepo(value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a repository" />
                  </SelectTrigger>
                  <SelectContent>
                    {repositories.map(repo => (
                      <SelectItem key={repo.name} value={repo.name}>
                        {repo.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* List of Open Pull Requests */}
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>Open Pull Requests</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {pullRequests.length > 0 ? (
                    pullRequests.map(pr => (
                      <div key={pr.number} className="flex items-center mb-2">
                        <Button
                          variant="outline"
                          className="w-full justify-start"
                          onClick={() => setSelectedPr(pr)}
                        >
                          <GitPullRequest className="mr-2 h-4 w-4" />
                          PR #{pr.number}: {pr.title} <span className="text-sm text-gray-500 ml-2">({pr.repo_name})</span>
                        </Button>
                      </div>
                    ))
                  ) : (
                    <p>No open pull requests found.</p>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Review and Diff Section */}
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>{selectedPr ? `Review for PR #${selectedPr.number}` : 'Select a PR'}</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedPr ? (
                  <>
                    <p className="mb-4">{review || 'Loading review...'}</p>
                    <h3 className="text-lg font-semibold mb-2">Diff</h3>
                    <SyntaxHighlighter language="diff" style={docco}>
                      {diff || 'Loading diff...'}
                    </SyntaxHighlighter>
                    <Button className="mt-4" onClick={() => runCliReview(selectedPr.number)}>
                      Run CLI Review
                    </Button>
                  </>
                ) : (
                  <p>Select a pull request to view its review and diff.</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* CLI Output Section */}
          {cliOutput && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>CLI Output</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="whitespace-pre-wrap bg-muted p-4 rounded-md">{cliOutput}</pre>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Repositories Tab */}
        <TabsContent value="repos">
          <Card>
            <CardHeader>
              <CardTitle>Repositories</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                {repositories.length > 0 ? (
                  repositories.map(repo => (
                    <div key={repo.name} className="mb-4">
                      <h3 className="text-lg font-semibold mb-2">{repo.name}</h3>
                      <a href={repo.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
                        View on GitHub
                      </a>
                    </div>
                  ))
                ) : (
                  <p>No repositories found.</p>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Organizations Tab */}
        <TabsContent value="orgs">
          <Card>
            <CardHeader>
              <CardTitle>Organizations & Teams</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                {organizations.length > 0 ? (
                  organizations.map(org => (
                    <div key={org.org_name} className="mb-4">
                      <h3 className="text-lg font-semibold mb-2">{org.org_name}</h3>
                      <a href={org.org_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
                        Visit Organization
                      </a>
                    </div>
                  ))
                ) : (
                  <p>No organizations found.</p>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
