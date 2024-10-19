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
import { GitPullRequest, Users, AlertCircle, Folder } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

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

interface Repository {
  name: string
  url: string
}

export default function PullRequests() {
  const [prs, setPrs] = useState<PullRequest[]>([])
  const [repoPrs, setRepoPrs] = useState<RepoPullRequests[]>([])
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [selectedPr, setSelectedPr] = useState<number | null>(null)
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null)
  const [review, setReview] = useState('')
  const [diff, setDiff] = useState('')
  const [cliOutput, setCliOutput] = useState<string | null>(null)
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [prsResponse, orgsResponse, reposResponse] = await Promise.all([
          axios.get('http://localhost:8000/open_prs'),
          axios.get('http://localhost:8000/user_groups'),
          axios.get('http://localhost:8000/repos/')
        ])
        setPrs(prsResponse.data)
        setOrganizations(orgsResponse.data.organizations)
        setRepositories(reposResponse.data.repositories)
      } catch (err) {
        setError('Failed to fetch initial data: ' + (err instanceof Error ? err.message : String(err)))
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    const fetchRepoPrs = async () => {
      if (selectedRepo) {
        try {
          const response = await axios.get(`http://localhost:8000/repo_pull_requests/${selectedRepo}`)
          setRepoPrs([response.data])
        } catch (err) {
          if (axios.isAxiosError(err) && err.response?.status === 404) {
            setRepoPrs([{ repo_name: selectedRepo, pull_requests: [] }])
          } else {
            setError('Failed to fetch repository pull requests: ' + (err instanceof Error ? err.message : String(err)))
          }
        }
      } else {
        try {
          const response = await axios.get('http://localhost:8000/repo_pull_requests')
          setRepoPrs(response.data.repo_prs)
        } catch (err) {
          setError('Failed to fetch all pull requests: ' + (err instanceof Error ? err.message : String(err)))
        }
      }
    }
    fetchRepoPrs()
  }, [selectedRepo])

  useEffect(() => {
    if (selectedPr !== null) {
      const fetchReview = async () => {
        try {
          const response = await axios.get(`http://localhost:8000/review_pr/${selectedPr}`)
          setReview(response.data.review)
          setDiff(response.data.diff)
        } catch (err) {
          setError('Failed to fetch review: ' + (err instanceof Error ? err.message : String(err)))
        }
      }
      fetchReview()
    }
  }, [selectedPr])

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
        <TabsContent value="prs">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>Open Pull Requests</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {prs.map(pr => (
                    <div key={pr.number} className="flex items-center mb-2">
                      <Button
                        variant="outline"
                        className="w-full justify-start"
                        onClick={() => setSelectedPr(pr.number)}
                      >
                        <GitPullRequest className="mr-2 h-4 w-4" />
                        PR #{pr.number}: {pr.title}
                      </Button>
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>{selectedPr ? `Review for PR #${selectedPr}` : 'Select a PR'}</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedPr ? (
                  <>
                    <p className="mb-4">{review}</p>
                    <h3 className="text-lg font-semibold mb-2">Diff</h3>
                    <SyntaxHighlighter language="diff" style={docco}>
                      {diff}
                    </SyntaxHighlighter>
                    <Button className="mt-4" onClick={() => runCliReview(selectedPr)}>
                      Run CLI Review
                    </Button>
                  </>
                ) : (
                  <p>Select a pull request to view its review and diff.</p>
                )}
              </CardContent>
            </Card>
          </div>

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
        <TabsContent value="repos">
          <Card>
            <CardHeader>
              <CardTitle>Repositories</CardTitle>
            </CardHeader>
            <CardContent>
              <Select onValueChange={(value) => setSelectedRepo(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a repository" />
                </SelectTrigger>
                <SelectContent>
                  {repositories.map((repo) => (
                    <SelectItem key={repo.name} value={repo.name}>
                      {repo.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedRepo && (
                <ScrollArea className="h-[400px] mt-4">
                  {repoPrs.map((repo) => (
                    <div key={repo.repo_name} className="mb-4">
                      <h3 className="text-lg font-semibold mb-2">{repo.repo_name}</h3>
                      {repo.pull_requests.length > 0 ? (
                        repo.pull_requests.map((pr) => (
                          <div key={pr.number} className="flex items-center mb-2">
                            <span className="mr-2">
                              PR #{pr.number}: {pr.title}
                            </span>
                            <Button
                              size="sm"
                              onClick={() => runCliReview(pr.number)}
                            >
                              Run CLI Review
                            </Button>
                          </div>
                        ))
                      ) : (
                        <p>No open pull requests for this repository.</p>
                      )}
                    </div>
                  ))}
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="orgs">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>Organizations & Teams</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {organizations.map(org => (
                    <Button
                      key={org.org_name}
                      variant="outline"
                      className="w-full justify-start mb-2"
                      onClick={() => setSelectedOrg(org.org_name)}
                    >
                      <Users className="mr-2 h-4 w-4" />
                      {org.org_name}
                    </Button>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Pull Requests from All Repositories</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  {repoPrs.map(repo => (
                    <div key={repo.repo_name} className="mb-4">
                      <h3 className="text-lg font-semibold mb-2">{repo.repo_name}</h3>
                      {repo.pull_requests.length > 0 ? (
                        repo.pull_requests.map(pr => (
                          <div key={pr.number} className="flex items-center mb-2">
                            <span className="mr-2">
                              PR #{pr.number}: {pr.title}
                            </span>
                            <Button
                              size="sm"
                              onClick={() => runCliReview(pr.number)}
                            >
                              Run CLI Review
                            </Button>
                          </div>
                        ))
                      ) : (
                        <p>No open pull requests for this repository.</p>
                      )}
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}