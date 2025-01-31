"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

interface ResourcesProps {
  selectedFile: string | null
}

export function Resources({ selectedFile }: ResourcesProps) {
  // Example resources based on file type
  const getResources = (filename: string) => {
    if (filename.endsWith(".tsx")) {
      return [
        {
          title: "React Documentation",
          description: "Official React documentation",
          link: "https://react.dev",
        },
        {
          title: "TypeScript Handbook",
          description: "Learn TypeScript fundamentals",
          link: "https://www.typescriptlang.org/docs/",
        },
        {
          title: "Next.js Documentation",
          description: "Learn about Next.js features and API",
          link: "https://nextjs.org/docs",
        },
      ]
    }
    return []
  }

  const resources = selectedFile ? getResources(selectedFile) : []

  return (
    <ScrollArea className="h-full px-6">
      <div className="max-w-3xl mx-auto py-6 space-y-6">
        {resources.length > 0 ? (
          resources.map((resource, i) => (
            <Card key={i} className="bg-zinc-800/50 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-white">{resource.title}</CardTitle>
                <CardDescription className="text-zinc-400">{resource.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <a
                  href={resource.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline"
                >
                  Learn More →
                </a>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="text-center text-zinc-400">Select a file to see relevant resources</div>
        )}
      </div>
    </ScrollArea>
  )
}

