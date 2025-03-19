'use client';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
}

export default function ChatMessage({ message, isUser, timestamp, isLoading }: ChatMessageProps) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg p-4 ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}
      >
        <div className="text-sm max-w-[50vw] whitespace-pre-wrap break-words">
          {isLoading ? (
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
            </div>
          ) : (
            message
          )}
        </div>
        <div className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
          {timestamp}
        </div>
      </div>
    </div>
  );
}
