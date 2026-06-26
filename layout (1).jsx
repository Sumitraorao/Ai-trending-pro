import './globals.css'

export const metadata = {
  title: 'AI-Trader-Pro',
  description: 'Autonomous AI Trading Assistant - Paper Trading',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-trading-bg text-trading-text min-h-screen">
        {children}
      </body>
    </html>
  )
}
