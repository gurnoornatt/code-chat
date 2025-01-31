"use client"

import { useState } from "react"
import { ChevronRight, ChevronDown, FileCode, Folder, FileJson, FileType, FileText } from "lucide-react"

interface FileExplorerProps {
  onFileSelect: (path: string, content: string) => void
}

interface FileNode {
  name: string
  type: "file" | "directory"
  children?: FileNode[]
  content?: string
  path: string
}

export function FileExplorer({ onFileSelect }: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(["/"]))

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedFolders(newExpanded)
  }

  const getFileIcon = (name: string) => {
    if (name.endsWith(".ts") || name.endsWith(".tsx")) return <FileCode className="h-4 w-4 text-[#1c98e7]" />
    if (name.endsWith(".json")) return <FileJson className="h-4 w-4 text-[#fbc748]" />
    if (name.endsWith(".md")) return <FileText className="h-4 w-4 text-[#5c5c5c]" />
    if (name.endsWith(".css")) return <FileType className="h-4 w-4 text-[#0098e7]" />
    return <FileType className="h-4 w-4 text-[#5c5c5c]" />
  }

  const renderFileTree = (node: FileNode, level = 0) => {
    const isExpanded = expandedFolders.has(node.path)
    const paddingLeft = `${level * 1.5}rem`

    if (node.type === "directory") {
      return (
        <div key={node.path}>
          <button
            className="flex w-full items-center gap-2 px-2 py-0.5 hover:bg-zinc-800/50 font-[system-ui]"
            style={{ paddingLeft }}
            onClick={() => toggleFolder(node.path)}
          >
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            <Folder className="h-4 w-4 text-yellow-400" />
            <span className="text-sm">{node.name}</span>
          </button>
          {isExpanded && node.children?.map((child) => renderFileTree(child, level + 1))}
        </div>
      )
    }

    return (
      <button
        key={node.path}
        className="flex w-full items-center gap-2 px-2 py-0.5 hover:bg-zinc-800/50 font-[system-ui]"
        style={{ paddingLeft }}
        onClick={() => node.content && onFileSelect(node.path, node.content)}
      >
        {getFileIcon(node.name)}
        <span className="text-sm">{node.name}</span>
      </button>
    )
  }

  // Example file structure
  const fileStructure: FileNode = {
    name: "project",
    type: "directory",
    path: "/",
    children: [
      {
        name: "app",
        type: "directory",
        path: "/app",
        children: [
          {
            name: "page.tsx",
            type: "file",
            path: "/app/page.tsx",
            content: "export default function Page() {\n  return <div>Hello World</div>\n}",
          },
          {
            name: "layout.tsx",
            type: "file",
            path: "/app/layout.tsx",
            content: "export default function Layout({ children }) {\n  return <div>{children}</div>\n}",
          },
        ],
      },
      {
        name: "package.json",
        type: "file",
        path: "/package.json",
        content: '{\n  "name": "project",\n  "version": "1.0.0"\n}',
      },
    ],
  }

  return <div className="h-full overflow-auto bg-black p-2">{renderFileTree(fileStructure)}</div>
}

