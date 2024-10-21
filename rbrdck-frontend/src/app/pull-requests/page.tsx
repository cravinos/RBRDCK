'use client'

import React, { useState, useEffect } from 'react'
import axios, { AxiosError } from 'axios'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import { docco } from 'react-syntax-highlighter/dist/cjs/styles/hljs'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { GitPullRequest, Users, AlertCircle } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import LoadingSpinner from "@/components/ui/LoadingSpinner" // Assume you have a loading spinner component

// Define API base URL using environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

// Type Definitions
interface PullRequest {
  number: number
  title: string
}

interface Repository {
  name: string
  url: string
}

const PullRequestsPage: React.FC = () => {
  // State Variables
  const [repos, setRepos] = useState<Repository[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null)
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  // Fetch Repositories on Component Mount
  useEffect(() => {
    const fetchRepos = async () => {
      setLoading(true)
      try {
        const response = await axios.get<{ repositories: Repository[] }>(`${API_BASE_URL}/repos/`)
        setRepos(response.data.repositories)
      } catch (err) {
        handleError(err, 'Failed to fetch repositories')
      } finally {
        setLoading(false)
      }
    }

    fetchRepos()
  }, [])

  // Fetch Pull Requests when a Repository is Selected
  useEffect(() => {
    if (!selectedRepo) {
      setPullRequests([])
      return
    }

    const fetchPullRequests = async () => {
      setLoading(true)
      try {
        const response = await axios.get<{ repositories: Repository[] }>(`${API_BASE_URL}/repos/`)
        const repo = response.data.repositories.find(r => r.name === selectedRepo)
        if (!repo) {
          setError(`Repository ${selectedRepo} not found`)
          setPullRequests([])
          return
        }

        // Fetch pull requests for the selected repository
        const prsResponse = await axios.get<PullRequest[]>(`${API_BASE_URL}/open_prs`)
        setPullRequests(prsResponse.data)
      } catch (err) {
        handleError(err, `Failed to fetch pull requests for ${selectedRepo}`)
      } finally {
        setLoading(false)
      }
    }

    fetchPullRequests()
  }, [selectedRepo])

  // Error Handling Function
  const handleError = (error: unknown, message: string) => {
    if (axios.isAxiosError(error)) {
      setError(`${message}: ${error.response?.data?.detail || error.message}`)
    } else if (error instanceof Error) {
      setError(`${message}: ${error.message}`)
    } else {
      setError(`${message}: An unknown error occurred.`)
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

      {loading && <LoadingSpinner />}

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
              {repos.map((repo) => (
                <SelectItem key={repo.name} value={repo.name}>
                  {repo.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Display Pull Requests for the Selected Repository */}
      {selectedRepo && (
        <Card>
          <CardHeader>
            <CardTitle>Open Pull Requests for {selectedRepo}</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              {pullRequests.length > 0 ? pullRequests.map(pr => (
                <div key={pr.number} className="flex items-center mb-2">
                  <GitPullRequest className="mr-2 h-4 w-4" />
                  <span className="mr-2">PR #{pr.number}: {pr.title}</span>
                  <Button
                    size="sm"
                    onClick={() => window.open(`${API_BASE_URL}/review_pr/${pr.number}`, '_blank')}
                  >
                    View Review
                  </Button>
                </div>
              )) : <p>No open pull requests available for this repository.</p>}
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default PullRequestsPage
