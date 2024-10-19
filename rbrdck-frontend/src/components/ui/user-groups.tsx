'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Users } from "lucide-react"

interface UserGroup {
  org_name: string;
  org_url: string;
}

export function UserGroups() {
  const [userGroups, setUserGroups] = useState<UserGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchUserGroups = async () => {
      try {
        const response = await fetch('/api/user_groups')
        if (!response.ok) {
          throw new Error('Failed to fetch user groups')
        }
        const data = await response.json()
        setUserGroups(data.organizations)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred')
        setLoading(false)
      }
    }

    fetchUserGroups()
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <Card>
      <CardHeader>
        <CardTitle>User Groups</CardTitle>
        <CardDescription>Organizations youre a part of</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {userGroups.map((group) => (
            <div key={group.org_name} className="flex items-center py-2">
              <Users className="mr-2" />
              <a href={group.org_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                {group.org_name}
              </a>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}