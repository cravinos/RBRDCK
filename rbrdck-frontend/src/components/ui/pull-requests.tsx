'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { GitPullRequest } from "lucide-react"

export function PullRequests() {
  const [openPRs, setOpenPRs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPRs = async () => {
      try {
        const response = await fetch('/api/open_prs')
        const data = await response.json()
        setOpenPRs(data)
        setLoading(false)
      } catch (err) {
        setError('Failed to fetch pull requests')
        setLoading(false)
      }
    }

    fetchPRs()
  }, [])

  const runReview = async (prNumber) => {
    try {
      const response = await fetch(`/api/run_cli_review/${prNumber}`, { method: 'POST' })
      const data = await response.json()
      console.log(data.message)
      // You might want to update the UI here to show the review has been run
    } catch (err) {
      console.error('Failed to run review:', err)
    }
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div>{error}</div>

  return (
    <Card>
      <CardHeader>
        <CardTitle>Open Pull Requests</CardTitle>
        <CardDescription>Review and manage open pull requests</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {openPRs.map((pr) => (
            <div key={pr.number} className="flex items-center justify-between py-2">
              <div className="flex items-center">
                <GitPullRequest className="mr-2" />
                <span>#{pr.number} - {pr.title}</span>
              </div>
              <Button onClick={() => runReview(pr.number)}>Run Review</Button>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}