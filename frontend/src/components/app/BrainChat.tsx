"use client";

import { useEffect, useRef, useState } from "react";
import { askBrain } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/Button";

interface BrainChatProps {
  quickPrompts?: string[];
  compact?: boolean;
  initialGreeting?: string;
}

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export function BrainChat({ quickPrompts = [], compact = false, initialGreeting }: BrainChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(
    initialGreeting
      ? [{ id: uid(), role: "assistant", content: initialGreeting, createdAt: new Date().toISOString() }]
      : []
  );
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send(question: string) {
    if (!question.trim() || streaming) return;
    const userMsg: ChatMessage = {
      id: uid(),
      role: "user",
      content: question.trim(),
      createdAt: new Date().toISOString(),
    };
    const assistantId = uid();
    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: assistantId, role: "assistant", content: "", createdAt: new Date().toISOString() },
    ]);
    setInput("");
    setStreaming(true);

    await askBrain({
      question: question.trim(),
      onToken: (token) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + token } : m))
        );
      },
      onDone: () => setStreaming(false),
    });
    setStreaming(false);
  }

  return (
    <div className="flex h-full flex-col">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-1 py-2">
        {messages.length === 0 && (
          <div className="py-6 text-center text-sm text-nexus-muted">
            Ask NEXUS BRAIN about your accounts, deals, or market signals.
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
            <div
              className={`max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-nexus-cyan/15 text-nexus-text"
                  : "nexus-card text-nexus-text"
              }`}
            >
              {m.content || (streaming ? <TypingDots /> : "")}
            </div>
          </div>
        ))}
      </div>

      {quickPrompts.length > 0 && messages.length < 2 && (
        <div className="flex flex-wrap gap-2 border-t border-nexus-border px-1 py-3">
          {quickPrompts.map((p) => (
            <button
              key={p}
              onClick={() => send(p)}
              className="focus-ring rounded-full border border-nexus-border bg-nexus-surface2 px-3 py-1.5 text-xs text-nexus-muted transition-colors hover:border-nexus-cyan/50 hover:text-nexus-cyan"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className={`flex items-center gap-2 border-t border-nexus-border pt-3 ${compact ? "px-1" : "px-1"}`}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the Business Brain..."
          className="focus-ring flex-1 rounded-md border border-nexus-border bg-nexus-surface2 px-3 py-2 text-sm text-nexus-text placeholder:text-nexus-muted"
        />
        <Button type="submit" size="sm" disabled={streaming || !input.trim()}>
          Send
        </Button>
      </form>
    </div>
  );
}

function TypingDots() {
  return (
    <span className="inline-flex gap-1">
      <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-nexus-cyan" />
      <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-nexus-cyan [animation-delay:0.2s]" />
      <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-nexus-cyan [animation-delay:0.4s]" />
    </span>
  );
}
